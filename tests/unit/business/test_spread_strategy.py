"""SpreadArbitrageStrategy 測試。"""
from __future__ import annotations

from decimal import Decimal

from business.strategy.base import StrategyConfig
from business.strategy.signal import ArbitrageDirection
from business.strategy.spread_arbitrage import SpreadArbitrageStrategy
from core.datatypes import OrderBook, PriceLevel


def _orderbook(bid_price: Decimal, bid_qty: Decimal, ask_price: Decimal, ask_qty: Decimal, exchange: str, symbol: str) -> OrderBook:
    return OrderBook(
        symbol=symbol,
        exchange=exchange,
        bids=[PriceLevel(price=bid_price, quantity=bid_qty, timestamp=0)],
        asks=[PriceLevel(price=ask_price, quantity=ask_qty, timestamp=0)],
        sequence=0,
        timestamp=0,
    )


def test_strategy_detects_upbit_sell_signal() -> None:
    config = StrategyConfig(
        min_profit_rate=Decimal("0.005"),
        max_volume=Decimal("0.1"),
        upbit_fee=Decimal("0.001"),
        bithumb_fee=Decimal("0.0025"),
    )
    strategy = SpreadArbitrageStrategy(config)
    upbit = _orderbook(Decimal("95000000"), Decimal("0.2"), Decimal("95100000"), Decimal("0.2"), "upbit", "KRW-BTC")
    bithumb = _orderbook(Decimal("90000000"), Decimal("0.2"), Decimal("89500000"), Decimal("0.2"), "bithumb", "BTC_KRW")
    signal = strategy.calculate(upbit, bithumb)
    assert signal is not None
    assert signal.direction == ArbitrageDirection.UPBIT_SELL
    assert signal.volume == Decimal("0.1")


def test_strategy_returns_none_when_spread_low() -> None:
    config = StrategyConfig(
        min_profit_rate=Decimal("0.01"),
        max_volume=Decimal("1"),
        upbit_fee=Decimal("0.001"),
        bithumb_fee=Decimal("0.002"),
    )
    strategy = SpreadArbitrageStrategy(config)
    upbit = _orderbook(Decimal("95000000"), Decimal("0.1"), Decimal("95100000"), Decimal("0.1"), "upbit", "KRW-BTC")
    bithumb = _orderbook(Decimal("94980000"), Decimal("0.1"), Decimal("94880000"), Decimal("0.1"), "bithumb", "BTC_KRW")
    signal = strategy.calculate(upbit, bithumb)
    assert signal is None
