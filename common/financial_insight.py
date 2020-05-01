import numpy as np
from core.asset import *
from common.balance_sheet import *
from common.income_statement import *
from common.cashflow_statement import *


class FinancialInsight:
    def __init__(self, ticker, quarter=False, year=5):
        self.quarter = quarter
        self.ticker = ticker
        self.year = year
        self.beta = 0
        self.balance_sheet = BalanceSheet(ticker, quarter, year)
        self.income_statement = IncomeStatement(ticker, quarter, year)
        self.cashflow_statement = CashflowStatement(ticker, quarter, year)
        self.company_value = None

    def __get_company_value(self):
        if self.company_value is None:
            ev_url = f"https://financialmodelingprep.com/api/v3/enterprise-value/{self.ticker}"
            ev_items = ["date", "Stock Price", "Number of Shares", "Market Capitalization", "Enterprise Value"]
            data = requests.get(ev_url + ("?period=quarter" if self.quarter else "")).json()["enterpriseValues"]
            data = pd.DataFrame.from_dict(data)[ev_items]
            self.company_value = data.sort_index().iloc[:(self.year if not self.quarter else 3*self.year)].T
            self.company_value.columns = self.company_value.iloc[0]
            self.company_value = self.company_value[1:].apply(pd.to_numeric, errors="coerce")
        return self.company_value

    def print_financials(self):
        self.balance_sheet.print()
        self.income_statement.print()
        self.cashflow_statement.print()

    def print_quantitative_fundamentals(self, beta, risk_free_return):
        self.get_profitability_insights()
        self.get_operation_insights()
        self.get_solvency_insights()
        self.get_growth_insights()
        self.get_investing_insights(beta, risk_free_return)
        self.get_dfc_valuation()

    def get_profitability_insights(self):
        profitability = pd.concat([
            self.income_statement.data["Gross Margin"],
            (self.income_statement.data["Net Income"].apply(pd.to_numeric, errors="coerce") /
             self.income_statement.data["Revenue"].apply(pd.to_numeric, errors="coerce")),
            (self.income_statement.data["Operating Expenses"].apply(pd.to_numeric, errors="coerce") /
             self.income_statement.data["Revenue"].apply(pd.to_numeric, errors="coerce")),
            (self.income_statement.data["Net Income"].apply(pd.to_numeric, errors="coerce") /
             self.balance_sheet.data["Total shareholders equity"].apply(pd.to_numeric, errors="coerce")),
            (self.balance_sheet.data["Total liabilities"].apply(pd.to_numeric, errors="coerce") /
             self.balance_sheet.data["Total assets"].apply(pd.to_numeric, errors="coerce")),
            (self.income_statement.data["Net Income"].apply(pd.to_numeric, errors="coerce") /
             self.balance_sheet.data["Total assets"].apply(pd.to_numeric, errors="coerce"))
        ], axis=1)
        profitability.columns = [
            "Gross Margin", "Net Income Margin", "Expenses Portion", "ROE", "Liability/Asset Ratio", "ROA"
        ]
        profitability = profitability.sort_index().iloc[:(self.year if not self.quarter else 3 * self.year)].T
        profitability.columns = self.balance_sheet.balance_sheet.columns
        profitability = profitability.apply(pd.to_numeric, errors='coerce')
        profitability.insert(loc=0, column="mean", value=profitability.mean(axis=1))
        print_table_title(f"{self.ticker} Profitability")
        print(profitability.applymap(percentify).to_string(max_rows=100, max_cols=100))

    def get_operation_insights(self):
        operation = pd.concat([
            365 / (self.income_statement.data["Revenue"].apply(pd.to_numeric, errors="coerce") /
                   self.balance_sheet.data["Receivables"].rolling(2).mean().shift(-1)),
            365 / (self.income_statement.data["Cost of Revenue"].apply(pd.to_numeric, errors="coerce") /
                   self.balance_sheet.data["Inventories"].rolling(2).mean().shift(-1)),
            356 / (self.income_statement.data["Revenue"].apply(pd.to_numeric, errors="coerce") /
                   self.balance_sheet.data["Total assets"].rolling(2).mean().shift(-1))
        ], axis=1)
        operation.columns = [
            "Receivables Turnover Period", "Inventories Turnover Period", "Total Assets Turnover Period"
        ]
        operation = operation.sort_index().iloc[:(self.year if not self.quarter else 3 * self.year)].T
        operation.columns = self.balance_sheet.balance_sheet.columns
        operation = operation.apply(pd.to_numeric, errors='coerce')
        operation.insert(loc=0, column="mean", value=operation.mean(axis=1))
        print_table_title(f"{self.ticker} Operation")
        print(operation.applymap(decimalize).to_string(max_rows=100, max_cols=100))

    def get_solvency_insights(self):
        solvency = pd.concat([
            (self.balance_sheet.data["Total liabilities"].apply(pd.to_numeric, errors="coerce") /
             self.balance_sheet.data["Total assets"].apply(pd.to_numeric, errors="coerce")),
            (self.balance_sheet.data["Total current assets"].apply(pd.to_numeric, errors="coerce") /
             self.balance_sheet.data["Total current liabilities"].apply(pd.to_numeric, errors="coerce")),
            ((self.balance_sheet.data["Total current assets"].apply(pd.to_numeric, errors="coerce") -
              self.balance_sheet.data["Inventories"].apply(pd.to_numeric, errors="coerce")) /
             self.balance_sheet.data["Total current liabilities"].apply(pd.to_numeric, errors="coerce"))
        ], axis=1)
        solvency.columns = ["Liability/Asset Ratio", "Current Ratio", "Acid-test Ratio"]
        solvency = solvency.sort_index().iloc[:(self.year if not self.quarter else 3 * self.year)].T
        solvency = solvency.apply(pd.to_numeric, errors='coerce')
        solvency.columns = self.balance_sheet.balance_sheet.columns
        solvency.insert(loc=0, column="mean", value=solvency.mean(axis=1))
        print_table_title(f"{self.ticker} Solvency")
        print(solvency.applymap(decimalize).to_string(max_rows=100, max_cols=100))

    def get_growth_insights(self):
        growth = pd.concat([
            self.income_statement.data["Revenue Growth"],
            self.income_statement.data["Net Income"].apply(pd.to_numeric, errors="coerce").pct_change(-1),
            self.income_statement.data["Operating Income"].apply(pd.to_numeric, errors="coerce").pct_change(-1),
            self.cashflow_statement.data["Free Cash Flow"].apply(pd.to_numeric, errors="coerce").pct_change(-1)
        ], axis=1)
        growth.columns = [
            "Revenue Growth", "Net Income Growth", "Operating Income Growth", "Free Cash Flow Growth"
        ]
        growth = growth.sort_index().iloc[:(self.year if not self.quarter else 3 * self.year)].T
        growth = growth.apply(pd.to_numeric, errors='coerce')
        growth.columns = self.balance_sheet.balance_sheet.columns
        growth.insert(loc=0, column="mean", value=growth.mean(axis=1))
        print_table_title(f"{self.ticker} Growth")
        print(growth.applymap(percentify).to_string(max_rows=100, max_cols=100))

    def get_investing_insights(self, beta, risk_free_return):
        # find the 13 week T-bill return rate at https://finance.yahoo.com/bonds
        market_return = 0.1
        data = []
        json = requests.get(f"https://financialmodelingprep.com/api/v3/financial-ratios/{self.ticker}").json()["ratios"]
        for x in json:
            data.append(
                {"date": x["date"], "dividendYield": x["investmentValuationRatios"]["dividendYield"],
                 "dividendPayoutRatio": x["cashFlowIndicatorRatios"]["dividendPayoutRatio"]}
            )
        dividend = pd.DataFrame.from_dict(data).set_index("date").apply(pd.to_numeric, errors="coerce")
        dividend = dividend.sort_index(ascending=False).iloc[:(self.year if not self.quarter else 3*self.year)].T
        total_debt = self.balance_sheet.balance_sheet.loc["Short-term debt"] + \
                     self.balance_sheet.balance_sheet.loc["Long-term debt"]
        market_cap = self.__get_company_value().loc["Market Capitalization"]
        interest_rate = self.income_statement.income_statement.loc["Interest Expense"] / total_debt
        income_tax = self.income_statement.income_statement.loc["Income Tax Expense"] / \
                     self.income_statement.income_statement.loc["Income Before Tax"]
        capm = risk_free_return + float(beta)*(market_return - risk_free_return)
        wacc = total_debt/(total_debt+market_cap)*interest_rate*(1-income_tax)+market_cap/(total_debt+market_cap)*capm
        invested_capital = total_debt + self.balance_sheet.balance_sheet.loc["Total shareholders equity"]
        roic = self.income_statement.income_statement.loc["Net Income"]/invested_capital
        excess_return = roic - wacc
        
        economic_profit = excess_return * invested_capital
        investing = pd.concat([wacc, roic, excess_return, economic_profit], axis=1)
        investing.columns = ["wacc", "roic", "excess return", "economic profit"]
        investing = pd.concat([investing.T, dividend])
        investing = investing.apply(pd.to_numeric, errors='coerce')
        investing.insert(loc=0, column="mean", value=investing.mean(axis=1))
        investing = pd.concat([investing, self.company_value])
        print_table_title(f"{self.ticker} Investing Insights")
        print(investing.applymap(mix_number).to_string(max_rows=100, max_cols=100))

    def get_dfc_valuation(self):
        pass