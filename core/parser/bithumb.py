"""Bithumb 解析邏輯。"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Sequence

from core.datatypes import Balance, OrderBook, OrderResult, PriceLevel
from core.parser.base import JsonParser


class BithumbParser(JsonParser):
    """解析 Bithumb JSON。"""

    def _assert_success(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if payload.get("status") != "0000":
            raise ValueError(f"Bithumb API error: {payload.get('status')}")
        return payload["data"]

    def parse_orderbook(self, raw: bytes) -> OrderBook:
        payload = self._decode(raw)
        data = self._assert_success(payload)
        timestamp = int(data.get("timestamp", 0))
        bids = [
            PriceLevel(
                price=self._to_decimal(level["price"]),
                quantity=self._to_decimal(level["quantity"]),
                timestamp=timestamp,
            )
            for level in data.get("bids", [])
        ]
        asks = [
            PriceLevel(
                price=self._to_decimal(level["price"]),
                quantity=self._to_decimal(level["quantity"]),
                timestamp=timestamp,
            )
            for level in data.get("asks", [])
        ]
        return OrderBook(
            symbol=data.get("order_currency", ""),
            exchange="bithumb",
            bids=bids,
            asks=asks,
            sequence=timestamp,
            timestamp=timestamp,
        )

    def parse_balance(self, raw: bytes) -> Sequence[Balance]:
        payload = self._decode(raw)
        data = self._assert_success(payload)
        balances: List[Balance] = []
        for key, value in data.items():
            if not key.startswith("available_"):
                continue
            currency = key.replace("available_", "").upper()
            available = self._to_decimal(value)
            locked = self._to_decimal(data.get(f"in_use_{currency.lower()}", "0"))
            total_key = f"total_{currency.lower()}"
            total = self._to_decimal(data.get(total_key, available + locked))
            balances.append(
                Balance(
                    exchange="bithumb",
                    currency=currency,
                    available=available,
                    locked=locked,
                    total=total,
                )
            )
        return balances

    def parse_order_result(self, raw: bytes) -> OrderResult:
        payload = self._decode(raw)
        data = self._assert_success(payload)
        return OrderResult(
            order_id=str(data.get("order_id", "")),
            exchange="bithumb",
            symbol=data.get("order_currency", ""),
            status=data.get("status", ""),
            filled_quantity=self._to_decimal(data.get("contract_amount", "0")),
            average_price=self._optional_decimal(data.get("contract_price")),
            raw=data,
        )

    def _optional_decimal(self, value: Any) -> Decimal | None:
        if value in (None, "", 0):
            return None
        return self._to_decimal(value)
