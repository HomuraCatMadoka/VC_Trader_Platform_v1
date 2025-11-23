"""訂單簿訂閱與管理協調器。"""
from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Optional

from core.datatypes import OrderBook
from core.wrapper.base import BaseExchangeWrapper
from business.orderbook.manager import OrderBookManager
from utils.logger import setup_logger

logger = setup_logger("orderbook_feed")


class OrderBookFeed:
    """維護單一交易對的行情訂閱與 OrderBookManager。"""

    def __init__(self, wrapper: BaseExchangeWrapper, symbol: str, manager: OrderBookManager) -> None:
        self._wrapper = wrapper
        self._symbol = symbol
        self._manager = manager
        self._task: Optional[asyncio.Task[None]] = None
        self._stopping = asyncio.Event()

    async def start(self) -> None:
        """初始化快照並啟動訂閱。"""
        await self._manager.initialize(self._wrapper, self._symbol)
        self._stopping.clear()
        self._task = asyncio.create_task(self._run(), name=f"orderbook-feed-{self._symbol}")

    async def stop(self) -> None:
        self._stopping.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        while not self._stopping.is_set():
            try:
                await self._wrapper.subscribe_orderbook(self._symbol, self._on_update)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # pragma: no cover - 需實際連線才會觸發
                logger.warning("訂閱失敗，5 秒後重試", extra={"symbol": self._symbol, "error": str(exc)})
                await asyncio.sleep(5)

    async def _on_update(self, orderbook: OrderBook) -> None:
        await self._manager.handle_orderbook_event(orderbook)
