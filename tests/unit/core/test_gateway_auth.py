"""Gateway 鑑權模塊測試。"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import uuid
from unittest import mock
from urllib.parse import urlencode

from core.gateway.auth.hmac_signer import sign_bithumb_request
from core.gateway.auth.jwt_native import generate_upbit_jwt


def _decode_payload(token: str) -> dict[str, object]:
    _, jwt_token = token.split(" ", 1)
    _header, payload, _signature = jwt_token.split(".")
    padding = "=" * (-len(payload) % 4)
    data = base64.urlsafe_b64decode(payload + padding)
    return json.loads(data)


@mock.patch("core.gateway.auth.jwt_native.uuid.uuid4", return_value=uuid.UUID(int=0))
def test_generate_upbit_jwt_includes_query_hash(_: mock.MagicMock) -> None:
    params = {"market": "KRW-BTC", "state": "done"}
    token = generate_upbit_jwt("test-access", "secret", params)
    payload = _decode_payload(token)
    assert payload["access_key"] == "test-access"
    assert payload["query_hash_alg"] == "SHA512"
    expected_hash = hashlib.sha512("market=KRW-BTC&state=done".encode()).hexdigest()
    assert payload["query_hash"] == expected_hash


@mock.patch("time.time", return_value=1700000000)
def test_sign_bithumb_request(_: mock.MagicMock) -> None:
    endpoint = "/info/account"
    headers = sign_bithumb_request(
        endpoint=endpoint,
        params={"currency": "BTC", "endpoint": endpoint},
        access_key="key",
        secret_key="secret",
    )
    assert headers["Api-Key"] == "key"
    assert headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert headers["Api-Nonce"] == str(1700000000000)
    payload = urlencode({"currency": "BTC", "endpoint": endpoint})
    signing_str = f"{endpoint}\0{payload}\0{headers['Api-Nonce']}".encode()
    expected_hash = hmac.new(b"secret", signing_str, hashlib.sha512).hexdigest()
    expected = base64.b64encode(expected_hash.encode()).decode()
    assert headers["Api-Sign"] == expected
