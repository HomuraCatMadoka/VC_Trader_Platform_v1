"""倉位限制。"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from business.strategy.signal import StrategySignal


@dataclass
class PositionLimit:
    max_volume: Decimal
    max_notional: Decimal


class PositionLimiter:
    def __init__(self, limit: PositionLimit) -> None:
        self._limit = limit

    def validate(self, signal: StrategySignal) -> bool:
        if signal.volume > self._limit.max_volume:
            return False
        notional = max(signal.upbit_price, signal.bithumb_price) * signal.volume
        return notional <= self._limit.max_notional
