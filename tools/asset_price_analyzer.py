import time
import multiprocessing
from core.asset import *


def scrape_asset_prices(ticker_list, file_path):
    """
    This function scrapes the price for each ticker, and calculate the daily expected return and risk. Save the data
    to file_path
    :param ticker_list: a list of tickers to scrape
    :param file_path: a file path to save the data
    :return:
    """
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    with open(file_path, 'w', encoding='utf-8') as fp:
        fp.write("ticker\texpected daily return\tdaily risk\n")
        tickers_failed = []
        for result in p.imap(price_scraping_worker, ticker_list):
            if len(result) < 5:
                tickers_failed.append(result)
            else:
                fp.write(result)
        print(f"failed tickers={tickers_failed}")


def price_scraping_worker(ticker):
    """
    This is a helper function to parallelize the asset price scraping
    :param ticker: the ticker to be scraped
    :return: the daily expected return and risk for ticker if successful, otherwise the ticker itself
    """
    a = Asset(ticker)
    try:
        t0 = time.clock()
        data = a.get_expected_daily_return_and_risk_from_all_history()
        print(f"- {ticker} e-sigma scraping done, takes {round(time.clock() - t0, 2)} seconds")
        return '\t'.join([ticker] + [str(d) for d in data])+'\n'
    except Exception as e:
        print(e)
        print(f"cannot scrape {ticker}")
        return ticker
