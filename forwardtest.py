'''
Orchestrates back-testing.
The lobby of whole game.
'''

# ? IMPORTS
from forward_testing.engine import ForwardTestingEngine
from risk.risk_manager import RiskManager
from consensus.consensus_engine import ConsensusEngine
from services.mt5_service import MT5Service
from account.mt5_account import MT5Account
from strategies.ema import EMA_Strategy
from indicators.ema import EMA_Indicator
import MetaTrader5 as mt5


# & CONSTANTS
SYMBOL = "XAUUSD"

# & INITS
service = MT5Service()
account = MT5Account(True)
manager = RiskManager(account)
consensus = ConsensusEngine()

strategy = EMA_Strategy(9, 21)
indicator = EMA_Indicator(9, 21)

engine = ForwardTestingEngine(
    manager, consensus, service, SYMBOL
)

engine.add_strategy(strategy)
engine.add_indicator(indicator)

engine.run(mt5.TIMEFRAME_M1)