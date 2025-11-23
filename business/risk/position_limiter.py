"""倉位限制。"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from business.strategy.signal import StrategySignal
from utils.logger import setup_logger

logger = setup_logger("position_limiter")


@dataclass
class PositionLimit:
    max_volume: Decimal
    max_notional: Decimal


class PositionLimiter:
    def __init__(self, limit: PositionLimit) -> None:
        self._limit = limit

    def validate(self, signal: StrategySignal) -> bool:
        if signal.volume > self._limit.max_volume:
            logger.debug("超出最大手數", extra={"volume": str(signal.volume)})
            return False
        notional = max(signal.upbit_price, signal.bithumb_price) * signal.volume
        if notional > self._limit.max_notional:
            logger.debug("超出名義金額", extra={"notional": str(notional)})
            return False
        return True
