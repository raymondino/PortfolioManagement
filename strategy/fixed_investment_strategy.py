from common.snapshot import Snapshot
from utils.widget import xirr
import numpy as np

# this code is not used any more

class FixedInvestmentStrategy():
    def __init__(self):
        self.fixed_investment_amount = 0
        self.enable_rebalance = False
        self.rebalance_offset = 0.15
        self.snapshots = []
        self.portfolio = None
        self.final_book_value = 0
        self.total_investment = 0
        self.annual_return = 0
        self.monthly_return = 0
        self.asset_risk = 0
        self.book_risk = 0
        self.book_gain_risk = 0
        self.customized_risk = 0
        self.sharpe_ratio_based_on_asset_risk = 0
        self.sharpe_ratio_based_on_book_risk = 0
        self.sharpe_ratio_based_on_book_gain_risk = 0
        self.sharpe_ratio_based_on_customized_risk = 0
        self.rebalance_times = 0

    def fit(self, portfolio, show_details, hide_log_during_optimization=False):
        self.snapshots = []  # clear snapshots at each fit
        if len(portfolio.assets) == 0:
            return
        self.portfolio = portfolio
        for i in range(0, portfolio.full_asset_price_history.shape[0]):
            self.snapshots.append(
                Snapshot(portfolio.asset_weights, (None if i == 0 else self.snapshots[-1]),
                         portfolio.full_asset_price_history.iloc[i],
                         self.enable_rebalance, self.rebalance_offset, self.fixed_investment_amount))

        # the last day: only vest, no invest
        self.final_book_value = self.snapshots[-1].book_value + self.snapshots[-1].money_invested
        self.total_investment = self.snapshots[-2].total_investment  # the last day: only vest, no invest
        self.monthly_return = self.__get_monthly_return_rate()
        self.asset_risk = self.__get_asset_risk()
        self.book_risk = self.__get_book_risk()
        self.book_gain_risk = self.__get_book_gain_risk()
        self.customized_risk = self.__get_customized_risk()
        self.sharpe_ratio_based_on_asset_risk = self.monthly_return / self.asset_risk
        self.sharpe_ratio_based_on_book_risk = self.monthly_return / self.book_risk
        self.sharpe_ratio_based_on_book_gain_risk = self.monthly_return / self.book_gain_risk
        self.sharpe_ratio_based_on_customized_risk = self.monthly_return / self.customized_risk
        self.rebalance_times = sum([0 if s.rebalanced == "[NOT]" else 1 for s in self.snapshots])
        if not hide_log_during_optimization:
            self.report(show_details)

    def __get_monthly_return_rate(self):
        def generate_cashflow_over_investment_date():
            """
            This is a helper function to generate cash flows for each snapshot. Each snapshot contains the investment
            amount (the cash flow for that investment behavior), and an investment date. This cash flow will be used to
            calculate the average return using XIRR
            :return: a list of tuples (datetime, money) as cash flows
            """
            cashflow = []
            if self.snapshots is None or len(self.snapshots) == 0:
                return cashflow

            # collect all previous invested money and investment date, except the last date.
            # assume at the last date, you will vest all your money. We will use the last snapshot's date,
            # the vested value will be calculated as the last date's book_value minus the investment_amount.
            for i in range(0, len(self.snapshots) - 1):
                cashflow.append((self.snapshots[i].snapshot_datetime, self.snapshots[i].money_invested))

            # take care of the last cash flow, which is a vested value (the book_value before the last investment)
            cashflow.append((self.snapshots[len(self.snapshots) - 1].snapshot_datetime,
                             self.snapshots[len(self.snapshots) - 1].book_value +  # yes, it's +
                             self.snapshots[len(self.snapshots) - 1].money_invested))  # remember money_invested is negative
            return cashflow
        self.annual_return = xirr(generate_cashflow_over_investment_date())
        return pow(self.annual_return, 1/12) if self.annual_return >= 0 else -1*pow(-1*self.annual_return, 1/12)

    def __get_asset_risk(self):
        """
        This function returns the risk calculated by the asset price change covariance.
        risk = [weights1] * asset_covariance_matrix * transpose([weights]), where [weights] is a row vector
        :return: risk defined by the covariance of assets
        """
        return np.matmul(np.matmul(np.array(self.portfolio.asset_weights), self.portfolio.get_assets_covariance().to_numpy()), np.array(self.portfolio.asset_weights).transpose())

    def __get_book_risk(self):
        """
        This is the standard deviation of book value changes over time
        :return: standarad deviation of book value changes
        """
        book_value_change=[]
        for i in range(1, len(self.snapshots)):
            book_value_change.append(self.snapshots[i].book_value / self.snapshots[i-1].book_value - 1)
        return np.std(book_value_change)

    def __get_book_gain_risk(self):
        """
        This is the standard deviation of book gain changes over the time
        :return: standard deviation of the book gain changes
        """
        book_value_gain_change = []
        for i in range(1, len(self.snapshots)):
            book_value_gain_change.append(0 if self.snapshots[i-1].book_value == self.snapshots[i-1].total_investment
                                     else (self.snapshots[i].book_value - self.snapshots[i].total_investment) /
                                     (self.snapshots[i-1].book_value - self.snapshots[i-1].total_investment) - 1)
        return np.std(book_value_gain_change)

    def __get_customized_risk(self):
        """
        Use the monthly annual return as the expected value, and do standard deviation for monthly book value changes
        :return: a customized risk
        """
        monthly_rate = self.__get_monthly_return_rate()
        variance = 0
        for i in range(1, len(self.snapshots)):
            variance += (monthly_rate - (self.snapshots[i].book_value / self.snapshots[i-1].book_value - 1))**2
        return pow(variance, 1/2)/(len(self.snapshots)-1)

    def print_investment_history(self):
        print("=========================================")
        print("Date\tBook\tGain\tRebalance\tasset shares\tasset values")
        for snapshot in self.snapshots:
            print(f"{snapshot.snapshot_datetime}\t{snapshot.book_value}\t{snapshot.book_value-snapshot.total_investment}"
                  f"\t{snapshot.rebalanced}\t{snapshot.assets_final_share}\t{snapshot.assets_value}")

    def report(self, show_details=False):
        print(f"asset tickers                  : {[a.ticker for a in self.portfolio.assets]}")
        print(f"asset weights                  : {['%.2f' % item for item in self.portfolio.asset_weights]}")
        print(f"book value                     : {'%.2f' % self.final_book_value}")
        print(f"total investment               : {'%.2f' % self.total_investment}")
        print(f"average annual return          : {'%.2f' % (self.annual_return*100)}%")
        print(f"average monthly return         : {'%.2f' % (self.monthly_return*100)}%")
        print(f"asset risk (monthly)           : {'%.6f' % self.asset_risk}")
        print(f"book risk (monthly)            : {'%.6f' % self.book_risk}")
        print(f"book gain risk (monthly)       : {'%.6f' % self.book_gain_risk}")
        print(f"customized risk (monthly)      : {'%.6f' % self.customized_risk}")
        print(f"sharpe (asset risk monthly)    : {'%.2f' % self.sharpe_ratio_based_on_asset_risk}")
        print(f"sharpe (book risk monthly)     : {'%.2f' % self.sharpe_ratio_based_on_book_risk}")
        print(f"sharpe (book gain risk monthly): {'%.2f' % self.sharpe_ratio_based_on_book_gain_risk}")
        print(f"sharpe (customized risk)       : {'%.2f' % self.sharpe_ratio_based_on_customized_risk}")
        print(f"rebalance times                : {self.rebalance_times}")
        print(f"rebalance offset               : {self.rebalance_offset}")
        if show_details:
            self.print_investment_history()