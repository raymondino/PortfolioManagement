import pandas as pd
import requests
from utils.widget import *


class CashflowStatement:
    url_prefix_f = "https://financialmodelingprep.com/api/v3/financials/"
    api_key = "ef7be903a5ace951c13f320358723e0f"

    cf_full_items = [
        "date",
        "Depreciation & Amortization",
        "Stock-based compensation",
        "Operating Cash Flow",
        "Capital Expenditure",
        "Acquisitions and disposals",
        "Investment purchases and sales",
        "Investing Cash flow" ,
        "Issuance (repayment) of debt",
        "Issuance (buybacks) of shares",
        "Dividend payments",
        "Financing Cash Flow",
        "Effect of forex changes on cash",
        "Net cash flow / Change in cash",
        "Free Cash Flow",
        "Net Cash/Marketcap"
    ]

    cf_print_items = [
        "date", "Operating Cash Flow", "Investing Cash flow", "Financing Cash Flow", "Net Cash Flow",
        "Capital Expenditure", "Free Cash Flow"
    ]

    def __init__(self, ticker, quarter=False, year=5):
        self.cf_url = f"{CashflowStatement.url_prefix_f}/cash-flow-statement/{ticker}"
        self.quarter = quarter
        self.ticker = ticker
        self.year = year
        self.data = requests.get(self.cf_url + (f"?period=quarter&apikey={CashflowStatement.api_key}" if quarter else f"?apikey={CashflowStatement.api_key}")).json()['financials']
        self.data = pd.DataFrame.from_dict(self.data)[CashflowStatement.cf_full_items]
        self.data = self.data[(self.data.date.str.len() == 10)]

        columns_to_number = [c for c in CashflowStatement.cf_full_items if c != "date"]
        self.data[columns_to_number] = self.data[columns_to_number].apply(pd.to_numeric, errors="coerce")
        self.data["Net Cash Flow"] = self.data[['Operating Cash Flow',"Investing Cash flow","Financing Cash Flow"]].sum(axis=1)

        self.cashflow_statement = self.data[CashflowStatement.cf_print_items]
        self.cashflow_statement.set_index('date', inplace=True, drop=True)
        self.cashflow_statement = self.cashflow_statement.sort_index(ascending=False).iloc[:(self.year if not self.quarter else 3 * self.year)].T

    def print(self):
        print_table_title(f"{self.ticker} Cash Flow Statements")
        print(self.cashflow_statement.applymap(millify).to_string(max_rows=100, max_cols=100))
