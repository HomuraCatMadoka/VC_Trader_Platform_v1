"""DryRun 主流程引擎（支援多交易對）。"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

from business.execution.executor import OrderExecutor
from business.orderbook.feed import OrderBookFeed
from business.orderbook.manager import OrderBookManager
from business.orderbook.snapshot import OrderBookSnapshot
from business.risk.balance_checker import BalanceState
from business.risk.manager import RiskManager
from business.strategy.base import BaseStrategy
from core.datatypes import Balance, OrderBook
from core.wrapper.base import BaseExchangeWrapper
from utils.logger import setup_logger

logger = setup_logger("dryrun_engine")


@dataclass
class PairContext:
    name: str
    upbit_symbol: str
    bithumb_symbol: str
    upbit_manager: OrderBookManager
    bithumb_manager: OrderBookManager
    upbit_feed: OrderBookFeed
    bithumb_feed: OrderBookFeed


class DryRunEngine:
    def __init__(
        self,
        *,
        upbit_wrapper: BaseExchangeWrapper,
        bithumb_wrapper: BaseExchangeWrapper,
        strategy: BaseStrategy,
        risk_manager: RiskManager,
        executor: OrderExecutor,
        pairs: Optional[List[PairContext]] = None,
        poll_interval: float = 0.5,
    ) -> None:
        self._upbit_wrapper = upbit_wrapper
        self._bithumb_wrapper = bithumb_wrapper
        self._strategy = strategy
        self._risk_manager = risk_manager
        self._executor = executor
        self._pairs = pairs or []
        self._poll_interval = poll_interval
        self._stopping = asyncio.Event()

    def attach_pair(self, pair: PairContext) -> None:
        self._pairs.append(pair)

    async def start(self) -> None:
        logger.info("啟動行情 Feed", extra={"pairs": len(self._pairs), "feeds": len(self._pairs) * 2})
        for pair in self._pairs:
            await pair.upbit_feed.start()
            await pair.bithumb_feed.start()
        self._stopping.clear()
        try:
            while not self._stopping.is_set():
                await self.run_once()
                await asyncio.sleep(self._poll_interval)
        finally:
            await self.stop()

    async def stop(self) -> None:
        self._stopping.set()
        for pair in self._pairs:
            await pair.upbit_feed.stop()
            await pair.bithumb_feed.stop()

    async def run_once(self) -> None:
        if not self._pairs:
            await asyncio.sleep(self._poll_interval)
            return
        balances = await self._fetch_balances()
        for pair in self._pairs:
            try:
                upbit_ob = self._orderbook_from_snapshot(pair.upbit_manager.snapshot)
                bithumb_ob = self._orderbook_from_snapshot(pair.bithumb_manager.snapshot)
            except RuntimeError:
                logger.debug("尚未取得訂單簿快照，等待下一輪", extra={"pair": pair.name})
                continue
            signal = self._strategy.calculate(upbit_ob, bithumb_ob)
            if not signal:
                logger.debug("策略無有效信號", extra={"pair": pair.name})
                continue
            logger.debug(
                "策略輸出信號",
                extra={"pair": pair.name, "direction": signal.direction, "spread": str(signal.spread)},
            )
            if not await self._risk_manager.evaluate(signal, balances):
                logger.info(
                    "風控拒絕信號",
                    extra={
                        "pair": pair.name,
                        "direction": signal.direction,
                        "volume": str(signal.volume),
                        "spread": str(signal.spread),
                    },
                )
                continue
            try:
                await self._executor.execute(signal)
                await self._risk_manager.record_success()
                logger.info(
                    "DryRun 交易完成",
                    extra={
                        "pair": pair.name,
                        "direction": signal.direction,
                        "volume": str(signal.volume),
                        "spread": str(signal.spread),
                    },
                )
            except Exception as exc:  # pragma: no cover
                await self._risk_manager.record_failure()
                logger.warning(
                    "DryRun 執行失敗",
                    extra={"pair": pair.name, "error": str(exc)},
                )

    def _orderbook_from_snapshot(self, snapshot: OrderBookSnapshot) -> OrderBook:
        return OrderBook(
            symbol=snapshot.symbol,
            exchange=snapshot.exchange,
            bids=list(snapshot.bids),
            asks=list(snapshot.asks),
            sequence=snapshot.sequence,
            timestamp=snapshot.timestamp,
        )

    async def _fetch_balances(self) -> BalanceState:
        # 假設所有 pair 共用同一帳戶，取第一個 pair 的 wrapper 作查詢
        upbit_balances = await self._upbit_wrapper.get_balance()
        bithumb_balances = await self._bithumb_wrapper.get_balance()
        state = BalanceState(
            upbit_btc=self._find_balance(upbit_balances, "BTC"),
            upbit_krw=self._find_balance(upbit_balances, "KRW"),
            bithumb_btc=self._find_balance(bithumb_balances, "BTC"),
            bithumb_krw=self._find_balance(bithumb_balances, "KRW"),
        )
        logger.debug(
            "帳戶餘額",
            extra={
                "upbit_btc": str(state.upbit_btc),
                "upbit_krw": str(state.upbit_krw),
                "bithumb_btc": str(state.bithumb_btc),
                "bithumb_krw": str(state.bithumb_krw),
            },
        )
        return state

    @staticmethod
    def _find_balance(balances: List[Balance], currency: str) -> Decimal:
        for item in balances:
            if item.currency.upper() == currency.upper():
                return item.available
        return Decimal("0")
