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

        self.CONTRACT_SIZES = {
            "XAUUSD": 100,
            "EURUSD": 100_000,
            "GBPUSD": 100_000,
            "USDJPY": 100_000,
        }

    # * FUNCTION TO CALCULATE LOT SIZE
    def calculate_lot_size(self, symbol_info: dict, sl:float):
        '''
        Calculates an ideal lot size for a trade.

        :param symbol_info: A dictionary containing the information of current symbol.
        :param sl: SL value in pips.
        '''

        risk_amount = self.account.balance * self.RISK_PER_TRADE
        calc_lot_size = round(risk_amount / (sl * symbol_info.get('trade_contract_size')), 3)

        min_lot = symbol_info.get('volume_min')
        lot_step = symbol_info.get('volume_step')

        lot_size = round(calc_lot_size / lot_step) * lot_step
        final_value = max(min_lot, lot_size)

        return final_value
    
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

    # * FUNCTION TO VALIDATE TRADE
    def validate(self, signal: Signal) -> Validation:
        '''
        Validates the trade based on the risk management rules.
        '''

        # VALIDATE RISK
        risk_amount = self.points_to_usd(signal.risk, signal.lot_size, self.CONTRACT_SIZES[signal.symbol])
        if (risk_amount > self.account.balance * self.RISK_PER_TRADE):
            exceeded = risk_amount - (self.account.balance * self.RISK_PER_TRADE)
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
        if (risk_amount > self.MAX_SL_SIZE):
            exceed = risk_amount - self.MAX_SL_SIZE
            return Validation(
                allowed=False,
                reason=f"Max SL size exceeded by {exceed} USD/PIP.",
                signal=signal
            )
        
        # DAILY LEVEL VALIDATION
        if (datetime.fromtimestamp(signal.entry_time, UTC).date() == date.today()):

            # VALIDATE DAILY TRADE LIMIT
            today_trades = self.account.get_current_date_trades()
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