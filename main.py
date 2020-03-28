from common.portfolio import Portfolio
from common.strategy import FixedInvestmentStrategy
from utils.optimizer import *

s = FixedInvestmentStrategy()
s.fixed_investment_amount = 1500
s.enable_rebalance = True
p = Portfolio()

# adjust time in Asset class. Make sure all stocks exist at the start time. Or just set period="max"

# optimization
# p.invest(["AAPL", "CCL"])
# optimize_sharpe_sharpe_ratio_based_on_asset_risk(p, s)
# optimize_sharpe_sharpe_ratio_based_on_book_risk(p, s)
# optimize_sharpe_ratio_based_on_book_gain_risk(p, s)
# optimize_sharpe_ratio_based_on_customized_risk(p, s)

# validation
# p.asset_weights = [0.00, 0.00, 0.06, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.68, 0.26, 0.00]
# p.invest(["AAPL", "AMT", "AMZN", "CCI", "DAL", "DIS", "EQIX", "FB", "GOOG", "IVV", "NFLX", "TSLA", "MSFT"]).using_strategy(s, show_details=True)

# plot correlation
# p.invest(["AAPL", "AMT", "AMZN", "CCI", "DAL", "DIS", "EQIX", "FB", "GOOG", "IVV", "NFLX", "TSLA", "MSFT"])
# p.plot_asset_correlation()

# market investment
p.invest(["CCL"]).using_strategy(s, show_details=True)