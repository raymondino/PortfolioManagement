from tools.financials_analyzer import *
from tools.asset_price_analyzer import *
from tools.modern_portfolio_theory_optimizer import *
from tools.portfolio_analyzer import *


if __name__ == "__main__":
    # some global parameters
    year = 5
    quarter = False
    risk_free_return = 0.009

    # adjust the number to toggle functions
    number = 3.6

    # get fundamentals & insights for a company
    if number == 1.1:
        analyze_company("BRK-B", risk_free_return, quarter=quarter, year=year)

    # compare fundamentals, specifying ticker_list will overwrite tickers loaded from ticker_list_file
    elif number == 1.2:
        ticker_list_file = r"./data/company_tickers_to_compare_fundamentals.txt"
        ticker_list = ["EQIX", "AMT", "CCI"]
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
        ticker_list = ["EXPO"]
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
        highlights =  ['MSFT', 'ZTS', 'VEEV', 'MKTX', 'WST', 'MASI', 'KL', 'EXPO', 'PDEX']  # to highlight certain assets
        only_show = []  # to only plot certain assets
        plot_assets_in_return_risk_plane(asset_return_risk_file_path, set(highlights), set(only_show))

    # plot portfolio assets correlation using the latest 5 years of daily price
    elif number == 3.1:
        asset_tickers = ["NEM", "GOLD", "AEM", "KL", "AU", "KGC", "GFI", "BTG", "BVN", "AUY", "NG", "AGI", "SSRM", "PVG", "CDE", "HMY", "IAG", "HL", "EGO", "EQX", "GSS", "GLD"]
        p = Portfolio()
        p.invest(asset_tickers)
        p.plot_asset_correlation()

    # risk-optimized portfolio with MPT
    elif number == 3.2:
        asset_tickers = []
        mpt_optimization(asset_tickers)

    # sharpe ratio-optimized portfolio with MPT
    elif number == 3.3:
        # asset_tickers = ['ZTS', 'VEEV', 'MKTX', 'WST', 'MASI', 'KL', 'EXPO', "SGOL"]
        asset_tickers = ["MSFT", "BRK-B", "AMZN"]
        mpt_optimization(asset_tickers, risk_free_return, start_date="2015-05-08", end_date="2020-02-01")

    # evaluate MPT optimization
    elif number == 3.4:
        asset_tickers = ['MSFT', "AAPL", "AMZN", "GOOG", "FB"]
        mpt_evaluation(asset_tickers, risk_free_return)

    # use customized weights to get the risk/sharpe ratio/return of the portfolio
    elif number == 3.5:
        # asset_tickers = ['ZTS', 'VEEV', 'MKTX', 'WST', 'MASI', 'KL', 'EXPO', 'SGOL']
        asset_tickers = ["CDE", "HL", "SSRM"]
        customize_weights = [0.33, 0.34, 0.33]
        # customize_weights = [0.0962, 0.0798, 0.1476, 0.1049, 0.2263, 0.1623, 0.0584, 0.1245]
        mpt_customize_weights(asset_tickers, customize_weights, risk_free_return, start_date="2020-05-08", end_date="2020-05-14")

    # back test portfolio with assets and their specified weights
    elif number == 3.6:
        asset_tickers = ['ZTS', 'VEEV', 'MKTX', 'WST', 'MASI', 'KL', 'EXPO', 'SGOL']
        customized_weights = [0.0962, 0.0798, 0.1476, 0.1049, 0.2263, 0.1623, 0.0584, 0.1245]
        back_test_portfolio(asset_tickers, customized_weights, "first blood backtest", r"./data/portfolio/firstblood_backtest_report.html")

        asset_tickers = ["MSFT", "AMZN"]
        customized_weights = [0.554, 0.446]
        back_test_portfolio(asset_tickers, customized_weights, "mega tech backtest", r"./data/portfolio/megatech_backtest_report.html")

    # generate portfolio reports
    elif number == 3.7:
        # this requires you to generate a portfolio json file
        portfolio_file = r"./data/portfolio/first_blood_20200511.json"
        get_portfolio_performance(portfolio_file, r"./data/portfolio/first_blood_20200511.html")

        portfolio_file = r"./data/portfolio/mega_tech_20200511.json"
        get_portfolio_performance(portfolio_file, r"./data/portfolio/mega_tech_20200511.html")

    # plot 20-day risk & return for an asset
    elif number == 4.1:
        Asset.print_yearly_return_risk(["MSFT"])

    # plot company stock price and revenue correlation
    elif number == 4.2:
        c = Company("ZTS")
        c.plot_stock_price_with_revenue(quarter=False)

    # plot a single stock performance
    elif number == 4.3:
        ticker = "AMZN"
        Asset(ticker).report_asset_stock_performance(report_path=rf"./data/portfolio/{ticker}_report.html")

    elif number == 5:
        # a = Asset("MSFT")
        # print(a.get_beta())
        c = Company("BT")
        print(c.serialize_fundamentals_summary(risk_free_return))