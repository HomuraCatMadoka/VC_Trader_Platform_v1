"""Upbit Wrapper 單元測試。"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any, Mapping, Optional

from core.datatypes import OrderRequest
from core.interface import BaseGateway
from core.parser.upbit import UpbitParser
from core.wrapper.upbit import UpbitWrapper


class FakeGateway(BaseGateway):
    def __init__(self, responses: Mapping[tuple[str, str], bytes]):
        self._responses = responses
        self.calls = []

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        signed: bool = False,
        headers: Optional[Mapping[str, str]] = None,
    ) -> bytes:
        self.calls.append({"method": method, "endpoint": endpoint, "params": params, "signed": signed})
        return self._responses[(method, endpoint)]

    async def ws_connect(self, url: Optional[str] = None, *, headers: Optional[Mapping[str, str]] = None):
        raise NotImplementedError

    async def close(self) -> None:
        return


def test_get_orderbook_calls_gateway() -> None:
    responses = {
        ("GET", "/v1/orderbook"): b"[{\"market\":\"KRW-BTC\",\"timestamp\":1,\"orderbook_units\":[{\"ask_price\":1,\"ask_size\":0.1,\"bid_price\":1,\"bid_size\":0.2}]}]"
    }
    wrapper = UpbitWrapper(FakeGateway(responses), UpbitParser())
    orderbook = asyncio.run(wrapper.get_orderbook("KRW-BTC"))
    assert orderbook.symbol == "KRW-BTC"


def test_place_order_payload() -> None:
    responses = {
        ("POST", "/v1/orders"): b"{\"uuid\":\"abc\",\"market\":\"KRW-BTC\",\"state\":\"done\",\"executed_volume\":\"0.1\"}"
    }
    gateway = FakeGateway(responses)
    wrapper = UpbitWrapper(gateway, UpbitParser())
    order = OrderRequest(
        exchange="upbit",
        symbol="KRW-BTC",
        side="bid",
        order_type="limit",
        quantity=Decimal("0.01"),
        price=Decimal("100"),
    )
    result = asyncio.run(wrapper.place_order(order))
    assert result.order_id == "abc"
    call = gateway.calls[0]
    assert call["signed"] is True
    assert call["params"]["volume"] == "0.01"
    assert call["params"]["price"] == "100"
