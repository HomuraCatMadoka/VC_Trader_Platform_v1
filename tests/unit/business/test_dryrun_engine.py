"""DryRunEngine 測試。"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Optional

from business.engine.dryrun import DryRunEngine, PairContext
from business.execution.executor import OrderExecutor
from business.orderbook.manager import OrderBookManager
from business.risk.circuit_breaker import CircuitBreakerConfig
from business.risk.manager import RiskConfig, RiskManager
from business.risk.position_limiter import PositionLimit
from business.strategy.base import StrategyConfig
from business.strategy.spread_arbitrage import SpreadArbitrageStrategy
from core.datatypes import Balance, OrderBook, OrderResult, PriceLevel
from core.interface import BaseGateway
from core.parser.base import JsonParser
from core.wrapper.base import BaseExchangeWrapper


class DummyParser(JsonParser):
    def parse_orderbook(self, raw: bytes):  # pragma: no cover
        raise NotImplementedError

    def parse_balance(self, raw: bytes):  # pragma: no cover
        raise NotImplementedError

    def parse_order_result(self, raw: bytes):  # pragma: no cover
        raise NotImplementedError


class DummyGateway(BaseGateway):
    async def request(self, method: str, endpoint: str, *, params=None, signed=False, headers=None) -> bytes:  # pragma: no cover
        raise NotImplementedError

    async def ws_connect(self, url: Optional[str] = None, *, headers=None):  # pragma: no cover
        raise NotImplementedError

    async def close(self) -> None:  # pragma: no cover
        return


class FakeWrapper(BaseExchangeWrapper):
    def __init__(self, name: str, orderbook: OrderBook, balances: dict[str, Decimal]):
        super().__init__(DummyGateway(), DummyParser())
        self.name = name
        self._orderbook = orderbook
        self._balances = balances
        self.market_orders: list[str] = []

    async def get_orderbook(self, symbol: str) -> OrderBook:
        return self._orderbook

    async def get_balance(self) -> list[Balance]:
        return [
            Balance(exchange=self.name, currency=cur, available=amt, locked=Decimal("0"), total=amt)
            for cur, amt in self._balances.items()
        ]

    async def buy_market_order(self, symbol: str, amount: Decimal) -> OrderResult:
        self.market_orders.append(f"buy:{amount}")
        return _dummy_result(symbol)

    async def sell_market_order(self, symbol: str, volume: Decimal) -> OrderResult:
        self.market_orders.append(f"sell:{volume}")
        return _dummy_result(symbol)

    async def place_order(self, order):  # pragma: no cover
        raise NotImplementedError

    async def cancel_order(self, order_id: str):  # pragma: no cover
        raise NotImplementedError

    async def get_order_status(self, order_id: str):  # pragma: no cover
        raise NotImplementedError

    async def subscribe_orderbook(self, symbol: str, callback):  # pragma: no cover
        raise NotImplementedError


class DummyFeed:
    def __init__(self, manager: OrderBookManager) -> None:
        self.manager = manager

    async def start(self) -> None:  # pragma: no cover - 測試不啟動真實訂閱
        return

    async def stop(self) -> None:  # pragma: no cover
        return


def _dummy_result(symbol: str) -> OrderResult:
    return OrderResult(
        order_id="test",
        exchange="test",
        symbol=symbol,
        status="filled",
        filled_quantity=Decimal("0"),
        average_price=None,
        raw=None,
    )


def _orderbook(symbol: str, bid_price: Decimal, ask_price: Decimal) -> OrderBook:
    return OrderBook(
        symbol=symbol,
        exchange="test",
        bids=[PriceLevel(price=bid_price, quantity=Decimal("0.5"), timestamp=0)],
        asks=[PriceLevel(price=ask_price, quantity=Decimal("0.5"), timestamp=0)],
        sequence=0,
        timestamp=0,
    )


def test_dryrun_engine_executes_signal() -> None:
    upbit_ob = _orderbook("KRW-BTC", Decimal("95000000"), Decimal("95100000"))
    bithumb_ob = _orderbook("BTC_KRW", Decimal("93000000"), Decimal("93100000"))
    upbit_wrapper = FakeWrapper(
        "upbit",
        upbit_ob,
        balances={"BTC": Decimal("1"), "KRW": Decimal("100000000")},
    )
    bithumb_wrapper = FakeWrapper(
        "bithumb",
        bithumb_ob,
        balances={"BTC": Decimal("1"), "KRW": Decimal("100000000")},
    )
    upbit_manager = OrderBookManager()
    bithumb_manager = OrderBookManager()

    async def init_managers() -> None:
        await upbit_manager.update_full(upbit_ob)
        await bithumb_manager.update_full(bithumb_ob)

    asyncio.run(init_managers())

    strategy = SpreadArbitrageStrategy(
        StrategyConfig(
            min_profit_rate=Decimal("0.005"),
            max_volume=Decimal("0.1"),
            upbit_fee=Decimal("0.001"),
            bithumb_fee=Decimal("0.0025"),
        )
    )
    from business.risk.circuit_breaker import CircuitBreakerConfig

    risk_manager = RiskManager(
        RiskConfig(
            reserve_ratio=Decimal("0.1"),
            position_limit=PositionLimit(max_volume=Decimal("0.5"), max_notional=Decimal("100000000")),
            circuit_breaker=CircuitBreakerConfig(failure_threshold=3, cool_down=1),
        )
    )
    executor = OrderExecutor(upbit_wrapper, bithumb_wrapper, dry_run=False)
    pair = PairContext(
        name="BTC",
        upbit_symbol="KRW-BTC",
        bithumb_symbol="BTC_KRW",
        upbit_manager=upbit_manager,
        bithumb_manager=bithumb_manager,
        upbit_feed=DummyFeed(upbit_manager),
        bithumb_feed=DummyFeed(bithumb_manager),
    )

    engine = DryRunEngine(
        upbit_wrapper=upbit_wrapper,
        bithumb_wrapper=bithumb_wrapper,
        strategy=strategy,
        risk_manager=risk_manager,
        executor=executor,
        pairs=[pair],
        poll_interval=0.1,
    )

    asyncio.run(engine.run_once())
    assert upbit_wrapper.market_orders[0].startswith("sell")
    assert bithumb_wrapper.market_orders[0].startswith("buy")
