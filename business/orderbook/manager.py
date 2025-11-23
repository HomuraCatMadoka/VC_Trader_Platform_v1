"""訂單簿管理器。"""
from __future__ import annotations

import asyncio
from typing import Optional

from core.datatypes import OrderBook
from core.wrapper.base import BaseExchangeWrapper
from business.orderbook.delta import OrderBookDelta
from business.orderbook.snapshot import OrderBookSnapshot
from utils.logger import setup_logger

logger = setup_logger("orderbook_manager")


class OrderBookManager:
    """維護單個 Symbol 的訂單簿狀態。"""

    def __init__(self) -> None:
        self._snapshot: Optional[OrderBookSnapshot] = None
        self._lock = asyncio.Lock()

    @property
    def snapshot(self) -> OrderBookSnapshot:
        if not self._snapshot:
            raise RuntimeError("OrderBook 尚未初始化")
        return self._snapshot

    async def initialize(self, wrapper: BaseExchangeWrapper, symbol: str) -> OrderBookSnapshot:
        """透過 Wrapper 拉取快照並建立狀態。"""
        logger.info("初始化訂單簿", extra={"symbol": symbol})
        orderbook = await wrapper.get_orderbook(symbol)
        return await self.update_full(orderbook)

    async def update_full(self, orderbook: OrderBook) -> OrderBookSnapshot:
        async with self._lock:
            self._snapshot = OrderBookSnapshot.from_orderbook(orderbook)
            logger.debug(
                "更新完整訂單簿",
                extra={"symbol": orderbook.symbol, "sequence": orderbook.sequence},
            )
            return self._snapshot

    async def apply_delta(self, delta: OrderBookDelta) -> OrderBookSnapshot:
        async with self._lock:
            if not self._snapshot:
                raise RuntimeError("尚未初始化，無法套用增量")
            delta.apply(self._snapshot)
            logger.debug(
                "套用增量",
                extra={"symbol": self._snapshot.symbol, "sequence": self._snapshot.sequence},
            )
            return self._snapshot

    async def get_top_n(self, n: int = 10) -> dict[str, list]:
        async with self._lock:
            if not self._snapshot:
                raise RuntimeError("尚未初始化")
            return {
                "bids": self._snapshot.bids[:n],
                "asks": self._snapshot.asks[:n],
                "sequence": self._snapshot.sequence,
            }

    async def handle_orderbook_event(self, orderbook: OrderBook) -> OrderBookSnapshot:
        """WS 更新若已標準化為 OrderBook，可直接覆蓋。"""
        return await self.update_full(orderbook)
