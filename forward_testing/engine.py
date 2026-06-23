'''
Manage the forward testing engine.
Used to forward test strategies.
'''

# ? IMPORTS
import MetaTrader5 as mt5
from risk.risk_manager import RiskManager
from consensus.consensus_engine import ConsensusEngine
from strategies.base_strategy import BaseStrategy
from indicators.base_indicator import BaseIndicator
from services.mt5_service import MT5Service
from datetime import datetime
import time

# & CLASS INIT
class ForwardTestingEngine:
    '''
    Forward tests a strategy over in real market with a virtual account.
    '''

    # * CONSTRUCTOR
    def __init__(
        self,
        manager: RiskManager,
        consensus: ConsensusEngine,
        service: MT5Service,
        symbol: str
    ):
        self.manager = manager
        self.consensus = consensus
        self.service = service
        self.symbol = symbol
        self.last_candle_time = None
        self.indicators: list[BaseIndicator] = []
        self.strategies: list[BaseStrategy] = []
        
        mt5.symbol_select(self.symbol, True)

    # * FUNCTION TO ADD A STRATEGY TO THE ENGINE
    def add_strategy(self, strategy: BaseStrategy):
        '''
        Adds a strategy to the engine.

        :param strategy: The strategy object to feed.
        '''

        self.strategies.append(strategy)

    # * FUNCTION TO ADD AN INDICATOR TO THE ENGINE
    def add_indicator(self, indicator: BaseIndicator):
        '''
        Adds an indicator to the engine.

        :param indicator: The indicator object to add.
        '''

        self.indicators.append(indicator)
    
    # * FUNCTION TO RUN THE ENGINE
    def run(self, timeframe: int):
        '''
        Runs the engine.
        '''

        # ! VALIDATE STRATEGIES
        if (len(self.strategies) == 0):
            print("No strategy fed in the engine.")
            return
        
        if (len(self.indicators) == 0):
            print("No indicator fed in the engine.")
            return
        
        # & ENGINE STARTING INFO STATEMENTS
        for strategy in self.strategies:
            print(f"Fed strategy {strategy.NAME}")

        for indicator in self.indicators:
            print(f"Added indicator {indicator.NAME}")
        
        print(f"\nStreaming live ticks for {self.symbol}.")
        print("Press ctrl+C to stop...\n")

        # & STREAM LOOP
        while (True):
            try:
                # FETCH LATEST CANDLE'S TIME
                candle = self.service.get_history(
                    self.symbol, timeframe, 1
                ).iloc[-1]

                current_candle_time = candle['time']

                # CHECK IF LAST SAVED CANDLE IS CLOSED
                if (current_candle_time != self.last_candle_time):
                    self.last_candle_time = current_candle_time

                    print(
                        f"New M{timeframe} candle:",
                        f"{datetime.fromtimestamp(current_candle_time)}"
                    )

                    # FETCH LAST 200 CANDLES TO ANALYZE
                    df = self.service.get_history(self.symbol, timeframe, 200)

                    # ADD INDICATORS
                    for indicator in self.indicators:
                        df = indicator.calculate_values(df)

                    # ANALYZE WITH FED STRATEGIES
                    for strategy in self.strategies:
                        signal = strategy.generate_signal(df)
                        if (signal is None): continue
                        self.consensus.add_signal(signal)

                    # FINALIZE A SIGNAL
                    final_signal = self.consensus.finalize()
                    if (not final_signal): continue

                    # VALIDATE THE FINAL SIGNAL
                    validation = self.manager.validate(final_signal)

                    # IF MANAGER REJECTED
                    if (not validation.allowed):
                        print("\nSignal rejected by Risk Manager")
                        print(validation.reason, end="\n\n")

                    # EXECUTE TRADE IF MANAGER ALLOWED
                    self.service.execute_trade(signal)
                    print("\nA trade has been executed.")
                    print(signal, end="\n\n")

                time.sleep(5)

            except KeyboardInterrupt:
                print("\nStreaming interrupted by user.\n")
                return