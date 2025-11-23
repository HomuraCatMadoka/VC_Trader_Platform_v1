"""Bithumb Gateway 實作。"""
from __future__ import annotations

from typing import Mapping, Optional
from urllib.parse import urlencode

from core.exceptions import GatewayError
from core.gateway.auth.hmac_signer import sign_bithumb_request
from core.gateway.base import BaseExchangeGateway, GatewaySettings
from core.gateway.ratelimit.token_bucket import TokenBucket


class BithumbGateway(BaseExchangeGateway):
    """封裝 Bithumb REST/WebSocket 請求。"""

    def __init__(
        self,
        settings: GatewaySettings,
        *,
        public_limiter: Optional[TokenBucket] = None,
        private_limiter: Optional[TokenBucket] = None,
    ) -> None:
        super().__init__(
            settings,
            public_limiter=public_limiter,
            private_limiter=private_limiter,
        )

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Mapping[str, object]] = None,
        signed: bool = False,
        headers: Optional[Mapping[str, str]] = None,
    ) -> bytes:
        normalized = dict(params or {})
        if signed and method.upper() != "GET":
            normalized.setdefault("endpoint", endpoint)
        return await super().request(
            method,
            endpoint,
            params=normalized,
            signed=signed,
            headers=headers,
        )

    def _prepare_request_kwargs(
        self,
        method: str,
        params: Optional[Mapping[str, object]],
    ) -> dict[str, object]:
        if method.upper() == "GET":
            return {"params": params}
        encoded = urlencode(params or {})
        return {"data": encoded}

    def _signed_headers(
        self,
        method: str,
        endpoint: str,
        params: Optional[Mapping[str, object]],
    ) -> Mapping[str, str]:
        if not self._settings.access_key or not self._settings.secret_key:
            raise GatewayError("Bithumb 簽名請求需要 access_key/secret_key")
        return sign_bithumb_request(
            endpoint=endpoint,
            params=params or {},
            access_key=self._settings.access_key,
            secret_key=self._settings.secret_key,
        )
