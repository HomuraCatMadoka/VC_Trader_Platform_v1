"""Gateway 層通用基類與設定。"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Mapping, Optional
from urllib.parse import urljoin

import aiohttp

from core.exceptions import GatewayError
from core.gateway.ratelimit.token_bucket import TokenBucket
from core.interface import BaseGateway
from utils.logger import setup_logger

logger = setup_logger("gateway")


@dataclass(slots=True)
class GatewaySettings:
    """單個交易所的連線設定。"""

    name: str
    rest_base: str
    websocket_url: str
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    request_timeout: float = 10.0


class BaseExchangeGateway(BaseGateway):
    """封裝 aiohttp 的通用 Gateway。"""

    def __init__(
        self,
        settings: GatewaySettings,
        *,
        public_limiter: Optional[TokenBucket] = None,
        private_limiter: Optional[TokenBucket] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self._settings = settings
        self._session = session
        self._session_lock = asyncio.Lock()
        self._public_limiter = public_limiter
        self._private_limiter = private_limiter

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session and not self._session.closed:
            return self._session
        async with self._session_lock:
            if self._session and not self._session.closed:
                return self._session
            timeout = aiohttp.ClientTimeout(total=self._settings.request_timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
            return self._session

    def _build_url(self, endpoint: str) -> str:
        if endpoint.startswith("http"):
            return endpoint
        return urljoin(self._settings.rest_base.rstrip("/" ) + "/", endpoint.lstrip("/"))

    def _default_headers(self) -> dict[str, str]:
        return {"User-Agent": "K-Arb/0.1"}

    def _choose_limiter(self, signed: bool) -> Optional[TokenBucket]:
        return self._private_limiter if signed else self._public_limiter

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        signed: bool = False,
        headers: Optional[Mapping[str, str]] = None,
    ) -> bytes:
        session = await self._ensure_session()
        limiter = self._choose_limiter(signed)
        if limiter:
            await limiter.acquire()

        url = self._build_url(endpoint)
        req_headers = self._default_headers()
        if headers:
            req_headers.update(headers)
        if signed:
            req_headers.update(self._signed_headers(method, endpoint, params))

        request_kwargs = self._prepare_request_kwargs(method, params)
        logger.debug(
            "發送 API 請求",
            extra={
                "exchange": self._settings.name,
                "method": method,
                "endpoint": endpoint,
                "signed": signed,
            },
        )
        try:
            async with session.request(method.upper(), url, headers=req_headers, **request_kwargs) as resp:
                body = await resp.read()
                if resp.status >= 400:
                    raise GatewayError(
                        f"{self._settings.name} API {resp.status}: {body.decode(errors='ignore')}"
                    )
                logger.debug(
                    "API 請求成功",
                    extra={
                        "exchange": self._settings.name,
                        "method": method,
                        "endpoint": endpoint,
                        "status": resp.status,
                    },
                )
                return body
        except aiohttp.ClientError as exc:
            logger.warning(
                "API 請求失敗",
                extra={
                    "exchange": self._settings.name,
                    "method": method,
                    "endpoint": endpoint,
                    "error": str(exc),
                },
            )
            raise GatewayError(f"{self._settings.name} request failed: {exc}") from exc

    def _prepare_request_kwargs(
        self,
        method: str,
        params: Optional[Mapping[str, Any]],
    ) -> dict[str, Any]:
        if method.upper() in {"GET", "DELETE"}:
            return {"params": params}
        return {"json": params}

    def _signed_headers(
        self,
        method: str,
        endpoint: str,
        params: Optional[Mapping[str, Any]],
    ) -> Mapping[str, str]:
        raise NotImplementedError

    async def ws_connect(
        self,
        url: Optional[str] = None,
        *,
        headers: Optional[Mapping[str, str]] = None,
    ) -> aiohttp.ClientWebSocketResponse:
        session = await self._ensure_session()
        ws_url = url or self._settings.websocket_url
        req_headers = self._default_headers()
        if headers:
            req_headers.update(headers)
        try:
            return await session.ws_connect(ws_url, headers=req_headers, heartbeat=30)
        except aiohttp.ClientError as exc:
            raise GatewayError(f"{self._settings.name} ws_connect failed: {exc}") from exc

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
