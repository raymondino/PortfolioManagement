import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from utils.widget import *


class Company:
    url_prefix_f = "https://financialmodelingprep.com/api/v3/financials/"
    url_prefix_e = "https://financialmodelingprep.com/api/v3/enterprise-value/"
    url_prefix_p = "https://financialmodelingprep.com/api/v3/company/profile/"

    def __init__(self, ticker, quarter=False):
        self.ticker = ticker
        self.quarter=quarter
        self.company_value = None
        self.balance_sheet = None
        self.income_statements = None
        self.cashflow_statements = None
        self.profitability_insights = None
        self.operating_insights = None
        self.solvency_insights = None
        self.investment_insights = None
        self.beta = 0
        self.bs_url = f"{Company.url_prefix_f}/balance-sheet-statement/{ticker}"
        self.is_url = f"{Company.url_prefix_f}/income-statement/{ticker}"
        self.cf_url = f"{Company.url_prefix_f}/cash-flow-statement/{ticker}"
        self.ev_url = f"{Company.url_prefix_e}{ticker}"
        self.pf_url = f"{Company.url_prefix_p}{ticker}"

    def __get_beta(self):
        if self.beta == 0:
            self.beta = float(requests.get(self.pf_url).json()["profile"]['beta'])

    def __get_company_value(self):
        ev_items = ["date", "Stock Price", "Number of Shares", "Market Capitalization", "Enterprise Value"]
        data = requests.get(self.ev_url + ("?period=quarter" if self.quarter else "")).json()['enterpriseValues']
        data = pd.DataFrame.from_dict(data)[ev_items]
        data.reindex(ev_items)
        self.company_value = data.T
        self.company_value.columns = self.company_value.iloc[0]
        self.company_value = self.company_value[1:].apply(pd.to_numeric, errors='coerce')

    def __get_balance_sheet(self):
        bs_items = ["date", "Cash and short-term investments", "Receivables", "Inventories", "Total current assets",
                    "Property, Plant & Equipment Net", "Goodwill and Intangible Assets", "Long-term investments",
                    "Total non-current assets", "Total assets", "Payables", "Deposit Liabilities","Short-term debt",
                    "Deferred revenue", "Total current liabilities", "Long-term debt", "Total non-current liabilities",
                    "Total liabilities", "Retained earnings (deficit)", "Total shareholders equity"]
        data = requests.get(self.bs_url + ("?period=quarter" if self.quarter else "")).json()['financials']
        data = pd.DataFrame.from_dict(data)[bs_items]
        data.reindex(bs_items)
        data.rename(columns={'Property, Plant & Equipment Net': 'Property, Plant, Equipment Net'}, inplace=True)
        self.balance_sheet = data.T
        self.balance_sheet.columns = self.balance_sheet.iloc[0]
        self.balance_sheet = self.balance_sheet[1:].apply(pd.to_numeric, errors='coerce')

    def __get_income_statements(self):
        is_items = ["date", "Revenue", "Cost of Revenue", "Gross Profit", "R&D Expenses", "SG&A Expense",
                    "Operating Income", "Interest Expense", "Income Tax Expense", "Net Income"]
        is_insights = ["date", "Revenue Growth", "Gross Margin", "Net Profit Margin", "Free Cash Flow margin"]
        data = requests.get(self.is_url + ("?period=quarter" if self.quarter else "")).json()['financials']
        dates = pd.DataFrame.from_dict(data)["date"]
        data = pd.DataFrame.from_dict(data)[is_items[1:] + is_insights[1:]].apply(pd.to_numeric, errors='coerce')
        data = pd.concat([dates, data], axis=1)
        data['Income Before Income Taxes'] = data['Net Income'] + data['Income Tax Expense']
        data['Other Income'] = data['Income Before Income Taxes'] - data['Operating Income']
        data['EBIT'] = data['Income Before Income Taxes'] + data['Interest Expense']
        is_items.insert(7, "Income Before Income Taxes")
        is_items.insert(7, "Other Income")
        is_items.append("EBIT")
        data.reindex(is_items + is_insights[1:])
        self.income_statements = data[is_items]
        self.income_statements = self.income_statements.rename(columns={'R&D Expenses': 'RnD Expenses'})
        self.income_statements = self.income_statements.rename(columns={'SG&A Expense': 'SGnA Expense'})
        self.income_statements = self.income_statements.T
        self.income_statements.columns = self.income_statements.iloc[0]
        self.income_statements = self.income_statements[1:].apply(pd.to_numeric, errors='coerce')
        self.profitability_insights = data[is_insights].T
        self.profitability_insights.columns = self.profitability_insights.iloc[0]
        self.profitability_insights = self.profitability_insights[1:].apply(pd.to_numeric, errors='coerce')

    def __get_cashflow_statements(self):
        cf_items = ["date", "Operating Cash Flow", "Financing Cash Flow", "Investing Cash flow",
                    "Net cash flow / Change in cash", "Free Cash Flow"]
        data = requests.get(self.cf_url + ("?period=quarter" if self.quarter else "")).json()['financials']
        data = pd.DataFrame.from_dict(data)[cf_items]
        data.reindex(cf_items)
        self.cashflow_statements = data.T
        self.cashflow_statements.columns = self.cashflow_statements.iloc[0]
        self.cashflow_statements = self.cashflow_statements[1:].apply(pd.to_numeric, errors='coerce')

    def __print_table_title(self, title):
        print()
        t = f"========== {title} =========="
        print("="*len(t))
        print(t)
        print("="*len(t))

    def print_balance_sheet(self, show_plot=False):
        if self.balance_sheet is None:
            self.__get_balance_sheet()
        self.__print_table_title(f"{self.ticker} Balance Sheet")
        print(self.balance_sheet.applymap(millify).to_string(max_rows=100, max_cols=100))
        bs_structure = pd.concat([
            self.balance_sheet.loc['Cash and short-term investments']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Receivables']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Inventories']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Total current assets']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Property, Plant, Equipment Net']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Goodwill and Intangible Assets']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Long-term investments']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Total non-current assets']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Total assets']/self.balance_sheet.loc['Total assets'],
            self.balance_sheet.loc['Payables']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Deposit Liabilities']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Short-term debt']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Deferred revenue']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Total current liabilities']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Long-term debt']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Total non-current liabilities']/self.balance_sheet.loc['Total liabilities'],
            self.balance_sheet.loc['Total liabilities']/self.balance_sheet.loc['Total liabilities']
        ], axis=1)
        bs_structure.columns = ["Cash and short-term investments", "Receivables", "Inventories", "Total current assets",
                    "Property, Plant, Equipment Net", "Goodwill and Intangible Assets", "Long-term investments",
                    "Total non-current assets", "Total assets", "Payables", "Deposit Liabilities","Short-term debt",
                    "Deferred revenue", "Total current liabilities", "Long-term debt", "Total non-current liabilities",
                    "Total liabilities"]
        self.__print_table_title(f"{self.ticker} Balance Sheet Structure")
        print(bs_structure.T.applymap(percentify).to_string(max_rows=100, max_cols=100))

        if show_plot:
            self.balance_sheet.T.iloc[::-1][
                ["Cash and short-term investments", "Receivables", "Inventories", "Total assets", "Total liabilities",
                 "Retained earnings (deficit)", "Total shareholders equity"]].plot.line(subplots=True, title=f"{self.ticker} Balance Sheet")
            plt.show()

    def print_income_statements(self, show_plot=False):
        if self.income_statements is None:
            self.__get_income_statements()

        self.__print_table_title(f"{self.ticker} Income Statements")
        print(self.income_statements.applymap(millify).to_string(max_rows=100, max_cols=100))

        if show_plot:
            self.income_statements.T.iloc[::-1][
                ["Revenue", "Cost of Revenue", "Gross Profit", "RnD Expenses", "SGnA Expense", "Interest Expense",
                 "Income Tax Expense", "Operating Income", "Net Income"]].plot.line(subplots=True, title=f"{self.ticker} Income Statements")
            plt.show()

    def print_cashflow_statements(self, show_plot=False):
        if self.cashflow_statements is None:
            self.__get_cashflow_statements()

        self.__print_table_title(f"{self.ticker} Cashflow Statements")
        print(self.cashflow_statements.applymap(millify).to_string(max_rows=100, max_cols=100))

        if show_plot:
            self.cashflow_statements.T.iloc[::-1].plot.line(subplots=True, title=f"{self.ticker} Cash Flow Statements")
            plt.show()

    def get_profitability_insights(self, show_plot=False, show_table=False):
        if self.balance_sheet is None:
            self.__get_balance_sheet()
        if self.income_statements is None:
            self.__get_income_statements()
        data = self.profitability_insights.T
        stats = pd.concat([
            self.income_statements.loc['Net Income'] / self.balance_sheet.loc['Total assets'],
            self.income_statements.loc['RnD Expenses'] / self.income_statements.loc['Revenue'],
            self.income_statements.loc['SGnA Expense'] / self.income_statements.loc['Revenue'],
            self.income_statements.loc['Interest Expense'] / (
                        self.balance_sheet.loc['Short-term debt'] + self.balance_sheet.loc['Long-term debt']),
            self.income_statements.loc['Income Tax Expense'] / self.income_statements.loc['Income Before Income Taxes']
        ], axis=1)
        stats.columns = ['Return on total assets', 'RnD Expense Margin', 'SGnA Expense Margin',
                         'Interest Rate Paid', 'Income Tax Rate']
        self.profitability_insights = self.profitability_insights.sort_index(ascending=False)
        self.profitability_insights = pd.concat([data, stats], axis=1).T.replace([np.inf, -np.inf], 0)
        self.profitability_insights.insert(loc=0, column="mean", value=self.profitability_insights.mean(axis=1))

        if show_table:
            self.__print_table_title(f"{self.ticker} Profitability Analysis")
            print(self.profitability_insights.applymap(percentify).to_string(max_rows=100, max_cols=100))
        if show_plot:
            self.profitability_insights.T.iloc[:0:-1].plot.line(title=f"{self.ticker} Profitability Analysis")
            plt.show()

    def get_operating_insights(self, show_plot=False, show_table=False):
        if self.balance_sheet is None:
            self.__get_balance_sheet()
        if self.income_statements is None:
            self.__get_income_statements()
        ins = self.income_statements.T
        bs = self.balance_sheet.T
        self.operating_insights = pd.concat([
                          365/(ins["Revenue"]/bs["Cash and short-term investments"]),
                          365/(ins["Revenue"]/bs["Receivables"]),
                          365/(ins["Cost of Revenue"]/bs['Inventories']),
                          365/(ins["Revenue"]/bs["Total current assets"]),
                          365/(ins["Revenue"]/bs["Property, Plant, Equipment Net"]),
                          365/(ins["Revenue"]/bs["Total assets"])], axis=1)
        self.operating_insights.columns = ["cash turnover days", "receivables turnover days",
                                           "inventories turnover days", "total current assets turnover days",
                                           "fixed assets turnover days", "total assets turnover days"]
        self.operating_insights = self.operating_insights.sort_index(ascending=False)
        self.operating_insights = self.operating_insights.T.replace([np.inf, -np.inf], 0)
        self.operating_insights.insert(loc=0, column="mean", value=self.operating_insights.mean(axis=1))

        if show_table:
            self.__print_table_title(f"{self.ticker} Operating Analysis")
            print(self.operating_insights.applymap(decimalize).to_string())
        if show_plot:
            self.operating_insights.T.iloc[:0:-1].plot.line(subplots=True, title=f"{self.ticker} Operating Analysis")
            plt.show()

    def get_solvency_insights(self, show_plot=False, show_table=False):
        if self.balance_sheet is None:
            self.__get_balance_sheet()
        if self.income_statements is None:
            self.__get_income_statements()
        ins = self.income_statements.T
        bs = self.balance_sheet.T
        self.solvency_insights = pd.concat([bs["Total current assets"]/bs["Total current liabilities"],
                          (bs["Total current assets"]-bs["Inventories"])/bs["Total current liabilities"],
                          ins["EBIT"]/ins["Interest Expense"], bs["Total liabilities"]/bs["Total assets"]], axis=1)
        self.solvency_insights.columns = ["current ratio", "acid-test ratio", "times interest earned",
                                          "liability/asset ratio"]
        self.solvency_insights = self.solvency_insights.sort_index(ascending=False)
        self.solvency_insights = self.solvency_insights.T.replace([np.inf, -np.inf], 0)
        self.solvency_insights.insert(loc=0, column="mean", value=self.solvency_insights.mean(axis=1))

        if show_table:
            self.__print_table_title(f"{self.ticker} Solvency Analysis")
            print(self.solvency_insights.applymap(decimalize).to_string())
        if show_plot:
            self.solvency_insights.T.iloc[:0:-1].plot.line(subplots=True, title=f"{self.ticker} Solvency Analysis")
            plt.show()

    def get_investment_insights(self, risk_free_return, market_return, show_table=False):
        if self.profitability_insights is None:
            self.get_profitability_insights(show_table=False)
        if self.company_value is None:
            self.__get_company_value()
        if self.beta == 0:
            self.__get_beta()

        total_debt = self.balance_sheet.loc['Short-term debt'] + self.balance_sheet.loc['Long-term debt']
        market_cap = self.company_value.loc['Market Capitalization']
        interest_rate = self.profitability_insights.loc['Interest Rate Paid'][1:]
        income_tax = self.profitability_insights.loc['Income Tax Rate'][1:]
        capm = risk_free_return + self.beta*(market_return - risk_free_return)
        wacc = total_debt/(total_debt+market_cap)*interest_rate*(1-income_tax)+market_cap/(total_debt+market_cap)*capm

        invested_capital = total_debt + self.balance_sheet.loc['Total shareholders equity']
        roic = self.income_statements.loc['Net Income']/invested_capital

        excess_return = roic - wacc
        economic_profit = excess_return * invested_capital

        self.investment_insights = pd.concat([wacc, roic, excess_return, economic_profit], axis=1)
        self.investment_insights.columns = ['wacc', 'roic', 'excess return', 'economic profit']
        self.investment_insights = self.investment_insights.sort_index(ascending=False)
        self.investment_insights = self.investment_insights.T.replace([np.inf, -np.inf], 0)
        self.investment_insights.insert(loc=0, column="mean", value=self.investment_insights.mean(axis=1))

        if show_table:
            self.__print_table_title(f"{self.ticker} Investment Analysis")
            print(pd.concat([self.investment_insights, self.company_value]).applymap(mix_number).to_string())

    def get_dfc_valuation(self, show_plot=False):
        pass

    def print_financials(self):
        self.print_balance_sheet()
        self.print_income_statements()
        self.print_cashflow_statements()

    def get_insights(self, risk_free_return, market_return):
        self.get_profitability_insights(show_table=True)
        self.get_operating_insights(show_table=True)
        self.get_solvency_insights(show_table=True)
        self.get_investment_insights(risk_free_return, market_return, show_table=True)
