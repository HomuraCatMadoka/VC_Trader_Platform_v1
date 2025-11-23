"""Bithumb Parser 測試。"""
from __future__ import annotations

from decimal import Decimal

import pytest

from core.parser.bithumb import BithumbParser


def test_parse_orderbook() -> None:
    raw = b"""{\"status\":\"0000\",\"data\":{\"timestamp\":\"1700000000\",\"order_currency\":\"BTC_KRW\",\"bids\":[{\"price\":\"94980000\",\"quantity\":\"0.4\"}],\"asks\":[{\"price\":\"95010000\",\"quantity\":\"0.2\"}]}}"""
    parser = BithumbParser()
    orderbook = parser.parse_orderbook(raw)
    assert orderbook.exchange == "bithumb"
    assert orderbook.bids[0].quantity == Decimal("0.4")


def test_parse_balance() -> None:
    raw = b"""{\"status\":\"0000\",\"data\":{\"available_btc\":\"0.5\",\"in_use_btc\":\"0.2\",\"total_btc\":\"0.8\"}}"""
    parser = BithumbParser()
    balances = parser.parse_balance(raw)
    assert balances[0].currency == "BTC"
    assert balances[0].locked == Decimal("0.2")
    assert balances[0].total == Decimal("0.8")


def test_parse_order_result() -> None:
    raw = b"""{\"status\":\"0000\",\"data\":{\"order_id\":\"123\",\"order_currency\":\"BTC_KRW\",\"status\":\"completed\",\"contract_amount\":\"0.05\",\"contract_price\":\"95000000\"}}"""
    parser = BithumbParser()
    result = parser.parse_order_result(raw)
    assert result.order_id == "123"
    assert result.filled_quantity == Decimal("0.05")
    assert result.average_price == Decimal("95000000")


def test_parse_error_status() -> None:
    raw = b"""{\"status\":\"5100\",\"data\":{}}"""
    parser = BithumbParser()
    with pytest.raises(ValueError):
        parser.parse_orderbook(raw)
