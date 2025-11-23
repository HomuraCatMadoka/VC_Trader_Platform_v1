"""整體風控管理。"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from business.risk.balance_checker import BalanceChecker, BalanceState
from business.risk.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from business.risk.position_limiter import PositionLimit, PositionLimiter
from business.strategy.signal import StrategySignal


@dataclass
class RiskConfig:
    reserve_ratio: Decimal
    position_limit: PositionLimit
    circuit_breaker: CircuitBreakerConfig


class RiskManager:
    def __init__(self, config: RiskConfig) -> None:
        self._balance_checker = BalanceChecker(config.reserve_ratio)
        self._position_limiter = PositionLimiter(config.position_limit)
        self._breaker = CircuitBreaker(config.circuit_breaker)

    async def evaluate(self, signal: StrategySignal, balances: BalanceState) -> bool:
        if not await self._breaker.allow():
            return False
        if not self._position_limiter.validate(signal):
            return False
        if not self._balance_checker.validate(signal, balances):
            return False
        return True

    async def record_success(self) -> None:
        await self._breaker.record_success()

    async def record_failure(self) -> None:
        await self._breaker.record_failure()
