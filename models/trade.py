'''
Manges the Trade class
Allows to manage risk based on historical statistics.
'''

# ? IMPORTS
from datetime import datetime


# & CLASS INIT
class Trade:
    '''Represents a trade.'''

    def __init__(
        self, *, symbol: str, entry_time: int|datetime, exit_time: int|datetime,
        entry_price: float, exit_price: float, type: str, sl: float, tp: float,
        risk: float|None=None, reward: float|None=None, profit: float,
        close_reason: str
    ):
        self.symbol = symbol
        self.type = type

        self.entry_time = entry_time
        self.exit_time = exit_time,

        self.entry_price = entry_price
        self.exit_price = exit_price

        self.sl = sl
        self.tp = tp

        self.risk = abs(self.entry_price - self.sl) if risk is None else risk
        self.reward = self.entry_price + abs(self.tp) if reward is None else reward

        self.profit = profit
        self.close_reason = close_reason