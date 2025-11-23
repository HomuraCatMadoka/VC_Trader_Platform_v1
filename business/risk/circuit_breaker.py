"""熔斷機制。"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int
    cool_down: float  # seconds


class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig) -> None:
        self._config = config
        self._failures = 0
        self._open_until: float = 0.0
        self._lock = asyncio.Lock()

    async def allow(self) -> bool:
        async with self._lock:
            if self._failures >= self._config.failure_threshold and time.time() < self._open_until:
                logger.debug("熔斷中")
                return False
            if time.time() >= self._open_until:
                self._failures = 0
            return True

    async def record_success(self) -> None:
        async with self._lock:
            self._failures = 0

    async def record_failure(self) -> None:
        async with self._lock:
            self._failures += 1
            if self._failures >= self._config.failure_threshold:
                self._open_until = time.time() + self._config.cool_down
                logger.warning("熔斷觸發", extra={"cool_down": self._config.cool_down})
from utils.logger import setup_logger

logger = setup_logger("circuit_breaker")
