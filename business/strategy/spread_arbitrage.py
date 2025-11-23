"""價差套利策略。"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from core.datatypes import OrderBook
from business.strategy.base import BaseStrategy, StrategyConfig
from business.strategy.signal import ArbitrageDirection, StrategySignal
from utils.logger import setup_logger

logger = setup_logger("strategy")


class SpreadArbitrageStrategy(BaseStrategy):
    """比較 Upbit 與 Bithumb 的買賣價差，輸出套利信號。"""

    def __init__(self, config: StrategyConfig) -> None:
        super().__init__(config)

    def calculate(self, upbit_ob: OrderBook, bithumb_ob: OrderBook) -> Optional[StrategySignal]:
        if not upbit_ob.bids or not upbit_ob.asks or not bithumb_ob.bids or not bithumb_ob.asks:
            return None
        upbit_best_bid = upbit_ob.bids[0]
        upbit_best_ask = upbit_ob.asks[0]
        bithumb_best_bid = bithumb_ob.bids[0]
        bithumb_best_ask = bithumb_ob.asks[0]

        spreads = [
            self._calc_spread(
                sell_price=upbit_best_bid.price,
                buy_price=bithumb_best_ask.price,
                direction=ArbitrageDirection.UPBIT_SELL,
                available_volume=min(upbit_best_bid.quantity, bithumb_best_ask.quantity),
                upbit_price=upbit_best_bid.price,
                bithumb_price=bithumb_best_ask.price,
            ),
            self._calc_spread(
                sell_price=bithumb_best_bid.price,
                buy_price=upbit_best_ask.price,
                direction=ArbitrageDirection.BITHUMB_SELL,
                available_volume=min(bithumb_best_bid.quantity, upbit_best_ask.quantity),
                upbit_price=upbit_best_ask.price,
                bithumb_price=bithumb_best_bid.price,
            ),
        ]
        valid_signals = [signal for signal in spreads if signal]
        if not valid_signals:
            logger.debug("Spread 不足，無信號")
            return None
        best = max(valid_signals, key=lambda sig: sig.expected_profit)
        logger.debug(
            "產生策略信號",
            extra={
                "direction": best.direction,
                "spread": str(best.spread),
                "volume": str(best.volume),
            },
        )
        return best

    def _calc_spread(
        self,
        *,
        sell_price: Decimal,
        buy_price: Decimal,
        direction: ArbitrageDirection,
        available_volume: Decimal,
        upbit_price: Decimal,
        bithumb_price: Decimal,
    ) -> Optional[StrategySignal]:
        if available_volume <= 0:
            return None
        spread = (sell_price - buy_price) / buy_price
        threshold = self._config.total_fee + self._config.min_profit_rate
        if spread <= threshold:
            return None
        volume = min(available_volume, self._config.max_volume)
        expected_profit = spread - self._config.total_fee
        return StrategySignal(
            direction=direction,
            expected_profit=expected_profit,
            volume=volume,
            upbit_price=upbit_price,
            bithumb_price=bithumb_price,
            spread=spread,
        )
