'''
Manages the BaseIndicator class
'''

# ? IMPORTS
import pandas as pd
from models.signal import Signal


# & CLASS INIT
class BaseIndicator:
    '''
    Foundation of all indicators
    '''

    # * CONSTRUCTOR
    def __init__(self):
        self.NAME = None

    # * FUNCTION TO CALCULATE VALUES
    def calculate_values(self, data: pd.DataFrame) -> pd.DataFrame:
        '''
        Calculate values for given data.

        :param data: DataFrame with 'close' column.
        :return: DataFrame with computed values.
        '''

        pass