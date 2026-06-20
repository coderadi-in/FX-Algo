'''
Manages the `MT5Service()` class.
Allows communication with MT5.
'''

# ? IMPORTS
import MetaTrader5 as mt5
import pandas as pd

# & CLASS INIT
class MT5Service:
    '''
    Communicates with MT5.

    ## Usage
    ```python
        from services.mt5_service import MT5Service
        service = MT5Service()
    ```
    '''

    # * CONSTRUCTOR
    def __init__(self):
        if (not mt5.initialize()):
            print("Failed to connect with MT5:", mt5.last_error())
            quit()

    # * FUNCTION TO GET SYMBOL INFO
    def get_pip_value(self, symbol: str):
        '''
        Returns the value of market movement of one pip for given symbol.

        :param symbol: The symbol to get pip value of.
        '''

        info = mt5.symbol_info(symbol)

        trade_tick_value = info.trade_tick_value
        trade_tick_size = info.trade_tick_size

        return (
            trade_tick_value
            * (self.get_pip_size(symbol) / trade_tick_size)
        )
    
    # * FUNCTION TO GET PIP SIZE
    def get_pip_size(self, symbol: str) -> float:
        '''
        Returns the size one pip for given symbol.

        :param symbol: The symbol to get pip size of.
        '''

        info = mt5.symbol_info(symbol)

        if (info.digits in (3, 5)):
            return info.point * 10

        return info.point
    
    # * FUNCTION TO GET SYMBOL INFO
    def get_symbol_info(self, symbol: str):
        '''
        Returns the symbol info of provided symbol.

        :param symbol: The symbol to get info of.
        '''

        info = mt5.symbol_info(symbol)
        return info._asdict()

    # * FUNCTION TO FETCH HISTORY
    def get_history(self, symbol: str, timeframe: int, amount: int):
        '''
        Fetches historical data for given symbol, timeframe and amount.

        :param symbol: The symbol to fetch data for.
        :param timeframe: The timeframe to fetch data for.
        :param amount: The amount of data to fetch.
        :return: A DataFrame containing the historical data.
        '''

        data = mt5.copy_rates_from_pos(
            symbol, timeframe,
            0, amount
        )

        return pd.DataFrame(data)