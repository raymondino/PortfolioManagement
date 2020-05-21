import pandas as pd
import requests
import numpy as np
from utils.widget import *


class IncomeStatement:
    url_prefix_f = "https://financialmodelingprep.com/api/v3/financials/"
    api_key = "ef7be903a5ace951c13f320358723e0f"
    is_full_items = [
        "date",
        "Revenue",
        "Revenue Growth",  # not always correct, I compute it by myself
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
        "date", "Revenue", "Cost of Revenue", "Gross Profit", "R&D Expenses", "SG&A Expense", "Operating Expenses",
        "Operating Income", "Interest Expense", "Income Before Tax", "Income Tax Expense", "Net Income"
    ]

    def __init__(self, ticker, quarter=False, year=5):
        self.is_url = f"{IncomeStatement.url_prefix_f}/income-statement/{ticker}"
        self.quarter = quarter
        self.ticker = ticker
        self.year = year
        self.data = requests.get(self.is_url + (f"?period=quarter&apikey={IncomeStatement.api_key}" if quarter else f"?apikey={IncomeStatement.api_key}")).json()["financials"]
        self.data = pd.DataFrame.from_dict(self.data)[IncomeStatement.is_full_items]
        self.data = self.data[(self.data.date.str.len() == 10)]

        columns_to_number = [c for c in IncomeStatement.is_full_items if c != "date"]
        self.data[columns_to_number] = self.data[columns_to_number].apply(pd.to_numeric, errors="coerce")
        self.data["Revenue Growth"] = self.data["Revenue"].pct_change(-1).dropna()*np.sign(self.data["Revenue"].shift(periods=-1).dropna())
        self.data["Income Before Tax"] = self.data["Income Tax Expense"] + self.data["Net Income"]

        self.income_statement = self.data[IncomeStatement.is_print_items]
        self.income_statement.set_index('date', inplace=True, drop=True)
        self.income_statement = self.income_statement.sort_index(ascending=False).iloc[:(self.year if not self.quarter else 3 * self.year)].T

    def print(self, year=5):
        print_table_title(f"{self.ticker} Income Statements")
        print(self.income_statement.applymap(millify).to_string(max_rows=100, max_cols=100))
        print("NOTE: Operating Expenses = R&D Expenses + SG&A Expenses + other expenses (compensation)")
