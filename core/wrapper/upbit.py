"""Upbit Wrapper。"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any, Awaitable, Callable, Mapping, Optional, Sequence

import msgspec
from aiohttp import WSMsgType

from core.datatypes import Balance, OrderBook, OrderRequest, OrderResult
from core.wrapper.base import BaseExchangeWrapper
from utils.logger import setup_logger

logger = setup_logger("upbit_wrapper")


class UpbitWrapper(BaseExchangeWrapper):
    """提供 Upbit 高階接口。"""

    async def get_orderbook(self, symbol: str) -> OrderBook:
        logger.debug("取得 Upbit 訂單簿", extra={"symbol": symbol})
        raw = await self._fetch_json("GET", "/v1/orderbook", params={"markets": symbol})
        return self._parser.parse_orderbook(raw)

    async def get_balance(self) -> Sequence[Balance]:
        logger.debug("查詢 Upbit 餘額")
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
        logger.info("Upbit 下單", extra={"symbol": order.symbol, "side": order.side, "ord_type": order.order_type})
        raw = await self._fetch_json("POST", "/v1/orders", params=payload, signed=True)
        return self._parser.parse_order_result(raw)

    async def cancel_order(self, order_id: str) -> OrderResult:
        raw = await self._fetch_json("DELETE", "/v1/order", params={"uuid": order_id}, signed=True)
        return self._parser.parse_order_result(raw)

    async def get_order_status(self, order_id: str) -> OrderResult:
        raw = await self._fetch_json("GET", "/v1/order", params={"uuid": order_id}, signed=True)
        return self._parser.parse_order_result(raw)

    async def buy_market_order(self, symbol: str, amount: Decimal) -> OrderResult:
        payload: Mapping[str, Any] = {
            "market": symbol,
            "side": "bid",
            "price": str(amount),
            "ord_type": "price",
        }
        logger.info("Upbit 市價買", extra={"symbol": symbol, "amount": str(amount)})
        raw = await self._fetch_json("POST", "/v1/orders", params=payload, signed=True)
        return self._parser.parse_order_result(raw)

    async def sell_market_order(self, symbol: str, volume: Decimal) -> OrderResult:
        payload: Mapping[str, Any] = {
            "market": symbol,
            "side": "ask",
            "volume": str(volume),
            "ord_type": "market",
        }
        logger.info("Upbit 市價賣", extra={"symbol": symbol, "volume": str(volume)})
        raw = await self._fetch_json("POST", "/v1/orders", params=payload, signed=True)
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
        normalized = self._normalize_ws_payload(payload)
        orderbook = self._parser.parse_orderbook(normalized)
        await callback(orderbook)

    async def _handle_ws_message_bytes(self, data: bytes, callback: Callable[[OrderBook], Awaitable[None]]) -> None:
        payload = msgspec.json.decode(data)
        normalized = self._normalize_ws_payload(payload)
        orderbook = self._parser.parse_orderbook(normalized)
        await callback(orderbook)

    def _normalize_ws_payload(self, payload: Any) -> bytes:
        if isinstance(payload, dict):
            if "market" not in payload and "code" in payload:
                payload = {**payload, "market": payload["code"]}
            return msgspec.json.encode([payload])
        return msgspec.json.encode(payload)
