from tools.company_fundamentals_analyzer import *


if __name__ == "__main__":
    # analyze a company fundamentals
    # analyze_company("MA", risk_free_return=0.0025, market_return=0.0668, quarter=True)

    # compare a list of companies
    # ticker_list = ["MSFT"]
    # compare_companies(ticker_list, risk_free_return=0.0025, market_return=0.0668)

    # scrape a list of companies and save to a file
    ticker_list = set()
    all_company_list = r"C:\Users\ruya\Documents\PortfolioManagement\data\nasdaq_amex_nyse.txt"
    with open(all_company_list, 'r', encoding='utf-8') as fp:
        ticker_list = set([ticker.strip() for ticker in fp.readlines()])
    file_path = r"C:\Users\ruya\Documents\PortfolioManagement\data\company_scrapings.tsv"
    scrape_company_fundamentals(ticker_list, file_path, 0.0025, 0.0668)