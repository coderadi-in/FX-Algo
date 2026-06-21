'''
Manages the BaseStrategy class.
'''

# ? IMPORTS
import pandas as pd
from models.signal import Signal

# & CLASS INIT
class BaseStrategy:
    '''
    Foundation of all strategies.
    '''

    NAME = None

    # * CONSTRUCTOR
    def __init__(self):
        pass

    # * FUNCTION TO ANALYZE SIGNAL
    def generate_signal(self, data: pd.DataFrame) -> Signal|None:
        '''
        Generates a trading signal.

        :param data: A Dataframe containing 'close' prices and pre-calculated strategy values.
        '''