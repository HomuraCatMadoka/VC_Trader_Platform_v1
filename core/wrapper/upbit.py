"""Upbit Wrapper。"""
from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Mapping, Optional, Sequence

import msgspec
from aiohttp import WSMsgType

from core.datatypes import Balance, OrderBook, OrderRequest, OrderResult
from core.wrapper.base import BaseExchangeWrapper


class UpbitWrapper(BaseExchangeWrapper):
    """提供 Upbit 高階接口。"""

    async def get_orderbook(self, symbol: str) -> OrderBook:
        raw = await self._fetch_json("GET", "/v1/orderbook", params={"markets": symbol})
        return self._parser.parse_orderbook(raw)

    async def get_balance(self) -> Sequence[Balance]:
        raw = await self._fetch_json("GET", "/v1/accounts", signed=True)
        return self._parser.parse_balance(raw)

    async def place_order(self, order: OrderRequest) -> OrderResult:
        payload: Mapping[str, Any] = {
            "market": order.symbol,
            "side": order.side,
            "ord_type": order.order_type,
            "volume": str(order.quantity),
        }
        if order.price is not None:
            payload = {**payload, "price": str(order.price)}
        raw = await self._fetch_json("POST", "/v1/orders", params=payload, signed=True)
        return self._parser.parse_order_result(raw)

    async def cancel_order(self, order_id: str) -> OrderResult:
        raw = await self._fetch_json("DELETE", "/v1/order", params={"uuid": order_id}, signed=True)
        return self._parser.parse_order_result(raw)

    async def get_order_status(self, order_id: str) -> OrderResult:
        raw = await self._fetch_json("GET", "/v1/order", params={"uuid": order_id}, signed=True)
        return self._parser.parse_order_result(raw)

    async def subscribe_orderbook(
        self,
        symbol: str,
        callback: Callable[[OrderBook], Awaitable[None]],
    ) -> None:
        ws = await self._gateway.ws_connect()
        payload = [
            {"ticket": "k-arb"},
            {"type": "orderbook", "codes": [symbol], "isOnlyRealtime": True},
        ]
        await ws.send_str(msgspec.json.encode(payload).decode())
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    await self._handle_ws_message(msg.data, callback)
                elif msg.type == WSMsgType.BINARY:
                    await self._handle_ws_message_bytes(msg.data, callback)
                elif msg.type == WSMsgType.ERROR:
                    break
        finally:
            await ws.close()

    async def _handle_ws_message(self, data: str, callback: Callable[[OrderBook], Awaitable[None]]) -> None:
        payload = msgspec.json.decode(data.encode())
        if isinstance(payload, dict):
            normalized = msgspec.json.encode([payload])
        else:
            normalized = msgspec.json.encode(payload)
        orderbook = self._parser.parse_orderbook(normalized)
        await callback(orderbook)

    async def _handle_ws_message_bytes(self, data: bytes, callback: Callable[[OrderBook], Awaitable[None]]) -> None:
        payload = msgspec.json.decode(data)
        if isinstance(payload, dict):
            normalized = msgspec.json.encode([payload])
        else:
            normalized = msgspec.json.encode(payload)
        orderbook = self._parser.parse_orderbook(normalized)
        await callback(orderbook)
