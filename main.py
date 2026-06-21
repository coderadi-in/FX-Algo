'''
Orchestrates everything.
The lobby of whole game.
'''

# ? IMPORTS
from back_testing.engine import BackTestingEngine
from back_testing.analytics import BackTestingAnalytics

from risk.risk_manager import RiskManager
from account.account_service import AccountService
from strategies.ema import EMA_Strategy
from indicators.ema import EMA_Indicator
from services.mt5_service import MT5Service
import pandas as pd
import MetaTrader5 as mt5


# & STATES
SYMBOL = "XAUUSD"
DATA = pd.read_csv("data/xauusd_m30_ema.csv")

# & INITS
account = AccountService(15_000)
manager = RiskManager(account)
strategy = EMA_Strategy(8, 33, 0.05)
strategy.symbol = SYMBOL

engine = BackTestingEngine(
    account=account,
    manager=manager,
    strategy=strategy,
    data=DATA,
    symbol=SYMBOL
)

# & EXECUTION
engine.run_optimistic_simulation()
analytics = pd.DataFrame(engine.trades)
analytics.to_csv('data/analytics_xauusd.csv')

analyzer = BackTestingAnalytics(engine)
summary = analyzer.analyze_trades()

print(summary)
analyzer.generate_equity_curve()