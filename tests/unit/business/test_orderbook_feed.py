"""OrderBookFeed 測試。"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any, Mapping, Optional

from business.orderbook.feed import OrderBookFeed
from business.orderbook.manager import OrderBookManager
from core.datatypes import OrderBook, PriceLevel
from core.interface import BaseGateway
from core.parser.base import JsonParser
from core.wrapper.base import BaseExchangeWrapper


def _orderbook(price: Decimal, sequence: int) -> OrderBook:
    return OrderBook(
        symbol="KRW-BTC",  # mapping not needed
        exchange="test",
        bids=[PriceLevel(price=price, quantity=Decimal("0.1"), timestamp=sequence)],
        asks=[PriceLevel(price=price + 1, quantity=Decimal("0.1"), timestamp=sequence)],
        sequence=sequence,
        timestamp=sequence,
    )


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


class DummyFeedWrapper(BaseExchangeWrapper):
    def __init__(self, updates: list[OrderBook]):
        super().__init__(DummyGateway(), DummyParser())
        self._updates = updates
        self._subscriptions = 0

    async def get_orderbook(self, symbol: str) -> OrderBook:
        return self._updates[0]

    async def get_balance(self):  # pragma: no cover
        raise NotImplementedError

    async def place_order(self, order):  # pragma: no cover
        raise NotImplementedError

    async def cancel_order(self, order_id: str):  # pragma: no cover
        raise NotImplementedError

    async def get_order_status(self, order_id: str):  # pragma: no cover
        raise NotImplementedError

    async def subscribe_orderbook(self, symbol: str, callback):
        self._subscriptions += 1
        for ob in self._updates[1:]:
            await callback(ob)
        await asyncio.sleep(0)


def test_feed_updates_manager() -> None:
    updates = [_orderbook(Decimal("10"), 1), _orderbook(Decimal("20"), 2)]
    wrapper = DummyFeedWrapper(updates)
    manager = OrderBookManager()
    feed = OrderBookFeed(wrapper, "KRW-BTC", manager)

    async def run() -> None:
        await feed.start()
        await asyncio.sleep(0.05)
        assert manager.snapshot.sequence == 2
        await feed.stop()

    asyncio.run(run())
