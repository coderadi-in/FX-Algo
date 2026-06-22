"""
Manges the Trade class
Allows to manage risk based on historical statistics.
"""

# ? IMPORTS
from datetime import datetime


# & CLASS INIT
class Trade:
    """Represents a trade."""

    def __init__(
        self,
        *,
        symbol: str,
        entry_time: int | datetime,
        exit_time: int | datetime = None,
        entry_price: float,
        exit_price: float = None,
        type: str,
        sl: float,
        tp: float,
        risk: float | None = None,
        reward: float | None = None,
        profit: float = None,
        close_reason: str = None,
        lot_size: float = None
    ):
        self.symbol = symbol
        self.type = type

        self.entry_time = entry_time
        self.exit_time = exit_time

        self.entry_price = entry_price
        self.exit_price = exit_price

        self.sl = sl
        self.tp = tp

        self.risk = abs(self.entry_price - self.sl) if risk is None else risk
        self.reward = self.entry_price + abs(self.tp) if reward is None else reward

        self.profit = profit
        self.close_reason = close_reason
        self.lot_size = lot_size

    def __str__(self):
        return f"Trade({self.symbol}, {self.type}, {self.close_reason}, {self.entry_time}, {self.entry_price}, {self.profit})"

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'type': self.type,
            'entry_time': self.entry_time,
            'exit_time': self.exit_time,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'sl': self.sl,
            'tp': self.tp,
            'risk': self.risk,
            'reward': self.reward,
            'profit': self.profit,
            'close_reason': self.close_reason,
            'lot_size': self.lot_size
        }