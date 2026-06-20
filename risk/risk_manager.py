'''
Manages the risk management class.
'''

# ? IMPORTS
from models.signal import Signal
from account.account_service import AccountService
from .validation import Validation
from datetime import datetime, date, UTC


# & CLASS INIT
class RiskManager:
    '''
    Risk Management for the Engine.
    '''

    # * CONSTRUCTOR
    def __init__(self, account: AccountService):
        self.account = account
        self.MAX_DAILY_LOSS = 2
        self.MAX_DAILY_TRADES = 3
        self.RISK_PER_TRADE = 0.005
        self.WEEKEND_TRADING = False
        self.POSITION_PER_SYMBOL = 1
        self.MAX_SL_SIZE = 25

    # * FUNCTION TO CALCULATE LOT SIZE
    def calculate_lot_size(self, symbol_info: dict, sl:float, pip_value:float):
        risk_amount = self.account.balance * self.RISK_PER_TRADE
        calc_lot_size = round(risk_amount / (sl * pip_value), 3)

        min_lot = symbol_info.get('volume_min')
        lot_step = symbol_info.get('volume_step')

        lot_size = round(calc_lot_size / lot_step) * lot_step
        final_value = max(min_lot, lot_size)

        return final_value

    # * FUNCTION TO VALIDATE TRADE
    def validate(self, signal: Signal) -> Validation:
        '''
        Validates the trade based on the risk management rules.
        '''

        # VALIDATE RISK
        if (signal.risk > self.account.balance * self.RISK_PER_TRADE):
            exceeded = signal.risk - (self.account.balance * self.RISK_PER_TRADE)
            return Validation(
                allowed=False,
                reason=f"Max risk per trade exceeded by {exceeded} USD/PIPs",
                signal=signal
            )
        
        # VALIDATE WEEKEND TRADING
        if (
            not self.WEEKEND_TRADING and
            datetime.fromtimestamp(signal.entry_time, UTC).weekday() == 5
        ):
            return Validation(
                allowed=False,
                reason="Weekend trading is not allowed",
                signal=signal
            )
        
        # VALIDATE OPEN POSITIONS
        if (self.account.open_positions.get(signal.symbol) is not None):
            return Validation(
                allowed=False,
                reason=f"A position is already open in {signal.symbol}.",
                signal=signal
            )
        
        # VALIDATE SL
        if (signal.sl > self.MAX_SL_SIZE):
            exceed = signal.sl - self.MAX_SL_SIZE
            return Validation(
                allowed=False,
                reason=f"Max SL size exceeded by {exceed} USD/PIP.",
                signal=signal
            )
        
        # DAILY LEVEL VALIDATION
        if (datetime.fromtimestamp(signal.entry_time, UTC).date() == date.today()):

            today_trades = self.account.get_current_date_trades()
            loosing_trades = 0
            
            # VALIDATE DAILY LOSS LIMIT
            for trade in today_trades:
                if (trade['profit'] < 0):
                    loosing_trades += 1

            if (loosing_trades >= self.MAX_DAILY_LOSS):
                return Validation(
                    allowed=False,
                    reason="Daily loss limit exceeded.",
                    signal=signal
                )


            # VALIDATE DAILY TRADE LIMIT
            if (len(today_trades) >= self.MAX_DAILY_TRADES):
                return Validation(
                    allowed=False,
                    reason="Daily trades limit reached.",
                    signal=signal
                )
            
        return Validation(
            allowed=True,
            reason=None,
            signal=signal
        )