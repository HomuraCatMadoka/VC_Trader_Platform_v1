"""DryRun 調試腳本：單次拉資料並逐步輸出狀態。"""
from __future__ import annotations

import asyncio
from decimal import Decimal

from business.execution.executor import OrderExecutor
from business.orderbook.manager import OrderBookManager
from business.risk.balance_checker import BalanceState
from business.risk.circuit_breaker import CircuitBreakerConfig
from business.risk.manager import RiskConfig, RiskManager
from business.risk.position_limiter import PositionLimit
from business.strategy.base import StrategyConfig
from business.strategy.spread_arbitrage import SpreadArbitrageStrategy
from core.gateway.base import GatewaySettings
from core.gateway.ratelimit.exchange_limits import DEFAULT_LIMITS
from core.gateway.ratelimit.token_bucket import TokenBucket
from core.gateway.upbit import UpbitGateway
from core.gateway.bithumb import BithumbGateway
from core.parser.upbit import UpbitParser
from core.parser.bithumb import BithumbParser
from core.wrapper.upbit import UpbitWrapper
from core.wrapper.bithumb import BithumbWrapper
from utils.config import get_config


async def main() -> None:
    cfg = get_config()
    exchanges = cfg["exchanges"]

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

    upbit = UpbitWrapper(upbit_gateway, UpbitParser())
    bithumb = BithumbWrapper(bithumb_gateway, BithumbParser())

    symbol_upbit = cfg["trading"]["symbol_upbit"]
    symbol_bithumb = cfg["trading"]["symbol_bithumb"]

    print("[1] 拉取 Upbit/Bithumb 訂單簿...")
    upbit_ob = await upbit.get_orderbook(symbol_upbit)
    bithumb_ob = await bithumb.get_orderbook(symbol_bithumb)
    print(f"    Upbit bid/ask: {upbit_ob.bids[0].price} / {upbit_ob.asks[0].price}")
    print(f"    Bithumb bid/ask: {bithumb_ob.bids[0].price} / {bithumb_ob.asks[0].price}")
    print("    [Upbit] Top 5 bids:")
    for level in upbit_ob.bids[:5]:
        print(f"       price={level.price}, qty={level.quantity}")
    print("    [Bithumb] Top 5 bids:")
    for level in bithumb_ob.bids[:5]:
        print(f"       price={level.price}, qty={level.quantity}")
    print("    [Upbit] Top 5 asks:")
    for level in upbit_ob.asks[:5]:
        print(f"       price={level.price}, qty={level.quantity}")
    print("    [Bithumb] Top 5 asks:")
    for level in bithumb_ob.asks[:5]:
        print(f"       price={level.price}, qty={level.quantity}")

    upbit_manager = OrderBookManager()
    bithumb_manager = OrderBookManager()
    await upbit_manager.update_full(upbit_ob)
    await bithumb_manager.update_full(bithumb_ob)

    strategy = SpreadArbitrageStrategy(
        StrategyConfig(
            min_profit_rate=Decimal(str(cfg["trading"]["min_profit_rate"])),
            max_volume=Decimal("0.1"),
            upbit_fee=Decimal("0.001"),
            bithumb_fee=Decimal("0.0025"),
        )
    )

    print("[2] 策略計算...")
    signal = strategy.calculate(upbit_ob, bithumb_ob)
    if not signal:
        print("    無套利信號（spread 不足或深度為空），但仍繼續打印餘額與風控資訊")
    else:
        print(f"    信號方向: {signal.direction}, spread={signal.spread:.4f}, volume={signal.volume}")

    print("[3] 查詢餘額...")
    upbit_balances = await upbit.get_balance()
    bithumb_balances = await bithumb.get_balance()
    for bal in upbit_balances:
        print(f"    Upbit balance - {bal.currency}: avail={bal.available}, locked={bal.locked}")
    for bal in bithumb_balances:
        print(f"    Bithumb balance - {bal.currency}: avail={bal.available}, locked={bal.locked}")

    balances = BalanceState(
        upbit_btc=_find_balance(upbit_balances, "BTC"),
        upbit_krw=_find_balance(upbit_balances, "KRW"),
        bithumb_btc=_find_balance(bithumb_balances, "BTC"),
        bithumb_krw=_find_balance(bithumb_balances, "KRW"),
    )

    risk_manager = RiskManager(
        RiskConfig(
            reserve_ratio=Decimal("0.1"),
            position_limit=PositionLimit(max_volume=Decimal("0.5"), max_notional=Decimal("100000000")),
            circuit_breaker=CircuitBreakerConfig(failure_threshold=3, cool_down=5),
        )
    )

    print("[4] 風控評估...")
    if signal:
        ok = await risk_manager.evaluate(signal, balances)
        if not ok:
            print("    風控拒絕信號：餘額不足或超過限額")
        else:
            print("    風控通過，執行 DryRun")
            executor = OrderExecutor(upbit, bithumb, dry_run=True)
            await executor.execute(signal)
            print("[5] DryRun 完成。")
    else:
        print("[4] 略過風控與 DryRun (因無信號)")

    await upbit_gateway.close()
    await bithumb_gateway.close()


def _find_balance(balances, currency: str) -> Decimal:
    for bal in balances:
        if bal.currency.upper() == currency.upper():
            return bal.available
    return Decimal("0")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
