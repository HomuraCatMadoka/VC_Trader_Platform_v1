"""OrderExecutor 測試。"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any, Mapping, Optional


from business.execution.executor import OrderExecutor
from business.strategy.signal import ArbitrageDirection, StrategySignal
from core.datatypes import OrderRequest, OrderResult
from core.interface import BaseGateway
from core.parser.base import JsonParser
from core.wrapper.base import BaseExchangeWrapper


class DummyParser(JsonParser):
    def parse_orderbook(self, raw: bytes):  # pragma: no cover
        raise NotImplementedError

    def parse_balance(self, raw: bytes):  # pragma: no cover
        raise NotImplementedError

    def parse_order_result(self, raw: bytes):  # pragma: no cover
        raise NotImplementedError


class DummyGateway(BaseGateway):
    async def request(self, method: str, endpoint: str, *, params=None, signed=False, headers=None) -> bytes:  # pragma: no cover
        raise NotImplementedError

    async def ws_connect(self, url: Optional[str] = None, *, headers=None):  # pragma: no cover
        raise NotImplementedError

    async def close(self) -> None:  # pragma: no cover
        return


class DummyWrapper(BaseExchangeWrapper):
    def __init__(self, name: str):
        super().__init__(DummyGateway(), DummyParser())
        self.name = name
        self.last_action: Optional[str] = None

    async def get_orderbook(self, symbol: str):  # pragma: no cover
        raise NotImplementedError

    async def get_balance(self):  # pragma: no cover
        raise NotImplementedError

    async def place_order(self, order: OrderRequest) -> OrderResult:  # pragma: no cover
        return OrderResult(
            order_id="test",
            exchange="test",
            symbol=order.symbol,
            status="filled",
            filled_quantity=order.quantity,
            average_price=None,
            raw=None,
        )

    async def cancel_order(self, order_id: str):  # pragma: no cover
        raise NotImplementedError

    async def get_order_status(self, order_id: str):  # pragma: no cover
        raise NotImplementedError

    async def subscribe_orderbook(self, symbol: str, callback):  # pragma: no cover
        raise NotImplementedError

    async def buy_market_order(self, symbol: str, amount: Decimal) -> OrderResult:
        self.last_action = f"{self.name}-buy:{amount}"
        return OrderResult(
            order_id="test",
            exchange=self.name,
            symbol=symbol,
            status="filled",
            filled_quantity=Decimal("0"),
            average_price=None,
            raw=None,
        )

    async def sell_market_order(self, symbol: str, volume: Decimal) -> OrderResult:
        self.last_action = f"{self.name}-sell:{volume}"
        return OrderResult(
            order_id="test",
            exchange=self.name,
            symbol=symbol,
            status="filled",
            filled_quantity=volume,
            average_price=None,
            raw=None,
        )


def test_executor_dryrun() -> None:
    upbit = DummyWrapper("upbit")
    bithumb = DummyWrapper("bithumb")
    executor = OrderExecutor(upbit, bithumb, dry_run=True)
    signal = StrategySignal(
        direction=ArbitrageDirection.UPBIT_SELL,
        expected_profit=Decimal("0.01"),
        volume=Decimal("0.05"),
        upbit_price=Decimal("95000000"),
        bithumb_price=Decimal("94500000"),
        spread=Decimal("0.02"),
    )
    result = asyncio.run(executor.execute(signal))
    assert result.upbit_result.order_id == "dryrun"


def test_executor_place_orders() -> None:
    upbit = DummyWrapper("upbit")
    bithumb = DummyWrapper("bithumb")
    executor = OrderExecutor(upbit, bithumb, dry_run=False)
    signal = StrategySignal(
        direction=ArbitrageDirection.UPBIT_SELL,
        expected_profit=Decimal("0.01"),
        volume=Decimal("0.05"),
        upbit_price=Decimal("95000000"),
        bithumb_price=Decimal("94500000"),
        spread=Decimal("0.02"),
    )
    result = asyncio.run(executor.execute(signal))
    assert result.upbit_result.order_id == "test"
    assert upbit.last_action.startswith("upbit-sell")
    assert bithumb.last_action.startswith("bithumb-buy")
