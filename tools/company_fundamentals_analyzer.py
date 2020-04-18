from core.company import *
import time
import multiprocessing


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
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    with open(file_path, 'w') as fp:
        fp.write("ticker\tmarket cap\tindustry\tsector\tcurrent price\trevenue growth\tgross margin\tnet profit margin\t"
                 "free cash flow margin\treturn on total assets\tR&D expenses\tSG&A expenses\tinterest rate paid\t"
                 "income tax rate\tcash turnover days\treceivables turnover days\tinventories turnover days\t"
                 "total current assets turnover days\tfixed assets turnover days\t"
                 "total assets turnover days\tcurrent ratio\tacid-test ratio\ttimes interest earned\t"
                 "liability/asset ratio\twacc\troic\t\excess return\t economic profit\tdividend yield\t"
                 "dividend payout ratio\n")
        tickers_failed = []
        for result in p.imap(compane_scraping_workder, [[ticker, risk_free_return, market_return, quarter] for ticker in ticker_list]):
            if len(result) <= 5:
                tickers_failed.append(result)
            else:
                fp.write(result)

        print(f"failed tickers={tickers_failed}")


def compane_scraping_workder(args):
    c = Company(args[0], quarter=args[3])
    try:
        t0 = time.clock()
        data = c.serilize_company_investment_info(args[1], args[2])
        print(f"- {args[0]} scraping done, scraping takes {round(time.clock() - t0, 2)} seconds")
        return data
    except Exception:
        print(f"tried to scrape {args[0]}")
        return args[0]



