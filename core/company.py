import numpy as np
from common.financial_insight import *


class Company:
    def __init__(self, ticker, quarter=False, year=5):
        self.ticker = ticker
        self.quarter=quarter
        self.year = year
        self.financial_insights = None
        data = requests.get(f"https://financialmodelingprep.com/api/v3/company/profile/{ticker}").json()["profile"]
        self.beta = data['beta']
        self.industry = data['industry']
        self.current_market_cap = data['mktCap']
        self.current_price = data['price']
        self.sector = data['sector']

    def print_financials(self):
        if self.financial_insights is None:
            self.financial_insights = FinancialInsight(self.ticker, year=self.year)
        self.financial_insights.print_financials()

    def print_quantitative_analysis(self, risk_free_return):
        if self.financial_insights is None:
            self.financial_insights = FinancialInsight(self.ticker)
        self.financial_insights.print_quantitative_fundamentals(self.beta, risk_free_return)