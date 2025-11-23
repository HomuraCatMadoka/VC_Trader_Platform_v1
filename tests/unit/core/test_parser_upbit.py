"""Upbit Parser 測試。"""
from __future__ import annotations

from decimal import Decimal

from core.parser.upbit import UpbitParser


def test_parse_orderbook() -> None:
    raw = b"""[{\"market\":\"KRW-BTC\",\"timestamp\":1700000000000,\"orderbook_units\":[{\"ask_price\":95000000,\"bid_price\":94990000,\"ask_size\":0.5,\"bid_size\":0.3}]}]"""
    parser = UpbitParser()
    orderbook = parser.parse_orderbook(raw)
    assert orderbook.symbol == "KRW-BTC"
    assert orderbook.bids[0].price == Decimal("94990000")
    assert orderbook.asks[0].quantity == Decimal("0.5")


def test_parse_balance() -> None:
    raw = b"""[{\"currency\":\"BTC\",\"balance\":\"0.5\",\"locked\":\"0.1\"}]"""
    parser = UpbitParser()
    balances = parser.parse_balance(raw)
    assert balances[0].currency == "BTC"
    assert balances[0].available == Decimal("0.5")
    assert balances[0].total == Decimal("0.6")


def test_parse_order_result() -> None:
    raw = b"""{\"uuid\":\"abc\",\"market\":\"KRW-BTC\",\"state\":\"done\",\"executed_volume\":\"0.1\",\"avg_price\":\"95000000\"}"""
    parser = UpbitParser()
    result = parser.parse_order_result(raw)
    assert result.order_id == "abc"
    assert result.average_price == Decimal("95000000")
