'''
Manages the MT5Account class.
Used to trade with virtual/real MT5 account.
'''

# ? IMPORTS
import MetaTrader5 as mt5
from datetime import datetime


# & CLASS INIT
class MT5Account:
    '''
    Uses a virtual/real MT5 account to trade in live market.
    '''

    # * CONSTRUCTOR
    def __init__(self, logged: bool=True):
        # LOGIN
        if (not logged) and (not mt5.initialize()):
            print("Failed to connect with MT5:", mt5.last_error())
            quit()

        # FETCH ACCOUNT DATA
        acc_info = mt5.account_info()

        self.balance = acc_info.balance
        self.equity = acc_info.equity
        self.free_margin = acc_info.margin_free

    # * FUNCTION TO GET OPENED POSITIONS FOR SPECIFIC SYMBOL
    def get_opened_pos(self, symbol: str):
        '''
        Returns all opened positions for specified symbol.

        :param symbol: The symbol to get open positions of.
        '''

        positions = mt5.positions_get(symbol=symbol)

        if (positions is None):
            print(f"\nCan't fetch opened positions for {symbol}")
            print(mt5.last_error(), end="\n\n")

        return positions

    # * FUNCTION TO GET ALL TRADES OF CURRENT DATE
    def get_current_date_trades(self):
        '''Returns all trades made in the current day (today)'''

        trades = mt5.history_orders_get(
            from_date=datetime.today(),
            to_date=datetime.today()
        )

        if (trades is None):
            print(f"Can't fetch order history from account.")
            print(mt5.last_error(), end="\n\n")

        return trades