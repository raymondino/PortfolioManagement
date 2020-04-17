from core.company import *
import time


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


def scrape_company_fundamentals(ticker_list, file_path, risk_free_return, market_return, quarter=False):
    """
    This function scrapes all the companies in the ticker_list for financial data and save to tsv file.
    :param ticker: company stock ticker
    :param risk_free_return: the 3-month t-bill return
    :param market_return: S&P 500 last 5 year compound average return
    :param quarter: whether to see it's quarter report. If false, will see its annual report
    :return:
    """
    with open(file_path, 'w') as fp:
        fp.write("ticker\tindustry\trevenue growth\tgross margin\tnet profit margin\tfree cash flow margin\t"
                 "return on total assets\tR&D expenses\tSG&A expenses\tinterest rate paid\tincome tax rate\t"
                 "cash turnover days\treceivables turnover days\tinventories turnover days\t"
                 "total current assets turnover days\tfixed assets turnover days\ttotal assets turnover rate\t"
                 "total assets turnover days\tcurrent ratio\tacid-test ratio\ttimes interest earned\t"
                 "liability/asset ratio\twacc\troic\t\excess return\t economic profit\tdividend yield\t"
                 "divident payout ratio\n")
        tickers_failed = []
        for ticker in ticker_list:
            c = Company(ticker, quarter=quarter)
            try_times = 0
            while try_times < 3:
                try:
                    t0 = time.clock()
                    fp.write(c.serilize_company_investment_info(risk_free_return, market_return))
                    print(f"- {ticker} scraping done, scraping takes {round(time.clock() - t0, 2)} seconds")
                    break
                except Exception:
                    try_times += 1
                    print(f"tried to scrape {ticker} - {try_times} times")
            if try_times == 3:
                tickers_failed.append(ticker)

        print(f"failed tickers={tickers_failed}")




