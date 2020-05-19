from core.portfolio import *
import numpy as np
import quantstats as qs
import matplotlib.pyplot as plt
from scipy.optimize import minimize


class AverageCostStrategy:
    def __init__(self, portfolio_name, risk_free_yearly_return, report_path, initial_fund, fixed_investment_fund,
                 fixed_investment_interval=20, rebalance_interval=20, rebalance_use_data=-1):
        self.portfolio_name = portfolio_name
        self.risk_free_daily_return = pow(1 + risk_free_yearly_return, 1/365) -1
        self.report_path = report_path
        self.initial_fund = initial_fund
        self.fixed_investment_fund = fixed_investment_fund
        self.fixed_investment_interval = fixed_investment_interval
        self.rebalance_inverval = rebalance_interval
        self.rebalance_use_data = rebalance_use_data
        self.total_cost = 0
        self.daily_book_value = []
        self.daily_book_value_change = []
        self.portfolio = None
        self.accumulated_book_value_diff_due_to_rebalance = 0

    def fit(self, portfolio, customized_weights=None, show_details=False, show_plot=False):
        print(f"investing: {[a.ticker for a in portfolio.assets]}")

        self.portfolio = portfolio
        cur_weights = customized_weights if customized_weights is not None else self.portfolio.asset_weights
        fund_for_each_asset = [w * self.initial_fund for w in cur_weights]
        cur_shares = np.around(pd.Series(fund_for_each_asset, index=self.portfolio.full_asset_price_history.columns) / self.portfolio.full_asset_price_history.iloc[0])
        self.total_cost += (cur_shares * self.portfolio.full_asset_price_history.iloc[0]).sum()

        for i in range(len(self.portfolio.full_asset_price_history)):
            rebalanced_shares = cur_shares
            if i > 0 and i % self.rebalance_inverval == 0:
                if self.rebalance_use_data == -1:
                    cur_weights = self.__rebalance(self.portfolio.full_asset_price_history_change[0:i - 1])
                else:
                    cur_weights = self.__rebalance(self.portfolio.full_asset_price_history_change[i - self.rebalance_use_data:i - 1])
                cur_book_value = self.daily_book_value[-1].sum()
                rebalanced_fund_for_each_asset = [cur_book_value * w for w in cur_weights]
                rebalanced_shares = np.around(pd.Series(rebalanced_fund_for_each_asset, index=self.portfolio.full_asset_price_history.columns) / self.portfolio.full_asset_price_history.iloc[i])
                rebalanced_book_value = (rebalanced_shares * self.portfolio.full_asset_price_history.iloc[i]).sum()
                self.accumulated_book_value_diff_due_to_rebalance += cur_book_value - rebalanced_book_value
                print(f"[REBALANCE] {self.portfolio.full_asset_price_history.index[i].strftime('%Y-%m-%d')}:{cur_shares.values.tolist()} ${round(cur_book_value, 2)} to {rebalanced_shares.values.tolist()} ${round(rebalanced_book_value, 2)}")

            if i > 0 and i % self.fixed_investment_interval == 0:
                fixed_investment_fund_for_each_asset = [w * self.fixed_investment_fund for w in cur_weights]
                new_shares = np.around((pd.Series(fixed_investment_fund_for_each_asset, index=self.portfolio.full_asset_price_history.columns) / self.portfolio.full_asset_price_history.iloc[i]))

                self.total_cost += (new_shares * self.portfolio.full_asset_price_history.iloc[i]).sum()
                cur_shares = rebalanced_shares + new_shares
                self.daily_book_value.append(cur_shares * self.portfolio.full_asset_price_history.iloc[i])
                self.daily_book_value_change.append(self.daily_book_value[-1].sum()/(self.daily_book_value[-2].sum() + self.fixed_investment_fund) - 1)
            else:
                self.daily_book_value.append(cur_shares * self.portfolio.full_asset_price_history.iloc[i])
                if i > 0:
                    self.daily_book_value_change.append(self.daily_book_value[-1].sum()/self.daily_book_value[-2].sum() - 1)

        self.daily_book_value_change = pd.Series(self.daily_book_value_change)
        print("======Average Cost Strategy========")
        print(f"total cost: {round(self.total_cost,2)}")
        print(f"total value: {round(self.daily_book_value[-1].sum(), 2)}")
        print(f"total accumulated gain/loss due to rebalance: {round(self.accumulated_book_value_diff_due_to_rebalance, 2)}")
        print(f"gain: {round(self.daily_book_value[-1].sum() - self.total_cost, 2)}")
        print(f"annualized return = {round(self.daily_book_value_change.mean() * 252, 6)}")
        print(f"annualized risk = {round(self.daily_book_value_change.std()*pow(252, 1/2), 6)}")
        print(f"annualized sharpe = {round(pow(252, 1/2)*self.daily_book_value_change.mean()/ self.daily_book_value_change.std(), 6)}")
        if show_plot:
            pd.DataFrame(self.daily_book_value, index=self.portfolio.full_asset_price_history.index).sum(axis=1).plot(title=f"{self.portfolio_name} book value history")
            plt.show()
        self.daily_book_value_change.index = self.portfolio.full_asset_price_history_change.index
        qs.reports.html(self.daily_book_value_change, "IVV", title=f"{self.portfolio_name} average cost", output=self.report_path, rf=self.risk_free_daily_return)

    def __rebalance(self, asset_price_history_change, target_risk=None):
        def sharpe_ratio(param):
            daily_mean_return = np.matmul(param, asset_price_history_change.mean().to_numpy().transpose())
            daily_risk = np.sqrt(np.matmul(np.matmul(param, self.portfolio.get_assets_covariance().to_numpy()), param.transpose()))
            return -1 * (daily_mean_return - self.risk_free_daily_return) / daily_risk
        param = np.array([1/len(asset_price_history_change)] * len(asset_price_history_change.columns))
        bnds = tuple([(0, 1)] * (len(param)))
        cons = [{'type': 'eq', 'fun': lambda param: np.sum(param) - 1}]
        if target_risk is not None:
            cons.append({'type':'eq', 'fun':lambda param: np.sqrt(np.matmul(np.matmul(param, asset_price_history_change.cov().to_numpy()), param.transpose())) - target_risk/np.sqrt(252)})
        ans = minimize(sharpe_ratio, param, bounds=bnds, constraints=cons)
        return ans.x




