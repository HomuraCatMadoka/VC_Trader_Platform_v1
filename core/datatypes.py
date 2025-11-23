"""核心數據結構定義，保證跨模塊的數據一致性。"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

__all__ = [
    "PriceLevel",
    "OrderBook",
    "Balance",
    "OrderRequest",
    "OrderResult",
]


@dataclass(slots=True)
class PriceLevel:
    """單個價位資訊。"""

    price: Decimal
    quantity: Decimal
    timestamp: int


@dataclass(slots=True)
class OrderBook:
    """標準化訂單簿結構。"""

    symbol: str
    exchange: str
    bids: List[PriceLevel] = field(default_factory=list)
    asks: List[PriceLevel] = field(default_factory=list)
    sequence: int = 0
    timestamp: int = 0


@dataclass(slots=True)
class Balance:
    """賬戶餘額資料。"""

    exchange: str
    currency: str
    available: Decimal
    locked: Decimal
    total: Decimal


@dataclass(slots=True)
class OrderRequest:
    """下單請求參數。"""

    exchange: str
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Optional[Decimal] = None


@dataclass(slots=True)
class OrderResult:
    """統一的下單結果結構。"""

    order_id: str
    exchange: str
    symbol: str
    status: str
    filled_quantity: Decimal
    average_price: Optional[Decimal]
    raw: Optional[dict] = None
