from strategy.fixed_investment_strategy import FixedInvestmentStrategy
from scipy.optimize import minimize
import numpy as np


def optimize_sharpe_ratio_based_on_customized_risk(portfolio, investing_strategy):
    def sharpe_ratio(param):
        portfolio.asset_weights = param[0:-1]
        investing_strategy.rebalance_offset = param[-1]
        investing_strategy.fit(portfolio, False, hide_log_during_optimization=True)
        return -1 * investing_strategy.sharpe_ratio_based_on_customized_risk

    param = [1/len(portfolio.asset_weights)]*len(portfolio.asset_weights)
    param.append(investing_strategy.rebalance_offset)
    bnds = tuple([(0, 1)] * (len(param)))
    cons = ({'type': 'eq', 'fun': lambda param: np.sum(param[:-1]) - 1})
    ans = minimize(sharpe_ratio, param, bounds=bnds, constraints=cons)
    portfolio.asset_weights = ans.x[:-1]
    investing_strategy.rebalance_offset = ans.x[-1]
    print("=========optimize_sharpe_ratio_based_on_customized_risk==========")
    portfolio.using_strategy(investing_strategy, show_details=False)


def optimize_sharpe_ratio_based_on_book_gain_risk(portfolio, investing_strategy):
    def sharpe_ratio(param):
        portfolio.asset_weights = param[0:-1]
        investing_strategy.rebalance_offset = param[-1]
        investing_strategy.fit(portfolio, False, hide_log_during_optimization=True)
        return -1 * investing_strategy.sharpe_ratio_based_on_book_gain_risk

    param = [1/len(portfolio.asset_weights)]*len(portfolio.asset_weights)
    param.append(investing_strategy.rebalance_offset)
    bnds = tuple([(0, 1)] * (len(param)))
    cons = ({'type': 'eq', 'fun': lambda param: np.sum(param[:-1]) - 1})
    ans = minimize(sharpe_ratio, param, bounds=bnds, constraints=cons)
    portfolio.asset_weights = ans.x[:-1]
    investing_strategy.rebalance_offset = ans.x[-1]
    print("=========optimize_sharpe_ratio_based_on_book_gain_risk==========")
    portfolio.using_strategy(investing_strategy, show_details=False)


def optimize_sharpe_sharpe_ratio_based_on_book_risk(portfolio, investing_strategy):
    def sharpe_ratio(param):
        portfolio.asset_weights = param[0:-1]
        investing_strategy.rebalance_offset = param[-1]
        investing_strategy.fit(portfolio, False, hide_log_during_optimization=True)
        return -1 * investing_strategy.sharpe_ratio_based_on_book_risk

    param = [1/len(portfolio.asset_weights)]*len(portfolio.asset_weights)
    param.append(investing_strategy.rebalance_offset)
    bnds = tuple([(0, 1)] * (len(param)))
    cons = ({'type': 'eq', 'fun': lambda param: np.sum(param[:-1]) - 1})
    ans = minimize(sharpe_ratio, param, bounds=bnds, constraints=cons)
    portfolio.asset_weights = ans.x[:-1]
    investing_strategy.rebalance_offset = ans.x[-1]
    print("=========optimize_sharpe_sharpe_ratio_based_on_book_risk==========")
    portfolio.using_strategy(investing_strategy, show_details=False)


def optimize_sharpe_sharpe_ratio_based_on_asset_risk(portfolio, investing_strategy):
    def sharpe_ratio(param):
        portfolio.asset_weights = param[0:-1]
        investing_strategy.rebalance_offset = param[-1]
        investing_strategy.fit(portfolio, False, hide_log_during_optimization=True)
        return -1 * investing_strategy.sharpe_ratio_based_on_asset_risk

    param = [1/len(portfolio.asset_weights)]*len(portfolio.asset_weights)
    param.append(investing_strategy.rebalance_offset)
    bnds = tuple([(0, 1)] * (len(param)))
    cons = ({'type': 'eq', 'fun': lambda param: np.sum(param[:-1]) - 1})
    ans = minimize(sharpe_ratio, param, bounds=bnds, constraints=cons)
    portfolio.asset_weights = ans.x[:-1]
    investing_strategy.rebalance_offset = ans.x[-1]
    print("=========optimize_sharpe_sharpe_ratio_based_on_asset_risk==========")
    portfolio.using_strategy(investing_strategy, show_details=False)
