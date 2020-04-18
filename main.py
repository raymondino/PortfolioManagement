from tools.company_fundamentals_analyzer import *
from tools.asset_price_analyzer import *

if __name__ == "__main__":
    # analyze a company fundamentals
    # analyze_company("SLP", risk_free_return=0.0025, market_return=0.0668, quarter=True)

    # compare a list of companies
    # ticker_list = ["CCO", "OUT", "QUOT", "OMC", "HHS", "NCMI", "IPG", "WPP"]
    # ticker_list=['MSFT']
    # compare_companies(ticker_list, risk_free_return=0.0025, market_return=0.0668)

    # scrape a list of companies and save to a file
    # ticker_list = set()
    # all_company_list = r"C:\Users\ruya\Documents\PortfolioManagement\data\nasdaq_amex_nyse.txt"
    # with open(all_company_list, 'r', encoding='utf-8') as fp:
    #     ticker_list = set([ticker.strip() for ticker in fp.readlines()])
    # file_path = r"C:\Users\ruya\Documents\PortfolioManagement\data\company_scrapings.tsv"
    # scrape_company_fundamentals(ticker_list, file_path, 0.0014, 0.0668)

    # get daily expected return and risk for an asset
    # a = Asset("MSFT")
    # print(a.get_expected_daily_return_and_risk_from_all_history())

    # scrape the ticker list for daily expected return and risk
    ticker_list = set()
    all_company_list = r"C:\Users\ruya\Documents\PortfolioManagement\data\nasdaq_amex_nyse.txt"
    with open(all_company_list, 'r', encoding='utf-8') as fp:
        ticker_list = set([ticker.strip() for ticker in fp.readlines()])
    file_path = r"C:\Users\ruya\Documents\PortfolioManagement\data\asset_daily_return_risk.tsv"
    scrape_asset_prices(ticker_list, file_path)