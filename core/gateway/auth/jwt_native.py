"""Upbit JWT 生成功能。"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import uuid
from typing import Mapping, Optional
from urllib.parse import urlencode


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _build_query_hash(params: Mapping[str, object]) -> str:
    # Upbit 需要按字母排序後進行 sha512
    encoded = urlencode(sorted(params.items()), doseq=True).encode()
    return hashlib.sha512(encoded).hexdigest()


def generate_upbit_jwt(
    access_key: str,
    secret_key: str,
    params: Optional[Mapping[str, object]] = None,
) -> str:
    """生成 Upbit JWT Bearer token。"""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"access_key": access_key, "nonce": str(uuid.uuid4())}
    if params:
        payload["query_hash"] = _build_query_hash(params)
        payload["query_hash_alg"] = "SHA512"

    signing_input = f"{_b64encode(json.dumps(header, separators=(',', ':')).encode())}."
    signing_input += _b64encode(json.dumps(payload, separators=(",", ":")).encode())

    signature = hmac.new(secret_key.encode(), signing_input.encode(), hashlib.sha256).digest()
    token = f"{signing_input}.{_b64encode(signature)}"
    return f"Bearer {token}"
