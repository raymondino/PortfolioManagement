from tools.company_fundamentals_analyzer import *


if __name__ == "__main__":
    # analyze a company fundamentals
    analyze_company("MSFT", risk_free_return=0.0025, market_return=0.0668)