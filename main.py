from tools.financials_analyzer import *
from tools.asset_price_analyzer import *
from tools.modern_portfolio_theory_optimizer import *


if __name__ == "__main__":
    # some global parameters
    year = 5
    quarter = False
    risk_free_return = 0.009

    # adjust the number to toggle functions
    number = 2.3

    # get fundamentals & insights for a company
    if number == 1.1:
        analyze_company("AAPL", risk_free_return, quarter=quarter, year=year)

    # compare fundamentals, specifying ticker_list will overwrite tickers loaded from ticker_list_file
    elif number == 1.2:
        ticker_list_file = r"./data/company_tickers_to_compare_fundamentals.txt"
        ticker_list =["MSFT", "GOOG"]
        if len(ticker_list) == 0 and not os.path.exists(ticker_list_file):
            print(f"ERROR: path does not exist: {ticker_list_file}")
        if len(ticker_list) == 0:
            with open(ticker_list_file, 'r', encoding='utf-8') as fp:
                ticker_list = set([ticker.strip() for ticker in fp.readlines()])
        compare_companies(ticker_list, risk_free_return)

    # scrape (possibly) all US listed companies' fundamentals
    elif number == 1.3:
        ticker_list_file = r"./data/all_tickers_amex_nasdaq_nyse_20200419.txt"
        scraping_result_file = r"./data/company_scrapings.tsv"
        if not os.path.exists(ticker_list_file):
            print(f"ERROR: path does not exist: {ticker_list_file}")
        with open(ticker_list_file, 'r', encoding='utf-8') as fp:
            ticker_list = set([t.strip() for t in fp.readlines()])
        scrape_company_fundamentals(ticker_list, scraping_result_file, risk_free_return)

    # get a list of  tickers' annualized return and risk over past 5 years
    elif number == 2.1:
        ticker_list = ["IVV"]
        print('\t'.join(['ticker', 'annualized return', 'annualized risk', 'beta']))
        for t in ticker_list:
            print('\t'.join([t] + [str(round(d, 4)) for d in Asset(t).get_expected_yearly_return_risk_beta()]))

    # scrape asset price expected daily return and risk
    elif number == 2.2:
        ticker_list_file = r"./data/first_round_filtering.txt"
        scraping_result_file = r"./data/asset_daily_return_risk.tsv"
        with open(ticker_list_file, 'r', encoding='utf-8') as fp:
            ticker_list = set([t.strip() for t in fp.readlines()])
        scrape_asset_return_risk(ticker_list, scraping_result_file)

    # plot a list of tickers return & risk from a tsv file with 3 columns: ticker, return, and risk
    elif number == 2.3:
        asset_return_risk_file_path = r"./data/asset_daily_return_risk.tsv"
        highlights = []  # to highlight certain assets
        only_show = []  # to only plot certain assets
        plot_assets_in_return_risk_plane(asset_return_risk_file_path, set(highlights), set(only_show))

    # plot portfolio assets correlation using the latest 5 years of daily price
    elif number == 3.1:
        asset_tickers = ["MSFT","VEEV","CPRT","MKTX","MASI","KL","PDEX"]
        p = Portfolio()
        p.invest(asset_tickers)
        p.plot_asset_correlation()

    # risk-optimized portfolio with MPT
    elif number == 3.2:
        asset_tickers = []
        mpt_optimization(asset_tickers)

    # sharpe ratio-optimized portfolio with MPT
    elif number == 3.3:
        asset_tickers = ["MSFT","VEEV","CPRT","MKTX","MASI","KL","PDEX"]
        mpt_optimization(asset_tickers, risk_free_return)

    # evaluate MPT optimization
    elif number == 3.4:
        asset_tickers = ["MSFT","VEEV","CPRT","MKTX","MASI","KL","PDEX"]
        mpt_evaluation(asset_tickers, risk_free_return)

    # use customized weights to get the risk/sharpe ratio/return of the portfolio
    elif number == 3.5:
        asset_tickers = ["MSFT", "AAPL", "V", "INTC", "MA"]
        customize_weights = [18.46/(18.46+18.25+4.46+3.8+3.5),18.25/(18.46+18.25+4.46+3.8+3.5),4.46/(18.46+18.25+4.46+3.8+3.5),3.8/(18.46+18.25+4.46+3.8+3.5),3.5/(18.46+18.25+4.46+3.8+3.5)]
        mpt_customize_weights(asset_tickers, customize_weights, risk_free_return)

    # plot 20-day risk & return for an asset
    elif number == 4.1:
        Asset.print_yearly_return_risk(["MSFT"])

    # plot company stock price and revenue correlation
    elif number == 4.2:
        c = Company("KL")
        c.plot_stock_price_with_revenue()

    elif number == 5:
        # a = Asset("MSFT")
        # print(a.get_beta())
        c = Company("BT")
        print(c.serialize_fundamentals_summary(risk_free_return))