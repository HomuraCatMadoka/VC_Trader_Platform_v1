"""Risk 模塊測試。"""
from __future__ import annotations

import asyncio
from decimal import Decimal

from business.risk.balance_checker import BalanceChecker, BalanceState
from business.risk.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from business.risk.manager import RiskConfig, RiskManager
from business.risk.position_limiter import PositionLimit, PositionLimiter
from business.strategy.signal import ArbitrageDirection, StrategySignal


def _signal(direction: ArbitrageDirection, volume: Decimal, upbit_price: Decimal, bithumb_price: Decimal) -> StrategySignal:
    return StrategySignal(
        direction=direction,
        expected_profit=Decimal("0.01"),
        volume=volume,
        upbit_price=upbit_price,
        bithumb_price=bithumb_price,
        spread=Decimal("0.02"),
    )


def test_balance_checker() -> None:
    checker = BalanceChecker(Decimal("0.1"))
    balances = BalanceState(
        upbit_btc=Decimal("1"),
        upbit_krw=Decimal("100000000"),
        bithumb_btc=Decimal("1"),
        bithumb_krw=Decimal("100000000"),
    )
    signal = _signal(ArbitrageDirection.UPBIT_SELL, Decimal("0.5"), Decimal("95000000"), Decimal("94000000"))
    assert checker.validate(signal, balances)
    bad_signal = _signal(ArbitrageDirection.UPBIT_SELL, Decimal("0.95"), Decimal("95000000"), Decimal("94000000"))
    assert checker.validate(bad_signal, balances) is False

def test_position_limiter() -> None:
    limiter = PositionLimiter(PositionLimit(max_volume=Decimal("0.5"), max_notional=Decimal("20000000")))
    sig = _signal(ArbitrageDirection.UPBIT_SELL, Decimal("0.3"), Decimal("90000000"), Decimal("89000000"))
    assert limiter.validate(sig) is False  # notional超過
    sig2 = _signal(ArbitrageDirection.UPBIT_SELL, Decimal("0.1"), Decimal("80000000"), Decimal("78000000"))
    assert limiter.validate(sig2) is True

def test_risk_manager_circuit_breaker() -> None:
    config = RiskConfig(
        reserve_ratio=Decimal("0.1"),
        position_limit=PositionLimit(max_volume=Decimal("0.5"), max_notional=Decimal("50000000")),
        circuit_breaker=CircuitBreakerConfig(failure_threshold=1, cool_down=1),
    )
    manager = RiskManager(config)
    balances = BalanceState(
        upbit_btc=Decimal("1"),
        upbit_krw=Decimal("100000000"),
        bithumb_btc=Decimal("1"),
        bithumb_krw=Decimal("100000000"),
    )
    sig = _signal(ArbitrageDirection.UPBIT_SELL, Decimal("0.1"), Decimal("90000000"), Decimal("89000000"))
    result = asyncio.run(manager.evaluate(sig, balances))
    assert result is True
    asyncio.run(manager.record_failure())
    assert asyncio.run(manager.evaluate(sig, balances)) is False
