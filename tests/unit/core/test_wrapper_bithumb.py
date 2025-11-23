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


def test_market_order_helpers() -> None:
    responses = {
        ("POST", "/trade/market_sell"): b"{\"status\":\"0000\",\"data\":{\"order_id\":\"s1\",\"contract_amount\":\"0.1\"}}",
        ("POST", "/trade/market_buy"): b"{\"status\":\"0000\",\"data\":{\"order_id\":\"b1\",\"contract_amount\":\"0.1\"}}",
    }
    gateway = FakeGateway(responses)
    wrapper = BithumbWrapper(gateway, BithumbParser())
    asyncio.run(wrapper.sell_market_order("BTC_KRW", Decimal("0.05")))
    asyncio.run(wrapper.buy_market_order("BTC_KRW", Decimal("0.03")))
    assert gateway.calls[0]["endpoint"] == "/trade/market_sell"
    assert gateway.calls[1]["endpoint"] == "/trade/market_buy"
