import time
import multiprocessing
from core.company import *
from utils.widget import *


def analyze_company(ticker, risk_free_return, quarter=False, year=5):
    """
    This function analyzes one company"s fundamentals
    :param ticker: company stock ticker
    :param risk_free_return: the 3-month t-bill return
    :param quarter: whether to see it's quarter report. If false, will see its annual report
    :param year: see data back to how many years. 5 is the default
    :return:
    """
    c = Company(ticker, quarter=quarter, year=year)
    c.print_financials()
    c.print_quantitative_analysis(risk_free_return)


def compare_companies(ticker_list, risk_free_return, quarter=False, year=5):
    """
    This function compares multiple companies" fundamentals, by comparing the latest report and 10 year mean
    :param ticker: company stock ticker
    :param risk_free_return: the 3-month t-bill return
    :param quarter: whether to see it's quarter report. If false, will see its annual report
    :param year: see data back to how many years. 5 is the default
    :return:
    """
    all_companies_insights = []
    for ticker in ticker_list:
        c = Company(ticker, quarter=quarter)
        try:
            all_companies_insights.append(c.get_fundamentals_summary(risk_free_return))
        except Exception as e:
            print(f"{ticker} cannot scrape - {e}")
    data = pd.concat(all_companies_insights, axis=1)
    mean_index = [(t, 'mean') for t in data.columns.get_level_values(0)]  # use data.columns.get_level_values(0) instead of ticker_list because there would potentially be any scraping failure for a company.
    latest_index = [(t, 'latest') for t in data.columns.get_level_values(0)]
    print_table_title(f"{ticker_list} Comparision")
    print(data.applymap(mix_number).to_string())
    print_table_title(f"{ticker_list} average of Mean")
    print(pd.DataFrame(data[mean_index].apply(pd.to_numeric, errors='coerce').mean(axis=1)).applymap(mix_number).to_string())
    print_table_title(f"{ticker_list} average of Latest")
    print(pd.DataFrame(data[latest_index].apply(pd.to_numeric, errors='coerce').mean(axis=1)).applymap(mix_number).to_string())


def scrape_company_fundamentals(ticker_list, file_path, risk_free_return, quarter=False, year=5):
    """
    This function scrapes all the companies in the ticker_list for financial data and save to tsv file.
    :param ticker: company stock ticker
    :param risk_free_return: the 3-month t-bill return
    :param quarter: whether to see it's quarter report. If false, will see its annual report
    :param year: see data back to how many years. 5 is the default
    :return:
    """
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    items = [
        "ticker", "market cap", "industry", "sector", "current price", "gross margin", "net income margin",
        "expenses portion", "ROE", "ROA", "receivables turnover days", "inventories turnover days",
        "total assets turnover days", "liability/asset ratio", "current ratio", "acid-test ratio", "revenue growth",
        "net income growth", "operating income growth", "free cash flow growth", "wacc", "roic", "excess return", 
        "economic profit", "stockholders equity growth", "dividend yield", "dividend payout ratio", "dcf", "beta",
        "annual return", "annual risk"
    ]
    with open(file_path, "w") as fp:
        fp.write("\t".join(items)+"\n")
        tickers_failed = []
        for result in p.imap(company_scraping_worker, [[ticker, risk_free_return, quarter] for ticker in ticker_list]):
            if len(result) <= 5:
                tickers_failed.append(result)
            else:
                fp.write(result)
        print(f"failed tickers={tickers_failed}")


def company_scraping_worker(args):
    """
    This is a helper function to parallelize the company information scraping.
    :param args: a list of four arguments: [ticker, risk_free_return, market_return, quarter]
    :return: the ticker if cannot scrape, or scraping info if can scrape
    """
    c = Company(args[0], quarter=args[2])
    try:
        t0 = time.clock()
        data = c.serialize_fundamentals_summary(args[1])
        print(f"- {args[0]} scraping done, takes {round(time.clock() - t0, 2)} seconds")
        return data
    except Exception:
        print(f"cannot scrape {args[0]}")
        return args[0]



