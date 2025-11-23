"""策略信號資料結構。"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class ArbitrageDirection(str, Enum):
    UPBIT_SELL = "upbit_sell"
    BITHUMB_SELL = "bithumb_sell"


@dataclass(slots=True)
class StrategySignal:
    """套利策略輸出的統一信號。"""

    direction: ArbitrageDirection
    expected_profit: Decimal
    volume: Decimal
    upbit_price: Decimal
    bithumb_price: Decimal
    spread: Decimal
