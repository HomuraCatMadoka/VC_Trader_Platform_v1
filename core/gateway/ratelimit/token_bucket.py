"""令牌桶限流實現。"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    """限流配置。"""

    capacity: int
    refill_rate: float  # tokens per second


class TokenBucket:
    """簡易令牌桶，支援異步等待。"""

    def __init__(self, capacity: int, refill_rate: float) -> None:
        if capacity <= 0 or refill_rate <= 0:
            raise ValueError("capacity/refill_rate 必須為正數")
        self._config = RateLimitConfig(capacity=capacity, refill_rate=refill_rate)
        self._tokens = float(capacity)
        self._lock = asyncio.Lock()
        self._last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._last_refill = now
        refill_amount = elapsed * self._config.refill_rate
        if refill_amount > 0:
            self._tokens = min(self._config.capacity, self._tokens + refill_amount)

    async def acquire(self, tokens: float = 1.0) -> None:
        if tokens <= 0:
            return
        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                deficit = tokens - self._tokens
                wait_time = deficit / self._config.refill_rate
            await asyncio.sleep(max(wait_time, 0.001))
