"""Upbit Gateway 實作。"""
from __future__ import annotations

from typing import Mapping, Optional

from core.exceptions import GatewayError
from core.gateway.auth.jwt_native import generate_upbit_jwt
from core.gateway.base import BaseExchangeGateway, GatewaySettings
from core.gateway.ratelimit.token_bucket import TokenBucket


class UpbitGateway(BaseExchangeGateway):
    """封裝 Upbit REST/WebSocket 請求。"""

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

    def _signed_headers(
        self,
        method: str,
        endpoint: str,
        params: Optional[Mapping[str, object]],
    ) -> Mapping[str, str]:
        if not self._settings.access_key or not self._settings.secret_key:
            raise GatewayError("Upbit 簽名請求需要 access_key/secret_key")
        token = generate_upbit_jwt(self._settings.access_key, self._settings.secret_key, params)
        return {"Authorization": token}
