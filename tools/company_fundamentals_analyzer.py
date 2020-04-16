from core.company import *


def analyze_company(ticker, risk_free_return, market_return, quarter=False):
    """
    This function analyzes one company's fundamentals
    :param ticker: company stock ticker
    :param risk_free_return: the 3-month t-bill return
    :param market_return: S&P 500 last 5 year compound average return
    :param quarter: whether to see it's quarter report. If false, will see its annual report
    :return:
    """
    c = Company(ticker, quarter=quarter)
    c.print_balance_sheet()
    c.print_income_statements()
    c.print_cashflow_statements()
    c.get_profitability_insights()
    c.get_operating_insights()
    c.get_solvency_insights()
    c.get_investment_insights(risk_free_return=risk_free_return, market_return=market_return)