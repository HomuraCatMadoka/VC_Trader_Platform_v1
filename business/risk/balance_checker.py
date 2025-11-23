"""餘額檢查模塊。"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict

from business.strategy.signal import ArbitrageDirection, StrategySignal
from utils.logger import setup_logger

logger = setup_logger("balance_checker")


@dataclass
class BalanceState:
    upbit_btc: Decimal
    upbit_krw: Decimal
    bithumb_btc: Decimal
    bithumb_krw: Decimal


class BalanceChecker:
    def __init__(self, reserve_ratio: Decimal) -> None:
        self._reserve_ratio = reserve_ratio

    def validate(self, signal: StrategySignal, balances: BalanceState) -> bool:
        if signal.direction == ArbitrageDirection.UPBIT_SELL:
            if balances.upbit_btc - signal.volume < balances.upbit_btc * self._reserve_ratio:
                logger.debug("Upbit BTC 餘額不足")
                return False
            # 買入 Bithumb 需要 KRW
            required_krw = signal.volume * signal.bithumb_price
            if balances.bithumb_krw - required_krw < balances.bithumb_krw * self._reserve_ratio:
                logger.debug("Bithumb KRW 餘額不足")
                return False
        else:
            required_krw = signal.volume * signal.upbit_price
            if balances.upbit_krw - required_krw < balances.upbit_krw * self._reserve_ratio:
                logger.debug("Upbit KRW 餘額不足")
                return False
            if balances.bithumb_btc - signal.volume < balances.bithumb_btc * self._reserve_ratio:
                logger.debug("Bithumb BTC 餘額不足")
                return False
        return True
