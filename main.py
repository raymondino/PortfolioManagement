from tools.mpt_optimizer import *


if __name__ == "__main__":

    """
    fill in the tickers of the assets you would like to invest in, as many as you want.
    """
    assets_list = ["MSFT", "GLD", "FB", "GOOG"]

    """
    uncomment this line only to optimize the portfolio without risk free asset
    results will be output in console
    """
    # mpt_optimization(assets_list)

    """
    uncomment this line only to optimize the portfolio with risk free asset
    results will be output in console. Get risk_free_annual_yield from:
    https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield
    """
    mpt_optimization(assets_list, risk_free_annual_yield=0.009)

    """
    uncomment this line only to evaluate MPT for your portfolio
    when evaluating, you should observe if the risk or sharpe ratio tracks closely with the ground truth. The plots of 
    returns are intended to provide you return info, should not be used as a metric to judge MPT performance.
    """
    # mpt_evaluation(assets_list, risk_free_annual_yield=0.09)
