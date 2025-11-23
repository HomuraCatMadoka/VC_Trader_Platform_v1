"""Bithumb HMAC-SHA512 簽名。"""
from __future__ import annotations

import base64
import hashlib
import hmac
import time
from typing import Mapping
from urllib.parse import urlencode


def sign_bithumb_request(
    endpoint: str,
    params: Mapping[str, object],
    access_key: str,
    secret_key: str,
) -> dict[str, str]:
    """生成 Bithumb 所需的簽名 Header。"""
    nonce = str(int(time.time() * 1000))
    query = urlencode(params)
    signing_str = f"{endpoint}\0{query}\0{nonce}".encode()
    digest = hmac.new(secret_key.encode(), signing_str, hashlib.sha512).hexdigest()
    signature = base64.b64encode(digest.encode()).decode()
    return {
        "Api-Key": access_key,
        "Api-Sign": signature,
        "Api-Nonce": nonce,
        "Content-Type": "application/x-www-form-urlencoded",
    }
