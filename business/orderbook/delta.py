"""訂單簿增量處理。"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List, Mapping

from core.datatypes import PriceLevel
from business.orderbook.snapshot import OrderBookSnapshot


@dataclass(slots=True)
class DeltaEntry:
    price: Decimal
    quantity: Decimal
    timestamp: int

    @classmethod
    def from_mapping(cls, data: Mapping[str, object], *, price_key: str, size_key: str, timestamp: int) -> "DeltaEntry":
        return cls(price=Decimal(str(data[price_key])), quantity=Decimal(str(data[size_key])), timestamp=timestamp)


@dataclass(slots=True)
class OrderBookDelta:
    """上層解析後的增量資料。"""

    bids: List[DeltaEntry]
    asks: List[DeltaEntry]
    sequence: int

    @classmethod
    def from_ws_payload(
        cls,
        payload: Mapping[str, object],
        *,
        bid_key: str,
        ask_key: str,
        price_key: str,
        size_key: str,
        sequence_key: str,
    ) -> "OrderBookDelta":
        timestamp = int(payload.get(sequence_key, 0))
        bids = [DeltaEntry.from_mapping(row, price_key=price_key, size_key=size_key, timestamp=timestamp) for row in payload.get(bid_key, [])]
        asks = [DeltaEntry.from_mapping(row, price_key=price_key, size_key=size_key, timestamp=timestamp) for row in payload.get(ask_key, [])]
        return cls(bids=bids, asks=asks, sequence=timestamp)

    def apply(self, snapshot: OrderBookSnapshot) -> None:
        if self.sequence and self.sequence < snapshot.sequence:
            return  # 舊序列，忽略
        for entry in self.bids:
            _update_side(snapshot.bids, entry, is_bid=True)
        for entry in self.asks:
            _update_side(snapshot.asks, entry, is_bid=False)
        if self.sequence:
            snapshot.sequence = self.sequence
            snapshot.timestamp = self.sequence


def _update_side(levels: List[PriceLevel], entry: DeltaEntry, *, is_bid: bool) -> None:
    for idx, level in enumerate(levels):
        if level.price == entry.price:
            if entry.quantity == 0:
                del levels[idx]
            else:
                levels[idx] = PriceLevel(price=entry.price, quantity=entry.quantity, timestamp=entry.timestamp)
            break
    else:
        if entry.quantity == 0:
            return
        levels.append(PriceLevel(price=entry.price, quantity=entry.quantity, timestamp=entry.timestamp))
    levels.sort(key=lambda lvl: lvl.price, reverse=is_bid)
