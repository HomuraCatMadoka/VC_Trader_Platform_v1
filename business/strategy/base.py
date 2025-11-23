"""策略基礎定義。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from core.datatypes import OrderBook
from business.strategy.signal import StrategySignal


@dataclass(slots=True)
class StrategyConfig:
    min_profit_rate: Decimal
    max_volume: Decimal
    upbit_fee: Decimal
    bithumb_fee: Decimal

    @property
    def total_fee(self) -> Decimal:
        return self.upbit_fee + self.bithumb_fee


class BaseStrategy(ABC):
    def __init__(self, config: StrategyConfig) -> None:
        self._config = config

    @abstractmethod
    def calculate(self, upbit_ob: OrderBook, bithumb_ob: OrderBook) -> Optional[StrategySignal]:
        """根據雙方訂單簿計算套利信號。"""
