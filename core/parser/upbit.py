"""Upbit 解析邏輯。"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Sequence

from core.datatypes import Balance, OrderBook, OrderRequest, OrderResult, PriceLevel
from core.parser.base import JsonParser


class UpbitParser(JsonParser):
    """將 Upbit JSON 轉為統一結構。"""

    def parse_orderbook(self, raw: bytes) -> OrderBook:
        data = self._decode(raw)
        payload: Dict[str, Any] = data[0]
        sequence = int(payload.get("timestamp", 0))
        bids = [
            PriceLevel(
                price=self._to_decimal(unit["bid_price"]),
                quantity=self._to_decimal(unit["bid_size"]),
                timestamp=sequence,
            )
            for unit in payload.get("orderbook_units", [])
        ]
        asks = [
            PriceLevel(
                price=self._to_decimal(unit["ask_price"]),
                quantity=self._to_decimal(unit["ask_size"]),
                timestamp=sequence,
            )
            for unit in payload.get("orderbook_units", [])
        ]
        return OrderBook(
            symbol=payload["market"],
            exchange="upbit",
            bids=bids,
            asks=asks,
            sequence=sequence,
            timestamp=sequence,
        )

    def parse_balance(self, raw: bytes) -> Sequence[Balance]:
        payload = self._decode(raw)
        balances: List[Balance] = []
        for item in payload:
            total = self._to_decimal(item.get("balance", "0")) + self._to_decimal(item.get("locked", "0"))
            balances.append(
                Balance(
                    exchange="upbit",
                    currency=item["currency"],
                    available=self._to_decimal(item.get("balance", "0")),
                    locked=self._to_decimal(item.get("locked", "0")),
                    total=total,
                )
            )
        return balances

    def parse_order_result(self, raw: bytes) -> OrderResult:
        payload = self._decode(raw)
        return OrderResult(
            order_id=payload.get("uuid", ""),
            exchange="upbit",
            symbol=payload.get("market", ""),
            status=payload.get("state", ""),
            filled_quantity=self._to_decimal(payload.get("executed_volume", "0")),
            average_price=self._optional_decimal(payload.get("avg_price")),
            raw=payload,
        )

    def _optional_decimal(self, value: Any) -> Decimal | None:
        if value in (None, "", 0):
            return None
        return self._to_decimal(value)
