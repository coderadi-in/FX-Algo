'''
Manages the account service class.
A virtual account system for the engine.
'''

# ? IMPORTS
import pandas as pd
from datetime import date
from models.trade import Trade


# & CLASS INIT
class AccountService:
    '''Represents a user account.'''

    TRADE_HISTORY_FILE = 'data/trade_history.csv'
    STARTING_CAPITAL = 15_000

    # * CONSTRUCTOR
    def __init__(self, balance: float):
        self.balance = balance
        self.equity = balance
        self.margin = 0
        self.free_margin = balance
        self.margin_level = 0
        self.open_positions: dict[str:Trade] = {}

    # * FUNCTION TO GET ALL TRADES OF CURRENT DATE
    def get_current_date_trades(self):
        '''Returns all trades made in the current date (today).'''

        trades = pd.read_csv(self.TRADE_HISTORY_FILE)
        trades['time'] = pd.to_datetime(trades['time'], unit="s", utc=True)
        today = date.today()

        current_date_trades = trades[trades['time'].date == today]
        return current_date_trades