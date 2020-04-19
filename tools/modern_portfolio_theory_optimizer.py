from core.portfolio import Portfolio
from core.modern_portfolio_theory_strategy import MPT


def mpt_customize_weights(assets_list, customize_weights, risk_free_annual_yield=None, show_details=True,
                          show_plot=False, start_date=None, end_date=None):
    """
    This function plots and calculates the portfolio performance with customized weights. Will print out the sharpe
    ratio, risk and return for the customized weights
    :param assets_list: a string list containing asset tickers
    :param customize_weights: customized weights assigned by you
    :param risk_free_annual_yield: the annual yield of a 3month T-bill. If set, MPT will do risk & sharpe ratio
     optimization, otherwise will only do risk-optimization
    :param show_detail: show details about the optimized weights output in the console
    :param show_plot: show the capital market line (if risk_free_annual_yield is set), and mean-std curve
    (efficient frontier), do not recommend to use when optimizing more than 4 assets -- will be slow in plotting
    :param start_date: set a specific date to start investing, will determine when the price history data will start
    :param end_date: set a specific date to end investing, this will determine when the price history data will end
    :return:
    """
    ptf = Portfolio()
    mpt = MPT(risk_free_annual_yield=risk_free_annual_yield)
    show_plots_for_less_than_three_assets = True if len(assets_list) <= 3 else False
    show_plots_for_less_than_three_assets = True if len(assets_list) <= 3 else False
    if start_date and end_date is None:
        ptf.invest(assets_list, mpt, customized_weights=customize_weights, period="max", show_details=show_details,
                   show_plot=show_plot or show_plots_for_less_than_three_assets)
    else:
        ptf.invest(assets_list, mpt, customized_weights=customize_weights, period="max", start_date=start_date,
                   end_date=end_date, show_details=show_details,
                   show_plot=show_plot or show_plots_for_less_than_three_assets)


def mpt_optimization(assets_list, risk_free_annual_yield=None, show_details=True, show_plot=False,
                     start_date=None, end_date=None):
    """
    This function uses the modern portfolio theory to optimize the portfolio.
    :param assets_list: a string list containing asset tickers
    :param risk_free_annual_yield: the annual yield of a 3month T-bill. If set, MPT will do risk & sharpe ratio
     optimization, otherwise will only do risk-optimization
    :param show_detail: show details about the optimized weights output in the console
    :param show_plot: show the capital market line (if risk_free_annual_yield is set), and mean-std curve
    (efficient frontier), do not recommend to use when optimizing more than 4 assets -- will be slow in plotting
    :param start_date: set a specific date to start investing, will determine when the price history data will start
    :param end_date: set a specific date to end investing, this will determine when the price history data will end
    """
    ptf = Portfolio()
    mpt = MPT(risk_free_annual_yield=risk_free_annual_yield)
    show_plots_for_less_than_three_assets = True if len(assets_list) <= 3 else False
    if start_date and end_date is None:
        ptf.invest(assets_list, mpt, period="max", show_details=show_details,
                   show_plot=show_plot or show_plots_for_less_than_three_assets)
    else:
        ptf.invest(assets_list, mpt, period="max", start_date=start_date, end_date=end_date, show_details=show_details,
                   show_plot=show_plot or show_plots_for_less_than_three_assets)


def mpt_evaluation(assets_list, risk_free_annual_yield=None):
    """
    This function evaluates how MPT works for your assets to be invested. I suggest you to do evaluation for each
    portfolio combination, to understand how MPT optimization can track the optimal solutions for your specific assets
    combo
    :param risk_free_annual_yield: I recommend to set it so as to allocate some risk-free assets.
    Its value is the annual yield of a 3month T-bill. If set, MPT will do risk & sharpe ratio
    optimization, otherwise will only do risk-optimization
    """
    ptf = Portfolio()
    mpt = MPT(risk_free_annual_yield=risk_free_annual_yield)
    mpt.portfolio = ptf
    mpt.evaluate(assets_list)