'''
Manages the EMA strategy.
'''

# ? IMPORTS
from .base_strategy import BaseStrategy
from models.signal import Signal
import pandas as pd
from datetime import datetime


# & CLASS INIT
class EMA_Strategy(BaseStrategy):
    '''
    Generates signals based to given fast and slow EMA levels
    '''

    # * CONSTRUCTOR
    def __init__(self, fast: int, slow: int, threshold: float = 0.0):
        super().__init__()
        self.fast = fast
        self.slow = slow
        self.threshold = threshold
        self.symbol = None
        self.NAME = f"EMA {self.fast}/{self.slow}"

    # * FUNCTION TO GENERATE SIGNAL BASED ON EMA CROSSOVER
    def generate_signal(self, data: pd.DataFrame, threshold: float|None = None) -> Signal|None:
        '''
        Generates a trading signal based on EMA crossover.

        :param data: A DataFrame containing 'close' prices and pre-calculated EMA values.
        :param threshold: The threshold for generating signals. If None, uses the instance's threshold.
        :return: A Signal object indicating 'buy' or 'sell', sometimes None.
        '''

        # Ensure the DataFrame has the necessary columns
        if (
            f'ema_{self.fast}' not in data.columns or 
            f'ema_{self.slow}' not in data.columns or
            f'close' not in data.columns
        ):
            raise ValueError(f"Data must contain 'ema_{self.fast}', 'ema_{self.slow}', and 'close' columns.")
        
        # Get current and previous candles
        current_candle = data.iloc[-2]
        previous_candle = data.iloc[-3]

        # Calculate the distance between the EMAs
        current_distance = current_candle[f'ema_{self.fast}'] - current_candle[f'ema_{self.slow}']
        previous_distance = previous_candle[f'ema_{self.fast}'] - previous_candle[f'ema_{self.slow}']

        # Set a threshold for signal generation
        if (threshold is None):
            threshold = self.threshold

        # Check for buy signal (fast EMA crosses above slow EMA)
        if (
            current_distance > threshold and
            previous_distance <= -threshold
        ):
            sl = min(current_candle['low'], previous_candle['low'])
            risk = abs(current_candle['close'] - sl)
            reward = risk * 4   # 1:4
            tp = current_candle['close'] + reward

            return Signal(
                self.symbol,
                current_candle['time'],
                current_candle['close'],
                type=Signal.BUY,
                sl=sl,
                tp=tp,
                strategy="EMA 8/33",
                risk=risk,
                reward=reward
            )


        # Check for sell signal (fast EMA crosses below slow EMA)
        elif (
            current_distance < -threshold and
            previous_distance >= threshold
        ):
            sl = max(current_candle['high'], previous_candle['high'])
            risk = abs(sl - current_candle['close'])
            reward = risk * 4   # 1:4
            tp = current_candle['close'] - reward

            return Signal(
                self.symbol,
                current_candle['time'],
                current_candle['close'],
                type=Signal.SELL,
                sl=sl,
                tp=tp,
                strategy="EMA 8/33",
                risk=risk,
                reward=reward
            )
        
        else:
            return None