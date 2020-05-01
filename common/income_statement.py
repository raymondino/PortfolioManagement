import pandas as pd
import requests
from utils.widget import *


class IncomeStatement:
    url_prefix_f = "https://financialmodelingprep.com/api/v3/financials/"
    is_full_items = [
        "date",
        "Revenue",
        "Revenue Growth",
        "Cost of Revenue",
        "Gross Profit",
        "R&D Expenses",
        "SG&A Expense",
        "Operating Expenses",  # = R&D Expenses + SG&A Expense
        "Operating Income",  # = EBIT = Gross Profit - Operating Expenses
        "Interest Expense",
        "Earnings before Tax",  # number not correct from API, will not use it
        "Income Tax Expense",
        "Net Income - Non-Controlling int",
        "Net Income - Discontinued ops",
        "Net Income",
        "Preferred Dividends",
        "Net Income Com",
        "EPS",
        "EPS Diluted",
        "Weighted Average Shs Out",
        "Weighted Average Shs Out (Dil)",
        "Dividend per Share",
        "Gross Margin",
        "EBITDA Margin",
        "EBIT Margin",
        "Profit Margin",
        "Free Cash Flow margin",
        "EBITDA",
        "EBIT",
        "Consolidated Income",
        "Earnings Before Tax Margin",
        "Net Profit Margin"
    ]

    is_print_items = [
        "date", "Revenue", "Cost of Revenue", "Gross Profit", "R&D Expenses", "SG&A Expense",
        "Operating Income", "Interest Expense", "Income Before Tax", "Income Tax Expense", "Net Income"
    ]

    def __init__(self, ticker, quarter=False, year=5):
        self.is_url = f"{IncomeStatement.url_prefix_f}/income-statement/{ticker}"
        self.quarter = quarter
        self.ticker = ticker
        self.year = year
        self.data = requests.get(self.is_url + ("?period=quarter" if quarter else "")).json()["financials"]
        self.data = pd.DataFrame.from_dict(self.data)[IncomeStatement.is_full_items]
        self.data["Income Before Tax"] = self.data["Income Tax Expense"].apply(pd.to_numeric, errors="coerce") + \
                                         self.data["Net Income"].apply(pd.to_numeric, errors="coerce")
        self.income_statement = self.data[IncomeStatement.is_print_items]
        self.income_statement.set_index('date', inplace=True, drop=True)
        self.income_statement = self.income_statement.sort_index(ascending=False).iloc[
                                :(self.year if not self.quarter else 3 * self.year)].T
        self.income_statement = self.income_statement.apply(pd.to_numeric, errors="coerce")

    def print(self, year=5):
        print_table_title(f"{self.ticker} Income Statements")
        print(self.income_statement.applymap(millify).to_string(max_rows=100, max_cols=100))
