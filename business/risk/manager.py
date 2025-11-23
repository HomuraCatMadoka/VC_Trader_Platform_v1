"""整體風控管理。"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from business.risk.balance_checker import BalanceChecker, BalanceState
from business.risk.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from business.risk.position_limiter import PositionLimit, PositionLimiter
from business.strategy.signal import StrategySignal
from utils.logger import setup_logger

logger = setup_logger("risk_manager")


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
            logger.info("熔斷器阻擋信號")
            return False
        if not self._position_limiter.validate(signal):
            logger.info(
                "倉位限制拒絕",
                extra={"volume": str(signal.volume), "spread": str(signal.spread)},
            )
            return False
        if not self._balance_checker.validate(signal, balances):
            logger.info("餘額不足，拒絕信號")
            return False
        logger.debug("風控通過")
        return True

    async def record_success(self) -> None:
        await self._breaker.record_success()
        logger.debug("風控記錄成功事件")

    async def record_failure(self) -> None:
        await self._breaker.record_failure()
        logger.warning("風控記錄失敗事件")
