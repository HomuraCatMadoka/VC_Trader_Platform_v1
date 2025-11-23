"""訂單執行器。"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from business.strategy.signal import StrategySignal, ArbitrageDirection
from core.datatypes import OrderResult
from core.wrapper.base import BaseExchangeWrapper
from utils.logger import setup_logger

logger = setup_logger("executor")


@dataclass(slots=True)
class ExecutionResult:
    upbit_result: OrderResult
    bithumb_result: OrderResult


class OrderExecutor:
    """負責並行執行套利指令，可選 DryRun。"""

    def __init__(self, upbit: BaseExchangeWrapper, bithumb: BaseExchangeWrapper, *, dry_run: bool = True) -> None:
        self._upbit = upbit
        self._bithumb = bithumb
        self._dry_run = dry_run

    async def execute(self, signal: StrategySignal) -> ExecutionResult:
        logger.info(
            "執行信號",
            extra={
                "direction": signal.direction,
                "volume": str(signal.volume),
                "dry_run": self._dry_run,
            },
        )
        if self._dry_run:
            return await self._simulate(signal)
        if signal.direction == ArbitrageDirection.UPBIT_SELL:
            upbit_task = self._upbit.sell_market_order("KRW-BTC", signal.volume)
            bithumb_task = self._bithumb.buy_market_order("BTC_KRW", signal.volume)
        else:
            upbit_total = signal.volume * signal.upbit_price
            upbit_task = self._upbit.buy_market_order("KRW-BTC", upbit_total)
            bithumb_task = self._bithumb.sell_market_order("BTC_KRW", signal.volume)
        results = await asyncio.gather(upbit_task, bithumb_task, return_exceptions=True)
        upbit_result, bithumb_result = self._handle_results(results)
        return ExecutionResult(upbit_result=upbit_result, bithumb_result=bithumb_result)

    async def _simulate(self, signal: StrategySignal) -> ExecutionResult:
        logger.info(
            "DryRun 訂單",
            extra={
                "direction": signal.direction,
                "volume": str(signal.volume),
                "upbit_price": str(signal.upbit_price),
                "bithumb_price": str(signal.bithumb_price),
            },
        )
        dummy = OrderResult(
            order_id="dryrun",
            exchange="dryrun",
            symbol="KRW-BTC",
            status="filled",
            filled_quantity=signal.volume,
            average_price=None,
            raw=None,
        )
        return ExecutionResult(upbit_result=dummy, bithumb_result=dummy)

    def _handle_results(self, results: list[object]) -> tuple[OrderResult, OrderResult]:
        errors = [res for res in results if isinstance(res, Exception)]
        if errors:
            raise errors[0]
        return results[0], results[1]
