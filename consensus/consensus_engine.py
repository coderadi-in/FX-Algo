'''
Manages the consensus engine.
Used to manage the signals of multiple strategies.
'''

# ? IMPORTS
from models.signal import Signal
import pandas as pd


# & CLASS INIT
class ConsensusEngine:
    '''
    Manages the signals of multiple strategies.
    Gives an average direction of all signals.
    '''

    TYPE_BUY = "BUY"
    TYPE_SELL = "SELL"
    NAME = "ConsensusEngine"

    def __init__(self):
        self.signals: list[Signal] = []
        self.df: list[dict] = []

    def add_signal(self, signal: Signal):
        '''
        Adds a signal to the engine.

        :param signal: The signal object to add.
        '''

        self.signals.append(signal)

    def count(self) -> str|None:
        '''
        Returns the direction most strategies point to.
        '''

        buy_count = 0
        sell_count = 0

        for signal in self.signals:
            self.df.append(signal.to_dict())
            if (signal.type == self.TYPE_BUY):
                buy_count += 1

            elif (signal.type == self.TYPE_SELL):
                sell_count += 1

        if (buy_count > sell_count):
            return self.TYPE_BUY
        elif (sell_count > buy_count):
            return self.TYPE_SELL
        return None
    

    def finalize(self):
        '''
        Finalized which direction to go for.
        '''

        if (not self.signals):
            return None

        direction = self.count()
        consensus_signals = [signal for signal in self.signals if signal.type == direction]
        
        if (not consensus_signals):
            return None

        base_signal = consensus_signals[0]
        self.signals = []

        return Signal(
            symbol=base_signal.symbol,
            entry_time=base_signal.entry_time,
            entry_price=base_signal.entry_price,
            type=base_signal.type,
            sl=base_signal.sl,
            tp=base_signal.tp,
            strategy=base_signal.strategy,
            risk=base_signal.risk,
            reward=base_signal.reward,
        )
