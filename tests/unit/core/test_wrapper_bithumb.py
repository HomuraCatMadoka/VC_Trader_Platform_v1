"""Bithumb Wrapper 測試。"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any, Mapping, Optional

from core.datatypes import OrderRequest
from core.interface import BaseGateway
from core.parser.bithumb import BithumbParser
from core.wrapper.bithumb import BithumbWrapper


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


def test_get_orderbook() -> None:
    responses = {
        ("GET", "/public/orderbook/BTC_KRW"): b"{\"status\":\"0000\",\"data\":{\"bids\":[{\"price\":\"1\",\"quantity\":\"0.1\"}],\"asks\":[{\"price\":\"2\",\"quantity\":\"0.2\"}]}}"
    }
    wrapper = BithumbWrapper(FakeGateway(responses), BithumbParser())
    orderbook = asyncio.run(wrapper.get_orderbook("BTC_KRW"))
    assert orderbook.exchange == "bithumb"


def test_place_order_payload() -> None:
    responses = {
        ("POST", "/trade/place"): b"{\"status\":\"0000\",\"data\":{\"order_id\":\"o1\",\"order_currency\":\"BTC_KRW\",\"status\":\"placed\",\"contract_amount\":\"0\"}}"
    }
    gateway = FakeGateway(responses)
    wrapper = BithumbWrapper(gateway, BithumbParser())
    order = OrderRequest(
        exchange="bithumb",
        symbol="BTC_KRW",
        side="bid",
        order_type="limit",
        quantity=Decimal("0.01"),
        price=Decimal("100"),
    )
    result = asyncio.run(wrapper.place_order(order))
    assert result.order_id == "o1"
    call = gateway.calls[0]
    assert call["signed"] is True
    assert call["params"]["order_currency"] == "BTC"
    assert call["params"]["payment_currency"] == "KRW"
