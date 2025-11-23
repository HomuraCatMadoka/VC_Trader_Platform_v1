"""Wrapper 層基類。"""
from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Mapping, Optional, Sequence

from core.datatypes import Balance, OrderBook, OrderRequest, OrderResult
from core.interface import BaseGateway, BaseParser, BaseWrapper


class BaseExchangeWrapper(BaseWrapper):
    """面向特定交易所的通用封裝。"""

    def __init__(self, gateway: BaseGateway, parser: BaseParser) -> None:
        super().__init__(gateway, parser)

    async def close(self) -> None:  # noqa: D401 - 文檔在父類
        await self._gateway.close()

    async def _fetch_json(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        signed: bool = False,
    ) -> bytes:
        return await self._gateway.request(
            method=method,
            endpoint=endpoint,
            params=params,
            signed=signed,
        )

    async def subscribe_orderbook(
        self,
        symbol: str,
        callback: Callable[[OrderBook], Awaitable[None]],
    ) -> None:
        raise NotImplementedError
