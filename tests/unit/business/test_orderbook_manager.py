"""OrderBook 管理模塊測試。"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any, Mapping, Optional

from business.orderbook.delta import DeltaEntry, OrderBookDelta
from business.orderbook.manager import OrderBookManager
from business.orderbook.snapshot import OrderBookSnapshot
from core.datatypes import OrderBook, PriceLevel
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


class DummyWrapper(BaseExchangeWrapper):
    async def get_orderbook(self, symbol: str) -> OrderBook:
        return OrderBook(
            symbol=symbol,
            exchange="test",
            bids=[PriceLevel(price=Decimal("2"), quantity=Decimal("1"), timestamp=1)],
            asks=[PriceLevel(price=Decimal("3"), quantity=Decimal("1"), timestamp=1)],
            sequence=1,
            timestamp=1,
        )

    async def get_balance(self):  # pragma: no cover
        raise NotImplementedError

    async def place_order(self, order):  # pragma: no cover
        raise NotImplementedError

    async def cancel_order(self, order_id: str):  # pragma: no cover
        raise NotImplementedError

    async def get_order_status(self, order_id: str):  # pragma: no cover
        raise NotImplementedError

    async def subscribe_orderbook(self, symbol: str, callback):  # pragma: no cover
        raise NotImplementedError


class DummyGateway(BaseGateway):
    async def request(self, method: str, endpoint: str, *, params=None, signed=False, headers=None) -> bytes:  # pragma: no cover
        raise NotImplementedError

    async def ws_connect(self, url: Optional[str] = None, *, headers=None):  # pragma: no cover
        raise NotImplementedError

    async def close(self) -> None:  # pragma: no cover
        return


def test_snapshot_sorting() -> None:
    ob = OrderBook(
        symbol="KRW-BTC",
        exchange="upbit",
        bids=[
            PriceLevel(price=Decimal("10"), quantity=Decimal("1"), timestamp=1),
            PriceLevel(price=Decimal("12"), quantity=Decimal("1"), timestamp=1),
        ],
        asks=[
            PriceLevel(price=Decimal("15"), quantity=Decimal("1"), timestamp=1),
            PriceLevel(price=Decimal("13"), quantity=Decimal("1"), timestamp=1),
        ],
        sequence=1,
        timestamp=1,
    )
    snapshot = OrderBookSnapshot.from_orderbook(ob)
    assert snapshot.bids[0].price == Decimal("12")
    assert snapshot.asks[0].price == Decimal("13")


def test_delta_apply_updates_and_remove() -> None:
    snapshot = OrderBookSnapshot(
        symbol="KRW-BTC",
        exchange="upbit",
        bids=[PriceLevel(price=Decimal("10"), quantity=Decimal("1"), timestamp=1)],
        asks=[PriceLevel(price=Decimal("11"), quantity=Decimal("1"), timestamp=1)],
        sequence=1,
        timestamp=1,
    )
    delta = OrderBookDelta(
        bids=[DeltaEntry(price=Decimal("10"), quantity=Decimal("0"), timestamp=2), DeltaEntry(price=Decimal("9"), quantity=Decimal("2"), timestamp=2)],
        asks=[DeltaEntry(price=Decimal("11"), quantity=Decimal("3"), timestamp=2)],
        sequence=2,
    )
    delta.apply(snapshot)
    assert len(snapshot.bids) == 1 and snapshot.bids[0].price == Decimal("9")
    assert snapshot.asks[0].quantity == Decimal("3")
    assert snapshot.sequence == 2


def test_manager_initialize_and_get_top() -> None:
    wrapper = DummyWrapper(DummyGateway(), DummyParser())
    manager = OrderBookManager()
    asyncio.run(manager.initialize(wrapper, "KRW-BTC"))
    top = asyncio.run(manager.get_top_n(1))
    assert top["bids"][0].price == Decimal("2")
