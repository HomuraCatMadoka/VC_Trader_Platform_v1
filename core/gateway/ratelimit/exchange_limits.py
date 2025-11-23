"""各交易所限流參數設定。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ExchangeLimit:
    """單個交易所的限流配置。"""

    public_capacity: int
    public_rate: float
    private_capacity: int
    private_rate: float


DEFAULT_LIMITS: Dict[str, ExchangeLimit] = {
    "upbit": ExchangeLimit(public_capacity=10, public_rate=10, private_capacity=8, private_rate=8),
    "bithumb": ExchangeLimit(public_capacity=20, public_rate=20, private_capacity=15, private_rate=15),
}
