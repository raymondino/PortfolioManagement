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
    c.print_financials()
    c.get_insights(risk_free_return, market_return)


def compare_companies(ticker_list, risk_free_return, market_return, quarter=False):
    """
    This function compares multiple companies' fundamentals, by comparing the latest report and 10 year mean
    :param ticker: company stock ticker
    :param risk_free_return: the 3-month t-bill return
    :param market_return: S&P 500 last 5 year compound average return
    :param quarter: whether to see it's quarter report. If false, will see its annual report
    :return:
    """
    all_companies_insights = []
    for ticker in ticker_list:
        c = Company(ticker, quarter=quarter)
        all_companies_insights.append(c.get_insights_summary(risk_free_return, market_return))

    Company.print_table_title(f"{ticker_list} Comparision")
    print(pd.concat(all_companies_insights, axis=1).applymap(mix_number).to_string())

