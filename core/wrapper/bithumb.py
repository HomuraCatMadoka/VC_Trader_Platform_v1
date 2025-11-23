"""Bithumb Wrapper。"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Awaitable, Callable, Mapping, Optional, Sequence

import msgspec
from aiohttp import WSMsgType

from core.datatypes import Balance, OrderBook, OrderRequest, OrderResult
from core.wrapper.base import BaseExchangeWrapper


class BithumbWrapper(BaseExchangeWrapper):
    """提供 Bithumb API 封裝。"""

    async def get_orderbook(self, symbol: str) -> OrderBook:
        raw = await self._fetch_json("GET", f"/public/orderbook/{symbol}")
        return self._parser.parse_orderbook(raw)

    async def get_balance(self) -> Sequence[Balance]:
        raw = await self._fetch_json("POST", "/info/balance", params={"currency": "ALL"}, signed=True)
        return self._parser.parse_balance(raw)

    async def place_order(self, order: OrderRequest) -> OrderResult:
        payload = {
            "order_currency": order.symbol.split("_")[0],
            "payment_currency": order.symbol.split("_")[-1],
            "units": str(order.quantity),
            "price": str(order.price or 0),
            "type": order.side,
        }
        raw = await self._fetch_json("POST", "/trade/place", params=payload, signed=True)
        return self._parser.parse_order_result(raw)

    async def cancel_order(self, order_id: str) -> OrderResult:
        raw = await self._fetch_json("POST", "/trade/cancel", params={"order_id": order_id}, signed=True)
        return self._parser.parse_order_result(raw)

    async def get_order_status(self, order_id: str) -> OrderResult:
        raw = await self._fetch_json("POST", "/info/order_detail", params={"order_id": order_id}, signed=True)
        return self._parser.parse_order_result(raw)

    async def buy_market_order(self, symbol: str, volume: Decimal) -> OrderResult:
        payload = {
            "order_currency": symbol.split("_")[0],
            "payment_currency": symbol.split("_")[-1],
            "units": str(volume),
        }
        raw = await self._fetch_json("POST", "/trade/market_buy", params=payload, signed=True)
        return self._parser.parse_order_result(raw)

    async def sell_market_order(self, symbol: str, volume: Decimal) -> OrderResult:
        payload = {
            "order_currency": symbol.split("_")[0],
            "payment_currency": symbol.split("_")[-1],
            "units": str(volume),
        }
        raw = await self._fetch_json("POST", "/trade/market_sell", params=payload, signed=True)
        return self._parser.parse_order_result(raw)

    async def subscribe_orderbook(
        self,
        symbol: str,
        callback: Callable[[OrderBook], Awaitable[None]],
    ) -> None:
        ws = await self._gateway.ws_connect()
        payload = {"type": "orderbookdepth", "symbols": [symbol], "tickTypes": ["30"]}
        await ws.send_str(msgspec.json.encode(payload).decode())
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    await self._handle_ws_payload(msg.data.encode(), callback)
                elif msg.type == WSMsgType.BINARY:
                    await self._handle_ws_payload(msg.data, callback)
                elif msg.type == WSMsgType.ERROR:
                    break
        finally:
            await ws.close()

    async def _handle_ws_payload(self, data: bytes, callback: Callable[[OrderBook], Awaitable[None]]) -> None:
        payload = msgspec.json.decode(data)
        if isinstance(payload, dict) and "content" in payload:
            # Bithumb WS 將 orderbook 放在 content 中
            normalized = msgspec.json.encode({"status": "0000", "data": payload["content"]})
        else:
            normalized = msgspec.json.encode({"status": "0000", "data": payload})
        orderbook = self._parser.parse_orderbook(normalized)
        await callback(orderbook)
