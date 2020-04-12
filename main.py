from tools.mpt_optimizer import *
from common.company import *


def mpt_optimization():
    """
    fill in the tickers of the assets you would like to invest in, as many as you want.
    """
    # assets_list = ["VGLT", "BLV", "GLD", "MSFT", "SPY"]
    assets_list = ["QQQ", "SQQQ", "MSFT"]
    # p = Portfolio()
    #
    # p.invest(assets_list)
    # p.plot_asset_correlation()

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
    # mpt_optimization(assets_list, risk_free_annual_yield=0.009)

    """
    uncomment this line only to evaluate MPT for your portfolio
    when evaluating, you should observe if the risk or sharpe ratio tracks closely with the ground truth. The plots of 
    returns are intended to provide you return info, should not be used as a metric to judge MPT performance.
    """
    mpt_evaluation(assets_list, risk_free_annual_yield=0.09)


def company_fundamental_analysis():

    """
    get fundamental analysis for a company
    """
    # a_company = Company("MSFT")
    # a_company.analyze_profitability(show_plot=False)
    # a_company.analyze_operational_capability(show_plot=False)
    # a_company.analyze_solvency(show_plot=False)
    # a_company.analyze_extreme_situations(show_plot=False)
    # a_company.analyze_investment_value(risk_free_return=0.0025, latest_five_years_stock_market_return=0.0668)

    """
    choose companies to invest based on their excess return
    """
    company_tickers_list = ["MSFT", "AAPL", "V", "INTC", "MA", "CSCO", "ADBE", "NVDA", "CRM", "ORCL", "PYPL", "ACN",
                            "IBM", "AVGO", "TXN", "QCOM", "FIS", "INTU", "ADP", "FISV", "NOW", "MU", "AMD", "AMAT",
                            "CASH"]
    # company_tickers_list = ["EQIX", "CCI", "AMT", "CCOI", "COR", "DLR", "QTS", "CONE", "SBAC", "GDS"]
    Company.choose_stock_based_on_excess_return(company_tickers_list, risk_free_return=0.0025,
                                                latest_five_years_stock_market_return=0.0668)


if __name__ == "__main__":
    company_fundamental_analysis()