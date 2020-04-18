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
    items = ['ticker', 'market cap', 'industry', 'sector', 'current price', 'revenue growth', 'gross margin',
             'net profit margin', 'free cash flow margin', 'return on total assets', 'R&D expense', 'SG&A expenses',
             'interest rate paid', 'income tax rate', 'cash turnover days', 'receivables turnover days',
             'inventory turnover days', 'total current assets turnover days', 'fixed assets turnover days',
             'total assets turnover days', 'current ratio', 'acid-test ratio', 'times interest earned',
             'liability/asset ratio', 'wacc', 'roic', 'excess return', 'economic profit', 'dividend yield',
             'dividend payout ratio']
    with open(file_path, 'w') as fp:
        fp.write('\t'.join(items)+"\n")
        tickers_failed = []
        for result in p.imap(company_scraping_worker, [[ticker, risk_free_return, market_return, quarter] for
                                                       ticker in ticker_list]):
            if len(result) <= 5:
                tickers_failed.append(result)
            else:
                fp.write(result)
        print(f"failed tickers={tickers_failed}")


def company_scraping_worker(args):
    """
    This is a helper function to parallize the company information scraping.
    :param args: a list of four arguments: [ticker, risk_free_return, market_return, quarter]
    :return: the ticker if cannot scrape, or scraping info if can scrape
    """
    c = Company(args[0], quarter=args[3])
    try:
        t0 = time.clock()
        data = c.serilize_company_investment_info(args[1], args[2])
        print(f"- {args[0]} scraping done, takes {round(time.clock() - t0, 2)} seconds")
        return data
    except Exception:
        print(f"cannot scrape {args[0]}")
        return args[0]



