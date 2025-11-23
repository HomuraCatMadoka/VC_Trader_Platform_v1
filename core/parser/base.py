"""Parser 層基類與通用工具。"""
from __future__ import annotations

from abc import ABC
from decimal import Decimal
from typing import Any

import msgspec

from core.interface import BaseParser


class JsonParser(BaseParser, ABC):
    """基於 msgspec 的 JSON Parser。"""

    @staticmethod
    def _decode(raw: bytes) -> Any:
        return msgspec.json.decode(raw)

    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        return Decimal(value)
