"""DryRun 主流程引擎。"""
from __future__ import annotations

import asyncio
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


class DryRunEngine:
    """整合 OrderBook -> Strategy -> Risk -> Executor 的 DryRun 流程。"""

    def __init__(
        self,
        *,
        upbit_wrapper: BaseExchangeWrapper,
        bithumb_wrapper: BaseExchangeWrapper,
        upbit_manager: OrderBookManager,
        bithumb_manager: OrderBookManager,
        strategy: BaseStrategy,
        risk_manager: RiskManager,
        executor: OrderExecutor,
        feeds: Optional[List[OrderBookFeed]] = None,
        poll_interval: float = 0.5,
    ) -> None:
        self._upbit_wrapper = upbit_wrapper
        self._bithumb_wrapper = bithumb_wrapper
        self._upbit_manager = upbit_manager
        self._bithumb_manager = bithumb_manager
        self._strategy = strategy
        self._risk_manager = risk_manager
        self._executor = executor
        self._feeds = feeds or []
        self._poll_interval = poll_interval
        self._stopping = asyncio.Event()

    def attach_feed(self, feed: OrderBookFeed) -> None:
        self._feeds.append(feed)

    async def start(self) -> None:
        for feed in self._feeds:
            await feed.start()
        self._stopping.clear()
        try:
            while not self._stopping.is_set():
                await self.run_once()
                await asyncio.sleep(self._poll_interval)
        finally:
            await self.stop()

    async def stop(self) -> None:
        self._stopping.set()
        for feed in self._feeds:
            await feed.stop()

    async def run_once(self) -> None:
        try:
            upbit_ob = self._orderbook_from_snapshot(self._upbit_manager.snapshot)
            bithumb_ob = self._orderbook_from_snapshot(self._bithumb_manager.snapshot)
        except RuntimeError:
            return
        signal = self._strategy.calculate(upbit_ob, bithumb_ob)
        if not signal:
            return
        balances = await self._fetch_balances()
        if not await self._risk_manager.evaluate(signal, balances):
            return
        try:
            await self._executor.execute(signal)
            await self._risk_manager.record_success()
            logger.info(
                "DryRun 交易完成",
                extra={"direction": signal.direction, "volume": str(signal.volume), "spread": str(signal.spread)},
            )
        except Exception as exc:  # pragma: no cover - 真正執行失敗時才會觸發
            await self._risk_manager.record_failure()
            logger.warning("DryRun 執行失敗", extra={"error": str(exc)})

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
        upbit_balances = await self._upbit_wrapper.get_balance()
        bithumb_balances = await self._bithumb_wrapper.get_balance()
        return BalanceState(
            upbit_btc=self._find_balance(upbit_balances, "BTC"),
            upbit_krw=self._find_balance(upbit_balances, "KRW"),
            bithumb_btc=self._find_balance(bithumb_balances, "BTC"),
            bithumb_krw=self._find_balance(bithumb_balances, "KRW"),
        )

    @staticmethod
    def _find_balance(balances: List[Balance], currency: str) -> Decimal:
        for item in balances:
            if item.currency.upper() == currency.upper():
                return item.available
        return Decimal("0")
