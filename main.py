import os
from tools.financials_analyzer import *
from tools.asset_price_analyzer import *
from tools.modern_portfolio_theory_optimizer import *


if __name__ == "__main__":
    # some global parameters
    year = 5
    quarter = False
    risk_free_return = 0.0012

    # adjust the number to toggle functions
    number = 0

    # get fundamentals & insights for a company
    if number == 0:
        analyze_company("MSFT", risk_free_return, quarter=quarter, year=year)

    # scrape (possibly) all US listed companies' fundamentals
    elif number == 1:
        ticker_list_file = r"/data/all_tickers_amex_nasdaq_nyse_20200419.txt"
        scraping_result_file = r"/data/company_scrapings.tsv"
        if not os.path.exists(ticker_list_file):
            print(f"ERROR: path does not exist: {ticker_list_file}")
        with open(ticker_list_file, 'r', encoding='utf-8') as fp:
            ticker_list = set([t.strip() for t in fp.readlines()])
        scrape_company_fundamentals(ticker_list, scraping_result_file, risk_free_return)

    # compare fundamentals, specifying ticker_list will overwrite tickers loaded from ticker_list_file
    elif number == 2:
        ticker_list_file = r"/data/company_tickers_to_compare_fundamentals.txt"
        ticker_list = ["T", "VZ"]
        if len(ticker_list) == 0 and not os.path.exists(ticker_list_file):
            print(f"ERROR: path does not exist: {ticker_list_file}")
        if len(ticker_list) == 0:
            with open(ticker_list_file, 'r', encoding='utf-8') as fp:
                ticker_list = set([ticker.strip() for ticker in fp.readlines()])
        compare_companies(ticker_list, risk_free_return)

    # get a ticker's daily expected return and risk over past 5 years
    elif number == 3:
        ticker = "MSFT"
        print('\t'.join([ticker] + [str(d) for d in Asset(ticker).get_expected_daily_return_and_risk()]) + '\n')

    # scrape asset price expected daily return and risk
    elif number == 4:
        ticker_list_file = r"/data/first_round_filtering.txt"
        scraping_result_file = r"/data/asset_daily_return_risk.tsv"
        with open(ticker_list_file, 'r', encoding='utf-8') as fp:
            ticker_list = set([t.strip() for t in fp.readlines()])
        scrape_asset_return_risk(ticker_list, scraping_result_file)

    # plot a list of tickers return & risk from a tsv file with 3 columns: ticker, return, and risk
    elif number == 5:
        asset_return_risk_file_path = r"/data/asset_daily_return_risk.tsv"
        highlights = []  # to highlight certain assets
        only_show = []  # to only plot certain assets
        plot_assets_in_return_risk_plane(asset_return_risk_file_path, set(highlights), set(only_show))

    # plot portfolio assets correlation
    elif number == 6:
        asset_tickers = []
        p = Portfolio()
        p.invest(asset_tickers)
        p.plot_asset_correlation()

    # risk-optimized portfolio with MPT
    elif number == 7:
        asset_tickers = []
        mpt_optimization(asset_tickers)

    # sharpe ratio-optimized portfolio with MPT
    elif number == 8:
        asset_tickers = []
        mpt_optimization(asset_tickers, risk_free_return)

    # evaluate MPT optimization
    elif number == 9:
        asset_tickers = []
        mpt_evaluation(asset_tickers, risk_free_return)

    # use customized weights to get the risk/sharpe ratio/return of the portfolio
    elif number == 10:
        asset_tickers = []
        customize_weights = []
        mpt_customize_weights(asset_tickers, customize_weights, risk_free_return)
