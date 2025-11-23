"""啟動 DryRun 引擎（需本地配置與 API Key）。"""
from __future__ import annotations

import asyncio
from decimal import Decimal

from business.engine.dryrun import DryRunEngine
from business.execution.executor import OrderExecutor
from business.orderbook.feed import OrderBookFeed
from business.orderbook.manager import OrderBookManager
from business.risk.manager import RiskConfig, RiskManager
from business.risk.position_limiter import PositionLimit
from business.risk.circuit_breaker import CircuitBreakerConfig
from business.strategy.base import StrategyConfig
from business.strategy.spread_arbitrage import SpreadArbitrageStrategy
from business.strategy.signal import ArbitrageDirection
from core.gateway.base import GatewaySettings
from core.gateway.ratelimit.token_bucket import TokenBucket
from core.gateway.ratelimit.exchange_limits import DEFAULT_LIMITS
from core.gateway.upbit import UpbitGateway
from core.gateway.bithumb import BithumbGateway
from core.parser.upbit import UpbitParser
from core.parser.bithumb import BithumbParser
from core.wrapper.upbit import UpbitWrapper
from core.wrapper.bithumb import BithumbWrapper
from utils.config import get_config


async def main() -> None:
    config = get_config()
    exchanges = config["exchanges"]

    upbit_settings = GatewaySettings(
        name="upbit",
        rest_base=exchanges["upbit"]["rest_base"],
        websocket_url=exchanges["upbit"]["websocket_url"],
        access_key=exchanges["upbit"].get("access_key"),
        secret_key=exchanges["upbit"].get("secret_key"),
    )
    bithumb_settings = GatewaySettings(
        name="bithumb",
        rest_base=exchanges["bithumb"]["rest_base"],
        websocket_url=exchanges["bithumb"]["websocket_url"],
        access_key=exchanges["bithumb"].get("access_key"),
        secret_key=exchanges["bithumb"].get("secret_key"),
    )

    upbit_limits = DEFAULT_LIMITS["upbit"]
    bithumb_limits = DEFAULT_LIMITS["bithumb"]
    upbit_gateway = UpbitGateway(
        upbit_settings,
        public_limiter=TokenBucket(upbit_limits.public_capacity, upbit_limits.public_rate),
        private_limiter=TokenBucket(upbit_limits.private_capacity, upbit_limits.private_rate),
    )
    bithumb_gateway = BithumbGateway(
        bithumb_settings,
        public_limiter=TokenBucket(bithumb_limits.public_capacity, bithumb_limits.public_rate),
        private_limiter=TokenBucket(bithumb_limits.private_capacity, bithumb_limits.private_rate),
    )

    upbit_wrapper = UpbitWrapper(upbit_gateway, UpbitParser())
    bithumb_wrapper = BithumbWrapper(bithumb_gateway, BithumbParser())

    upbit_manager = OrderBookManager()
    bithumb_manager = OrderBookManager()

    upbit_feed = OrderBookFeed(upbit_wrapper, config["trading"]["symbol_upbit"], upbit_manager)
    bithumb_feed = OrderBookFeed(bithumb_wrapper, config["trading"]["symbol_bithumb"], bithumb_manager)

    strategy = SpreadArbitrageStrategy(
        StrategyConfig(
            min_profit_rate=Decimal(str(config["trading"]["min_profit_rate"])),
            max_volume=Decimal("0.1"),
            upbit_fee=Decimal("0.001"),
            bithumb_fee=Decimal("0.0025"),
        )
    )

    risk_manager = RiskManager(
        RiskConfig(
            reserve_ratio=Decimal("0.1"),
            position_limit=PositionLimit(max_volume=Decimal("0.5"), max_notional=Decimal("100000000")),
            circuit_breaker=CircuitBreakerConfig(failure_threshold=3, cool_down=5),
        )
    )

    executor = OrderExecutor(upbit_wrapper, bithumb_wrapper, dry_run=True)

    engine = DryRunEngine(
        upbit_wrapper=upbit_wrapper,
        bithumb_wrapper=bithumb_wrapper,
        upbit_manager=upbit_manager,
        bithumb_manager=bithumb_manager,
        strategy=strategy,
        risk_manager=risk_manager,
        executor=executor,
        feeds=[upbit_feed, bithumb_feed],
        poll_interval=0.5,
    )

    await engine.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
