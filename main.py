from tools.company_fundamentals_analyzer import *
from tools.asset_price_analyzer import *
from tools.modern_portfolio_theory_optimizer import *
import os


def compare_fundamentals(ticker_list):
    if len(ticker_list) == 0 and not os.path.exists(ticker_list_file):
        print(f"ERROR: path does not exist: {ticker_list_file}")
    if len(ticker_list) == 0:
        with open(ticker_list_file, 'r', encoding='utf-8') as fp:
            ticker_list = set([ticker.strip() for ticker in fp.readlines()])
    compare_companies(ticker_list, risk_free_return=risk_free_return, market_return=market_return)


def company_fundamentals_scraper():
    if not os.path.exists(ticker_list_file):
        print(f"ERROR: path does not exist: {ticker_list_file}")
    with open(ticker_list_file, 'r', encoding='utf-8') as fp:
        ticker_list = set([t.strip() for t in fp.readlines()])
    scrape_company_fundamentals(ticker_list, scraping_result_file, risk_free_return, market_return)


def asset_daily_expected_return_risk_scraper():
    with open(ticker_list_file, 'r', encoding='utf-8') as fp:
        ticker_list = set([t.strip() for t in fp.readlines()])
    scrape_asset_return_risk(ticker_list, scraping_result_file)


if __name__ == "__main__":
    # some global parameters
    risk_free_return = 0.0025
    market_return = 0.0668
    quarter = False

    # adjust the number to toggle functions
    number = 9

    # get one company fundamentals
    if number == 0:
        ticker = "TSLA"
        analyze_company(ticker, risk_free_return=risk_free_return, market_return=market_return, quarter=quarter)

    # compare fundamentals for a list of companies, specify tickers or read tickers from a file
    elif number == 1:
        ticker_list_file = r"C:\Users\ruya\Documents\PortfolioManagement\data\company_tickers_to_compare_fundamentals.txt"
        # specifying ticker_list will overwrite tickers read from ticker_list_file
        compare_fundamentals(ticker_list=["MSFT", "TSLA"])

    # get a ticker's daily expected return and risk
    elif number == 2:
        ticker = "MSFT"
        a = Asset(ticker)
        print('\t'.join([ticker] + [str(d) for d in a.get_expected_daily_return_and_risk_from_all_history()]) + '\n')

    # plot a series of ticker's return and risk from file, the file is generated by function called
    # asset_daily_expected_return_risk_scraper, so if you do not have such file, you need to run that function first
    elif number == 3:
        asset_return_risk_file_path = r"C:\Users\ruya\Documents\PortfolioManagement\data\asset_daily_return_risk.tsv"
        highlights = ["MSFT"]  # to highlight certain assets
        only_show = []  # to only plot certain assets
        plot_assets_in_return_risk_plane(asset_return_risk_file_path, set(highlights), set(only_show))

    # scrape companies fundamentals
    elif number == 4:
        ticker_list_file = r"C:\Users\ruya\Documents\PortfolioManagement\data\nasdaq_amex_nyse.txt"
        scraping_result_file = r"C:\Users\ruya\Documents\PortfolioManagement\data\company_scrapings.tsv"
        company_fundamentals_scraper()

    # scrape asset price expected daily return and risk
    elif number == 5:
        ticker_list_file = r"C:\Users\ruya\Documents\PortfolioManagement\data\first_round_filtering.txt"
        scraping_result_file = r"C:\Users\ruya\Documents\PortfolioManagement\data\asset_daily_return_risk.tsv"
        asset_daily_expected_return_risk_scraper()

    # plot assets correlation
    elif number == 6:
        asset_tickers = ["MSFT", "GOOG", "FB"]
        p = Portfolio()
        p.invest(asset_tickers)
        p.plot_asset_correlation()

    # risk-optimized portfolio with MPT
    elif number == 7:
        asset_tickers = ["MSFT", "GOOG", "FB"]
        mpt_optimization(asset_tickers)

    # sharpe ratio-optimized portfolio with MPT
    elif number == 8:
        asset_tickers = ["MSFT", "GOOG", "FB"]
        mpt_optimization(asset_tickers, risk_free_annual_yield=risk_free_return)

    # evaluate MPT optimization
    elif number == 9:
        asset_tickers = ["MSFT", "GLD"]
        mpt_evaluation(asset_tickers, risk_free_annual_yield=risk_free_return)

    # use customized weights to get the risk/sharpe ratio/return of the portfolio
    elif number == 10:
        asset_tickers = ["MSFT", "GOOG", "FB"]
        customize_weights = [0.2, 0.4, 0.4]
        mpt_customize_weights(asset_tickers, customize_weights=customize_weights, risk_free_annual_yield=risk_free_return)










