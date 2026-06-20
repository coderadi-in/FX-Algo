'''
Orchestrates everything.
The lobby of whole game.
'''

# ? IMPORTS
from services.mt5_service import MT5Service
# from indicators.ema import EMA_Indicator
from strategies.ema import EMA_Strategy
from risk.risk_manager import RiskManager
from account.account_service import AccountService

import MetaTrader5 as mt5
import pandas as pd

# & INIT
account = AccountService(15_000)
data = pd.read_csv('data/eurusd_m30_ema.csv')
service = MT5Service()
strategy = EMA_Strategy(8, 33, 0.00005)
manager = RiskManager(account)
signals = []

for i in range(50, len(data)):
    current_df = data.iloc[:i]
    
    signal = strategy.generate_signal(current_df)

    if (signal is None): continue

    signals.append(signal)

    validation = manager.validate(signal)

    if (not validation.allowed):
        print(validation.reason)

    else:
        symbol_info = service.get_symbol_info("EURUSD")
        pip_value = service.get_pip_value("EURUSD")
        pip_size = service.get_pip_size("EURUSD")
        ideal_lot_size = manager.calculate_lot_size(symbol_info, signal.risk / pip_size, pip_value)

        expected_loss = (
            ideal_lot_size
            * pip_value
            * signal.risk / pip_size
        )
        print(f"Expected Loss: {expected_loss}")

        print(
            f"""
            Signal: {signal}
            Price: {signal.entry_price}
            Balance: {account.balance}
            Risk Amount: {account.balance * manager.RISK_PER_TRADE}
            SL Pips: {signal.risk / pip_size}
            Pip Value: {pip_value}
            Lot Size: {ideal_lot_size}
            """
        )

print(f"Candle count: {len(data)}")
print(f"Signals: {len(signals)}")