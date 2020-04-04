from common.portfolio import Portfolio
from strategy.fixed_investment_strategy import FixedInvestmentStrategy
from strategy.modern_portfolio_theory_strategy import MPT
from utils.optimizer import *


def plot_assets_correlation(assets_list):
    s = FixedInvestmentStrategy()
    s.fixed_investment_amount = 1500
    s.enable_rebalance = True
    p = Portfolio()
    p.invest(assets_list)
    p.plot_asset_correlation()


def optimize_portfolio_weights(assets_list, period="max", start_date=None, end_date=None):
    s = FixedInvestmentStrategy()
    s.fixed_investment_amount = 1500
    s.enable_rebalance = True
    p = Portfolio()
    p.invest(assets_list, period=period, start_date=start_date, end_date=end_date)
    # optimize_sharpe_sharpe_ratio_based_on_asset_risk(p, s)
    # optimize_sharpe_sharpe_ratio_based_on_book_risk(p, s)
    # optimize_sharpe_ratio_based_on_book_gain_risk(p, s)
    optimize_sharpe_ratio_based_on_customized_risk(p, s)


def validate_optimized_portfolio_weights(assets_list):
    s = FixedInvestmentStrategy()
    s.fixed_investment_amount = 1500
    s.enable_rebalance = True
    p = Portfolio()
    print("results using optimized weights for the validation history")
    p.asset_weights = [0.35, 0.35, 0, 0.3]  # to be filled after running the optimization
    p.invest(assets_list, period="max", start_date="2019-01-01", end_date="2020-01-01").using_strategy(s, show_details=False)
    print("optimized weights using the validation history")
    optimize_portfolio_weights(assets_list, period="max", start_date="2019-01-01", end_date="2020-01-01")


def optimize_portfolio_with_mpt():
    ptf = Portfolio()

    # do not allocate risk-free asset
    mpt = MPT()
    # allocate risk-free asset. please update risk_free_annual_yield each time, use 3-month T-bill annual yield rate
    # mpt = MPT(allocate_risk_free_asset=True, risk_free_annual_yield=0.009)

    # specify an investing period for optimization
    # ptf.invest(assets_list, period="max", start_date="2019-01-01", end_date="2020-01-01").using_strategy(mpt, show_details=True, show_plots=False)
    # use all the history data for optimization, show_plots=True will be slow for ploting >= 4 assets
    # ptf.invest(assets_list, period="max").using_strategy(mpt, show_details=True, show_plots=True)

    # evaluation
    mpt.portfolio = ptf
    mpt.evaluate(assets_list)


if __name__ == "__main__":
    assets_list = ["MSFT", "GLD"]

    # step 1: optimize the portfolio with a pre-set end_date. Comment line 46 before running
    # optimize_portfolio_weights(assets_list, start_date="2017-12-31", end_date='2018-12-31')

    # step 2: collect the optimized weight and fill in line 33. Then comment line 43 and run
    # validate_optimized_portfolio_weights(assets_list)

    optimize_portfolio_with_mpt()
