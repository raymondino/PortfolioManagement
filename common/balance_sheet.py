import pandas as pd
import requests
from utils.widget import *


class BalanceSheet():
    url_prefix_f = "https://financialmodelingprep.com/api/v3/financials/"
    bs_full_items = [
        "date",
        "Cash and cash equivalents",
        "Short-term investments",
        "Cash and short-term investments",  # = Cash and cash equivalents + Short-term investments
        "Receivables",
        "Inventories",
        "Total current assets",
        "Property, Plant & Equipment Net",
        "Goodwill and Intangible Assets",
        "Long-term investments",
        "Tax assets",  # tax return, not needed
        "Total non-current assets",
        "Total assets",
        "Payables",
        "Short-term debt",
        "Total current liabilities",
        "Long-term debt",
        "Total debt",  # Short-term debt + Long-term debt
        "Deferred revenue",
        "Tax Liabilities",
        "Deposit Liabilities",
        "Total non-current liabilities",
        "Total liabilities",
        "Other comprehensive income",
        "Retained earnings (deficit)",
        "Total shareholders equity",
        "Investments",  # = Short-term investments + Long-term investments
        "Net Debt",
        "Other Assets",
        "Other Liabilities"
    ]

    bs_print_items = [
        "date", "Cash and short-term investments", "Receivables", "Inventories", "Total current assets",
        "Property, Plant & Equipment Net", "Goodwill and Intangible Assets", "Long-term investments",
        "Total non-current assets", "Total assets", "Payables", "Short-term debt", "Total current liabilities",
        "Long-term debt", "Deferred revenue", "Total non-current liabilities", "Total liabilities",
        "Other comprehensive income", "Retained earnings (deficit)", "Total shareholders equity"
    ]

    def __init__(self, ticker, quarter=False, year=5):
        self.bs_url = f"{BalanceSheet.url_prefix_f}/balance-sheet-statement/{ticker}"
        self.quarter = quarter
        self.ticker = ticker
        self.year = year
        self.data = requests.get(self.bs_url + ("?period=quarter" if quarter else "")).json()['financials']
        self.data = pd.DataFrame.from_dict(self.data)[BalanceSheet.bs_full_items]
        self.balance_sheet = self.data[BalanceSheet.bs_print_items]
        self.balance_sheet.set_index('date', inplace=True, drop=True)
        self.balance_sheet = self.balance_sheet.sort_index(ascending=False).iloc[
                             :(self.year if not self.quarter else 3 * self.year)].T
        self.balance_sheet = self.balance_sheet.apply(pd.to_numeric, errors='coerce')

    def print(self):
        print_table_title(f"{self.ticker} Balance Sheet")
        print(self.balance_sheet.applymap(millify).to_string(max_rows=100, max_cols=100))

        bs_structure = pd.concat([
            self.balance_sheet.loc['Cash and short-term investments']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Receivables']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Inventories']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Total current assets']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Property, Plant & Equipment Net']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Goodwill and Intangible Assets']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Long-term investments']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Total non-current assets']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Total assets']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Payables']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Short-term debt']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Total current liabilities']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Long-term debt']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Deferred revenue']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Total non-current liabilities']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Total liabilities']/self.balance_sheet.loc['Total liabilities']
        ], axis=1)
        bs_structure.columns = [
            "Cash and short-term investments", "Receivables", "Inventories", "Total current assets",
            "Property, Plant, Equipment Net", "Goodwill and Intangible Assets", "Long-term investments",
            "Total non-current assets", "Total assets", "Payables", "Short-term debt", "Total current liabilities",
            "Long-term debt", "Deferred revenue", "Total non-current liabilities", "Total liabilities"
        ]
        print_table_title(f"{self.ticker} Balance Sheet Structure")
        print(bs_structure.T.applymap(percentify).to_string(max_rows=100, max_cols=100))
