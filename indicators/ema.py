'''
Manages the EMA indicator.
Allows to calculate EMA.
'''

# ? IMPORTS
import pandas as pd

# & CLASS INIT
class EMA_Indicator:
    '''
    Calculates EMA for given data.
    '''

    # * CONSTRUCTOR
    def __init__(self, fast: int, slow: int):
        self.fast = fast
        self.slow = slow
        
    # * FUNCTION TO CALCULATE EMA
    def calculate_ema(self, data: pd.DataFrame) -> pd.DataFrame:
        '''
        Calculates EMA for given data.

        :param data: DataFrame with 'close' column.
        :return: DataFrame with EMA columns added.
        '''
        data[f'ema_{self.fast}'] = data['close'].ewm(span=self.fast, adjust=False).mean()
        data[f'ema_{self.slow}'] = data['close'].ewm(span=self.slow, adjust=False).mean()
        return data