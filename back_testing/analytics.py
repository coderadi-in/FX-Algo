'''
Manages the back testing analytics.
Used to analyze back tested report.
'''

# ? IMPORTS
from .engine import BackTestingEngine
import matplotlib.pyplot as plt
import pandas as pd


# & CLASS INIT
class BackTestingAnalytics:
    '''
    Analyzes a back tested report and gives a summary.
    '''

    # * CONSTRUCTOR
    def __init__(self, engine: BackTestingEngine):
        self.engine = engine

    # * FUNCTION TO GENERATE EQUITY CURVE
    def generate_equity_curve(self):
        '''
        Generates a minimal equity curve of all trades.
        '''

        df = pd.DataFrame(self.engine.trades)

        plt.figure(figsize=(8, 5))

        x = list(range(1, len(self.engine.trades)+1))
        y = df['profit'].cumsum()

        plt.plot(x, y)
        plt.show()

    # * FUNCTION TO ANALYZE TRADE HISTORY
    def analyze_trades(self):
        '''
        Analyzes the trades history and provided concise summary.
        '''

        df = pd.DataFrame(self.engine.trades)
        total_trades = len(df)

        winning_trades = df[df['profit'] > 0]
        loosing_trades = df[df['profit'] < 0]

        wins = len(winning_trades)
        losses = len(loosing_trades)

        win_rate = wins / total_trades
        loss_rate = losses / total_trades

        average_win = winning_trades['profit'].mean()
        average_loss = loosing_trades['profit'].mean()

        largest_win = max(winning_trades['profit'])
        largest_loss = min(loosing_trades['profit'])

        net_profit = df['profit'].sum()
        profit_factor = winning_trades['profit'].sum() / abs(loosing_trades['profit'].sum())
        expectancy = (
            (wins / total_trades) * average_win +
            (losses / total_trades) * average_loss
        )

        return pd.Series(
            [
                total_trades, wins, losses, win_rate, loss_rate, net_profit,
                average_win, average_loss, profit_factor, largest_win, largest_loss, expectancy, self.engine.account.balance
            ],
            index=[
                "Total Trades", "Wins", "Losses", "Win Rate (%)", "Loss Rate (%)", "Net Profit",
                "Average Win", "Average Loss", "Profit Factor", "Largest Win", "Largest Loss", "Expectancy", "Balance"
            ]
        )