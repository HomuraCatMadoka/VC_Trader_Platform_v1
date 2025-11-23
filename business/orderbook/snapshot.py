"""訂單簿快照結構。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from core.datatypes import OrderBook, PriceLevel


@dataclass(slots=True)
class OrderBookSnapshot:
    """保存排序後的訂單簿資料。"""

    symbol: str
    exchange: str
    bids: List[PriceLevel] = field(default_factory=list)
    asks: List[PriceLevel] = field(default_factory=list)
    sequence: int = 0
    timestamp: int = 0

    @classmethod
    def from_orderbook(cls, orderbook: OrderBook) -> "OrderBookSnapshot":
        """根據完整訂單簿建立快照，並確保排序。"""
        bids = sorted(orderbook.bids, key=lambda level: level.price, reverse=True)
        asks = sorted(orderbook.asks, key=lambda level: level.price)
        return cls(
            symbol=orderbook.symbol,
            exchange=orderbook.exchange,
            bids=bids,
            asks=asks,
            sequence=orderbook.sequence,
            timestamp=orderbook.timestamp,
        )
