from core.portfolio import *
import numpy as np
import quantstats as qs
import matplotlib.pyplot as plt


class AverageCostStrategy:
    def __init__(self, portfolio_name, risk_free_yearly_return, report_path, initial_fund, fixed_investment_fund,
                 allow_fractional_shares=False, fixed_investment_interval=20):
        self.portfolio_name = portfolio_name
        self.risk_free_daily_return = pow(1 + risk_free_yearly_return, 1/365) -1
        self.report_path = report_path
        self.initial_fund = initial_fund
        self.fixed_investment_fund = fixed_investment_fund
        self.allow_fractional_shares = allow_fractional_shares
        self.fixed_investment_interval = fixed_investment_interval
        self.total_cost = 0
        self.daily_book_value = []
        self.daily_book_value_change = []
        self.portfolio = None

    def fit(self, portfolio, customized_weights=None, show_details=False, show_plot=False):
        self.portfolio = portfolio
        fund_for_each_asset = [w * self.initial_fund for w in self.portfolio.asset_weights]
        cur_shares = (np.floor(pd.Series(fund_for_each_asset, index=self.portfolio.full_asset_price_history.columns) /
                              self.portfolio.full_asset_price_history.iloc[0])
                      if not self.allow_fractional_shares else
                      round((pd.Series(fund_for_each_asset, index=self.portfolio.full_asset_price_history.columns) /
                             self.portfolio.full_asset_price_history.iloc[0]), 4))
        self.total_cost += (cur_shares * self.portfolio.full_asset_price_history.iloc[0]).sum()
        for i in range(len(self.portfolio.full_asset_price_history)):
            if i > 0 and i % self.fixed_investment_interval == 0:
                fixed_investment_fund_for_each_asset = [w * self.fixed_investment_fund for w in self.portfolio.asset_weights]
                new_shares = (np.floor((pd.Series(fixed_investment_fund_for_each_asset,
                                                  index=self.portfolio.full_asset_price_history.columns) /
                                        self.portfolio.full_asset_price_history.iloc[i]))
                               if not self.allow_fractional_shares else
                               round((pd.Series(fixed_investment_fund_for_each_asset,
                                                index=self.portfolio.full_asset_price_history.columns) /
                                      self.portfolio.full_asset_price_history.iloc[i]), 4))
                self.total_cost += (new_shares * self.portfolio.full_asset_price_history.iloc[i]).sum()
                cur_shares += new_shares
                self.daily_book_value.append(cur_shares * self.portfolio.full_asset_price_history.iloc[i])
                self.daily_book_value_change.append(self.daily_book_value[-1].sum()/(self.daily_book_value[-2].sum() + self.fixed_investment_fund) - 1)
            else:
                self.daily_book_value.append(cur_shares * self.portfolio.full_asset_price_history.iloc[i])
                if i > 0:
                    self.daily_book_value_change.append(self.daily_book_value[-1].sum()/self.daily_book_value[-2].sum() - 1)
        self.daily_book_value_change = pd.Series(self.daily_book_value_change)
        print("======Average Cost Strategy========")
        print(f"total cost: {self.total_cost}")
        print(f"total value: {self.daily_book_value[-1].sum()}")
        print(f"gain: {self.daily_book_value[-1].sum() - self.total_cost}")
        print(f"annualized return = {round(self.daily_book_value_change.mean() * 252, 6)}")
        print(f"annualized risk = {round(self.daily_book_value_change.std()*pow(252, 1/2), 6)}")
        print(f"annualized sharpe = {round(pow(252, 1/2)*self.daily_book_value_change.mean()/ self.daily_book_value_change.std(), 6)}")
        if show_plot:
            pd.DataFrame(self.daily_book_value, index=self.portfolio.full_asset_price_history.index).sum(axis=1).plot(title=f"{self.portfolio_name} book value history")
            plt.show()
        self.daily_book_value_change.index = self.portfolio.full_asset_price_history_change.index
        qs.reports.html(self.daily_book_value_change, "IVV", title=f"{self.portfolio_name} average cost", output=self.report_path, rf=self.risk_free_daily_return)






