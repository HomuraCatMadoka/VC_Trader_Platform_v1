"""項目入口，暫用於驗證 Phase 0 骨架。"""
from __future__ import annotations

import asyncio

from utils.config import get_config
from utils.logger import setup_logger


async def main() -> None:
    """暫時輸出啟動訊息以便 Phase 0 驗收。"""
    logger = setup_logger()
    config = get_config()
    logger.info("Hello K-Arb!", extra={"config_profile": config.get("profile", "development")})


if __name__ == "__main__":
    asyncio.run(main())
