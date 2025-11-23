"""Phase 0 API 連通性驗證腳本。"""
from __future__ import annotations

import asyncio
from typing import Any, Dict

import aiohttp


async def _assert_status(resp: aiohttp.ClientResponse, expected: int) -> Dict[str, Any]:
    if resp.status != expected:
        body = await resp.text()
        raise RuntimeError(f"Unexpected status {resp.status}: {body}")
    return await resp.json()


async def test_upbit_public(session: aiohttp.ClientSession) -> None:
    url = "https://api.upbit.com/v1/ticker"
    params = {"markets": "KRW-BTC"}
    async with session.get(url, params=params, timeout=10) as resp:
        data = await _assert_status(resp, 200)
        market = data[0]["market"]
        assert market == "KRW-BTC"
        print("✅ Upbit Public API: OK")


async def test_bithumb_public(session: aiohttp.ClientSession) -> None:
    url = "https://api.bithumb.com/public/ticker/BTC_KRW"
    async with session.get(url, timeout=10) as resp:
        data = await _assert_status(resp, 200)
        assert data["status"] == "0000"
        print("✅ Bithumb Public API: OK")


async def main() -> None:
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        await test_upbit_public(session)
        await test_bithumb_public(session)


if __name__ == "__main__":
    asyncio.run(main())
