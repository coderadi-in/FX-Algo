'''
Manage the back testing engine.
Used to back test strategies.
'''

# ? IMPORTS
from account.account_service import AccountService
from risk.risk_manager import RiskManager
from consensus.consensus_engine import ConsensusEngine
from strategies.base_strategy import BaseStrategy
import pandas as pd
from models.trade import Trade
from datetime import datetime


# & CLASS INIT
class BackTestingEngine:
    '''
    Back tests a strategy over a dataframe of candles.
    '''

    # * CONSTRUCTOR
    def __init__(
        self, *, account: AccountService,
        manager: RiskManager,
        data: pd.DataFrame=None,
        consensus: ConsensusEngine,
        symbol: str
    ):
        self.account = account
        self.manager = manager
        self.consensus = consensus
        self.strategies: list[BaseStrategy] = []
        self.data = data
        self.symbol = symbol
        self.trades = []

    # * FUNCTION TO ADD STRATEGY
    def add_strategy(self, strategy: BaseStrategy):
        '''
        Adds an strategy in the engine.

        :param strategy: The strategy object to add.
        '''

        self.strategies.append(strategy)
        print(f"Fed strategy: {strategy.NAME}")

    # * FUNCTION TO FEED DATA
    def feed_data(self, data: pd.DataFrame):
        '''
        Feeds candles data in the engine.

        :param data: A DataFrame containing candles data.
        '''

        self.data = data

    # * FUNCTION TO GET THE CURRENT OPENED POSITION
    def get_opened_pos(self, symbol: str) -> Trade|None:
        '''
        Returns the current opened position.

        :param symbol: The symbol to get opened position of.
        '''

        return self.account.open_positions.get(symbol)
    
    # * FUNCTION TO CLOSE A POSITION
    def close_pos(self, trade_obj: Trade, exit_time: datetime|int, exit_price: float, exit_reason: str, pl: float):
        '''
        Closes an opened position and appends to trades list.

        :param trade_obj: The trade object of opened position.
        :param exit_time: Exit time of position.
        :param exit_price: Exit price of position.
        :param exit_reason: Exit reason of 
        :param pl: The profit or loss amount.
        '''

        trade_obj.exit_time = exit_time
        trade_obj.exit_price = exit_price
        trade_obj.close_reason = exit_reason
        trade_obj.profit = pl

        self.trades.append(trade_obj.to_dict())
        self.account.open_positions[trade_obj.symbol] = None

    # * FUNCTION TO RUN THE ENGINE WITH OPTIMISTIC SIMULATION
    def run_optimistic_simulation(self, start_index: int = 50):
        '''
        Runs the engine with optimistic simulation.

        :param start_index: The amount of candles to start simulation with.
        '''

        print("Running optimistic simulation...")

        for i in range(start_index, len(self.data)):
            # Create partial dataframe to analyze
            current_df = self.data.iloc[:i]

            # Check for SL/TP
            current_pos = self.get_opened_pos(self.symbol)
            if (current_pos is not None):
                current_candle = current_df.iloc[-1] # Last closed candle
                profit = 0

                if (current_pos.type == 'BUY'):

                    if (current_candle['high'] >= current_pos.tp):
                        profit = current_pos.reward
                        self.close_pos(current_pos, current_candle['time'], current_pos.tp, "TP", profit)

                    elif (current_candle['low'] <= current_pos.sl):
                        profit = -current_pos.risk
                        self.close_pos(current_pos, current_candle['time'], current_pos.sl, "SL", profit)

                    self.account.balance += profit
                    self.account.equity += profit
                    self.account.free_margin += profit

                elif (current_pos.type == 'SELL'):
                    if (current_candle['low'] <= current_pos.tp):
                        profit = current_pos.reward
                        self.close_pos(current_pos, current_candle['time'], current_pos.tp, "TP", profit)

                    elif (current_candle['high'] >= current_pos.sl):
                        profit = -current_pos.risk
                        self.close_pos(current_pos, current_candle['time'], current_pos.sl, "SL", profit)

                    self.account.balance += profit
                    self.account.equity += profit
                    self.account.free_margin += profit

            # Analyze data with all strategies
            for strategy in self.strategies:
                signal = strategy.generate_signal(current_df)
                if (signal is None): continue
                self.consensus.add_signal(signal)

            # Finalize a signal with consensus engine
            final_signal = self.consensus.finalize()
            if (final_signal is None): continue

            # Validate signal
            validation = self.manager.validate(final_signal)

            # Conditional if signal is rejected.
            if (not validation.allowed):
                # print("Signal reject by Risk Manager.")
                # print(validation.reason + "\n")
                continue

            # Open a position
            opened_position = Trade(
                symbol=final_signal.symbol,
                entry_time=final_signal.entry_time,
                entry_price=final_signal.entry_price,
                type=final_signal.type,
                sl=final_signal.sl,
                tp=final_signal.tp,
                risk=final_signal.risk,
                reward=final_signal.reward
            )

            # Add opened position to account service
            self.account.open_positions[final_signal.symbol] = opened_position