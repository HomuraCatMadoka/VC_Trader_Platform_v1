"""核心抽象接口定義，確保各層模塊遵循統一契約。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Awaitable, Callable, Mapping, Optional, Sequence

from core.datatypes import Balance, OrderBook, OrderRequest, OrderResult


class BaseGateway(ABC):
    """網關層抽象基類，負責網絡通信與鑑權。"""

    @abstractmethod
    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        signed: bool = False,
        headers: Optional[Mapping[str, str]] = None,
    ) -> bytes:
        """發送 HTTP 請求並返回原始二進制響應。"""

    @abstractmethod
    async def ws_connect(
        self,
        url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
    ) -> AsyncIterator[bytes]:
        """建立 WebSocket 連線並異步產出消息。"""

    @abstractmethod
    async def close(self) -> None:
        """釋放底層連線資源。"""


class BaseParser(ABC):
    """解析層抽象基類，負責將原始數據轉為標準結構。"""

    @abstractmethod
    def parse_orderbook(self, raw: bytes) -> OrderBook:
        """解析訂單簿數據。"""

    @abstractmethod
    def parse_balance(self, raw: bytes) -> Sequence[Balance]:
        """解析餘額數據。"""

    @abstractmethod
    def parse_order_result(self, raw: bytes) -> OrderResult:
        """解析下單結果。"""


class BaseWrapper(ABC):
    """封裝層抽象基類，面向業務層提供統一接口。"""

    def __init__(self, gateway: BaseGateway, parser: BaseParser) -> None:
        self._gateway = gateway
        self._parser = parser

    @abstractmethod
    async def get_orderbook(self, symbol: str) -> OrderBook:
        """獲取指定交易對的訂單簿。"""

    @abstractmethod
    async def get_balance(self) -> Sequence[Balance]:
        """獲取賬戶餘額列表。"""

    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResult:
        """提交下單請求。"""

    @abstractmethod
    async def cancel_order(self, order_id: str) -> OrderResult:
        """取消指定訂單。"""

    @abstractmethod
    async def get_order_status(self, order_id: str) -> OrderResult:
        """查詢訂單狀態。"""

    @abstractmethod
    async def subscribe_orderbook(
        self,
        symbol: str,
        callback: Callable[[OrderBook], Awaitable[None]],
    ) -> None:
        """訂閱訂單簿更新並將結果回調給上層。"""

    @abstractmethod
    async def close(self) -> None:
        """釋放底層網關資源。"""
