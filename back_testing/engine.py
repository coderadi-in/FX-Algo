'''
Manage the back testing engine.
Used to back test strategies.
'''

# ? IMPORTS
from account.account_service import AccountService
from risk.risk_manager import RiskManager
from consensus.consensus_engine import ConsensusEngine
from strategies.base_strategy import BaseStrategy
from services.mt5_service import MT5Service
import pandas as pd
from models.trade import Trade
from models.signal import Signal
from datetime import datetime
from typing import Literal


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
        symbol: str,
        service: MT5Service
    ):
        self.account = account
        self.manager = manager
        self.consensus = consensus
        self.strategies: list[BaseStrategy] = []
        self.data = data
        self.symbol = symbol
        self.service = service
        self.trades: list[dict] = []
        self.rejected: list[Signal] = []

        self.OPTIMISTIC = "optimistic"
        self.PESSIMISTIC = "pessimistic"

        self.CONTRACT_SIZES = {
            "XAUUSD": 100,
            "EURUSD": 100_000,
            "GBPUSD": 100_000,
            "USDJPY": 100_000,
        }


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

    # * FUNCTION TO CHECK FOR SL/TP IN OPTIMISTIC ORDER
    def check_sltp_optimistic(self, current_df: pd.DataFrame, current_pos: Trade):
        '''
        Checks for SL/TP hit in optimistic order.
        Optimistic order means it first checks for TP hits.

        :param current_df: The currently simulating dataframe section.
        :param current_pos: The currently opened position.
        '''

        current_candle = current_df.iloc[-1] # Last closed candle
        profit = 0

        if (current_pos.type == 'BUY'):

            if (current_candle['high'] >= current_pos.tp):
                profit = self.points_to_usd(current_pos.reward, current_pos.lot_size, self.CONTRACT_SIZES[current_pos.symbol])
                self.close_pos(current_pos, current_candle['time'], current_pos.tp, "TP", profit)

            elif (current_candle['low'] <= current_pos.sl):
                profit = self.points_to_usd(-current_pos.risk, current_pos.lot_size, self.CONTRACT_SIZES[current_pos.symbol])
                self.close_pos(current_pos, current_candle['time'], current_pos.sl, "SL", profit)

            self.account.balance += profit
            self.account.equity += profit
            self.account.free_margin += profit

        elif (current_pos.type == 'SELL'):
            if (current_candle['low'] <= current_pos.tp):
                profit = self.points_to_usd(current_pos.reward, current_pos.lot_size, self.CONTRACT_SIZES[current_pos.symbol])
                self.close_pos(current_pos, current_candle['time'], current_pos.tp, "TP", profit)

            elif (current_candle['high'] >= current_pos.sl):
                profit = self.points_to_usd(-current_pos.risk, current_pos.lot_size, self.CONTRACT_SIZES[current_pos.symbol])
                self.close_pos(current_pos, current_candle['time'], current_pos.sl, "SL", profit)

            self.account.balance += profit
            self.account.equity += profit
            self.account.free_margin += profit

    # * FUNCTION TO CHECK FOR SL/TP IN PESSIMISTIC ORDER
    def check_sltp_pessimistic(self, current_df: pd.DataFrame, current_pos: Trade):
        '''
        Checks for SL/TP hit in pessimistic order.
        Pessimistic order means it first checks for SL hits.

        :param current_df: The currently simulating dataframe section.
        :param current_pos: The currently opened position.
        '''

        current_candle = current_df.iloc[-1] # Last closed candle
        profit = 0

        if (current_pos.type == 'BUY'):
            if (current_candle['low'] <= current_pos.sl):
                profit = self.points_to_usd(-current_pos.risk, current_pos.lot_size, self.CONTRACT_SIZES[current_pos.symbol])
                self.close_pos(current_pos, current_candle['time'], current_pos.sl, "SL", profit)

            elif (current_candle['high'] >= current_pos.tp):
                profit = self.points_to_usd(current_pos.reward, current_pos.lot_size, self.CONTRACT_SIZES[current_pos.symbol])
                self.close_pos(current_pos, current_candle['time'], current_pos.tp, "TP", profit)


            self.account.balance += profit
            self.account.equity += profit
            self.account.free_margin += profit

        elif (current_pos.type == 'SELL'):
            if (current_candle['high'] >= current_pos.sl):
                profit = self.points_to_usd(-current_pos.risk, current_pos.lot_size, self.CONTRACT_SIZES[current_pos.symbol])
                self.close_pos(current_pos, current_candle['time'], current_pos.sl, "SL", profit)

            elif (current_candle['low'] <= current_pos.tp):
                profit = self.points_to_usd(current_pos.reward, current_pos.lot_size, self.CONTRACT_SIZES[current_pos.symbol])
                self.close_pos(current_pos, current_candle['time'], current_pos.tp, "TP", profit)

            self.account.balance += profit
            self.account.equity += profit
            self.account.free_margin += profit

    # * FUNCTION TO CLEAR ENGINE
    def shutdown(self):
        '''
        Clears everything from the engine includes trades, rejected signals, and other run-time insights.
        '''

        self.account = None
        self.manager = None
        self.consensus = None
        self.strategies: list[BaseStrategy] = []
        self.data = None
        self.symbol = None
        self.trades: list[dict] = []
        self.rejected: list[Signal] = []

    # * FUNCTION TO CONVERT POINTS TO USD
    def points_to_usd(self, points: float, lot_size: float, contract_size: float) -> float:
        """
        Converts a price movement (points) into USD profit/loss.

        :param points: Price movement (tp - entry or entry - sl)
        :param lot_size: Trade lot size (e.g. 0.01, 0.1, 1.0)
        :param contract_size: Units per lot.

        Returns:
            Profit/Loss in USD.
        """
        return points * lot_size * contract_size

    # * FUNCTION TO RUN THE ENGINE WITH OPTIMISTIC SIMULATION
    def run(
        self, start_index: int = 50, 
        simulation: Literal["optimistic", "pessimistic"] = None,
    ):
        '''
        Runs the engine with optimistic simulation.

        :param start_index: The amount of candles to start simulation with.
        :param simulation: Simulation type "optimistic" or "pessimistic".
        '''

        if (simulation not in ["optimistic", "pessimistic"]):
            print("Simulation type is invalid, expected 'optimistic' or 'pessimistic'")
            return

        print(f"\nRunning {simulation} simulation...")
        print("Press 'ctrl+C' to stop\n")

        try:

            for i in range(start_index, len(self.data)):
                # Create partial dataframe to analyze
                current_df = self.data.iloc[:i]

                # Check for SL/TP
                current_pos = self.get_opened_pos(self.symbol)
                if (current_pos is not None):
                    if (simulation == "optimistic"): self.check_sltp_optimistic(current_df, current_pos)
                    elif (simulation == "pessimistic"): self.check_sltp_pessimistic(current_df, current_pos)

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
                    print("Signal rejected by Risk Manager")
                    print(validation.reason, end="\n\n")
                    self.rejected.append(final_signal)
                    continue

                # Calculate ideal lot size for the trade
                symbol_info = self.service.get_symbol_info(self.symbol)
                ideal_lot_size = self.manager.calculate_lot_size(symbol_info, validation.signal.risk)
                final_signal.lot_size = ideal_lot_size

                # Open a position
                opened_position = Trade(
                    symbol=final_signal.symbol,
                    entry_time=final_signal.entry_time,
                    entry_price=final_signal.entry_price,
                    type=final_signal.type,
                    sl=final_signal.sl,
                    tp=final_signal.tp,
                    risk=final_signal.risk,
                    reward=final_signal.reward,
                    lot_size=0.1
                )

                # Add opened position to account service
                self.account.open_positions[final_signal.symbol] = opened_position
        
        except KeyboardInterrupt:
            print("Streaming interrupted by user.")
            return