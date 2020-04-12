import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate


class Company:
    def __init__(self, ticker):
        # set up
        self.ticker = ticker
        self.data = yf.Ticker(ticker)
        self.info = self.data.info
        self.balance_sheet = self.data.balance_sheet
        self.income_statement = self.data.financials
        self.cash_flows_statement = self.data.cashflow

        # fundamentals
        self.revenue = self.income_statement.loc['Total Revenue']
        self.cost_of_revenue = self.income_statement.loc['Cost Of Revenue']
        self.gross_margin = self.income_statement.loc["Gross Profit"]
        self.Ebit = self.income_statement.loc['Ebit']
        self.interest_expense = self.income_statement.loc['Interest Expense']
        self.net_income = self.income_statement.loc['Net Income']
        self.income_tax = self.income_statement.loc['Income Tax Expense']
        self.income_before_tax = self.income_statement.loc['Income Before Tax']

        # assets
        self.cash = self.balance_sheet.loc['Cash']
        self.short_term_investment = self.balance_sheet.loc['Short Term Investments'] if "Short Term Investments" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.total_cash = self.cash + self.short_term_investment
        self.account_receivables = self.balance_sheet.loc['Net Receivables'] if "Net Receivables" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.inventories = self.balance_sheet.loc['Inventory'] if "Inventory" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.other_current_assets = self.balance_sheet.loc['Other Current Asset'] if "Other Current Asset" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.total_current_assets = self.balance_sheet.loc['Total Current Assets']
        self.fixed_assets = self.balance_sheet.loc['Property Plant Equipment']  # property, plant and equipment
        self.long_term_investments = self.balance_sheet.loc['Long Term Investments'] if "Long Term Investments" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns) # Equity and other investment
        self.good_will = self.balance_sheet.loc['Good Will'] if "Good Will" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.intangible_assets = self.balance_sheet.loc['Intangible Assets'] if "Intangible Assets" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.other_assets = self.balance_sheet.loc['Other Assets']  # other long-term assets
        self.total_assets = self.balance_sheet.loc["Total Assets"]

        # liabilities
        self.short_term_debt = self.balance_sheet.loc['Short Long Term Debt'] if "Short Long Term Debt" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)  # current debt
        self.accounts_payable = self.balance_sheet.loc['Accounts Payable'] if "Accounts Payable" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.total_current_liabilities = self.balance_sheet.loc['Total Current Liabilities']
        self.other_current_liabilities = self.total_current_liabilities - self.short_term_debt - self.accounts_payable
        self.long_term_debt = self.balance_sheet.loc['Long Term Debt'] if "Long Term Debt" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.total_liabilities = self.balance_sheet.loc["Total Liab"]
        self.other_non_current_liabilities = self.total_liabilities - self.total_current_liabilities - self.long_term_debt

        # stockholders' equity
        self.common_stock = self.balance_sheet.loc['Common Stock'] if "Common Stock" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.retained_earnings = self.balance_sheet.loc['Retained Earnings']
        self.total_stockholders_equity = self.balance_sheet.loc['Total Stockholder Equity']

    def print_balance_sheet(self, show_table=True):
        assets = pd.concat([self.cash.head(1), self.short_term_investment.head(1), self.total_cash.head(1),
                            self.account_receivables.head(1), self.inventories.head(1),
                            self.other_current_assets.head(1), self.total_current_assets.head(1),
                            self.fixed_assets.head(1), self.long_term_investments.head(1), self.good_will.head(1),
                            self.intangible_assets.head(1), self.other_assets.head(1),
                            self.total_assets.head(1)], axis=1)
        assets.columns = ["cash", "short term investments", "TOTAL CASH", "account receivables", "inventories",
                          "other current assets", "TOTAL CURRENT ASSETS", "fixed assets", "long term investments",
                          "good will", "intangible assets", "other assets", "TOTAL ASSETS"]
        assets = assets.transpose()
        assets.columns=[f"{self.ticker} assets value"]
        assets[f"{self.ticker} assets portion"] = round(assets[f"{self.ticker} assets value"] / self.total_assets.head(1).values[0], 2)
        liabilities = pd.concat([self.short_term_debt.head(1), self.accounts_payable.head(1),
                                 self.other_current_liabilities.head(1), self.total_current_liabilities.head(1),
                                 self.long_term_debt.head(1), self.other_non_current_liabilities.head(1),
                                 self.total_liabilities.head(1)], axis=1)
        liabilities.columns = ["short term debt", "accounts payable", "other current liabilities",
                               "TOTAL CURRENT LIABILITIES", "long term debt", "other non current liabilities",
                               "TOTAL LIABILITIES"]
        liabilities = liabilities.transpose()
        liabilities.columns=[f"{self.ticker} liabilities value"]
        liabilities[f"{self.ticker} liabilities portion"] = round(liabilities[f"{self.ticker} liabilities value"] / self.total_liabilities.head(1).values[0], 2)
        equity = pd.concat([self.common_stock.head(1), self.retained_earnings.head(1),
                            self.total_stockholders_equity.head(1)], axis=1)
        equity.columns = ["common stock", "retained earnings", "TOTAL STOCKHOLDERS' EQUITY"]
        equity = equity.transpose()
        equity.columns=[f"{self.ticker} stockholders' equity"]
        equity[f"{self.ticker} stockholders' equity portion"] = round(equity[f"{self.ticker} stockholders' equity"] / self.total_stockholders_equity.head(1).values[0], 2)
        if show_table:
            print(tabulate(assets, headers='keys', tablefmt='grid'))
            print(tabulate(liabilities, headers='keys', tablefmt='grid'))
            print(tabulate(equity, headers='keys', tablefmt='grid'))

        return assets, liabilities, equity

    def analyze_profitability(self, show_plot=False):
        # profitability analysis
        self.gross_margin_rate = self.gross_margin / self.revenue
        self.net_income_rate = self.net_income / self.revenue
        self.return_on_total_assets = self.net_income / self.total_assets

        profitability = pd.concat([self.gross_margin_rate, self.net_income_rate, self.return_on_total_assets], axis=1)
        profitability.columns = ["gross margin rate", "net income rate", "return on total assets"]
        print(f"{self.ticker} Profitability Analysis")
        print(tabulate(profitability, headers='keys', tablefmt='grid'))
        if show_plot:
            profitability["date"] = profitability.index.strftime('%Y-%m-%d')
            profitability.plot(x='date', kind="bar", figsize=(9, 6))
            plt.show()

    def analyze_operational_capability(self, show_plot=False):
        # operational capability analysis
        self.total_assets_turnover_rate = self.revenue / self.total_assets
        self.total_assets_turnover_days = 365 / self.total_assets_turnover_rate
        self.account_receivables_turnover_rate = self.revenue / self.account_receivables if "Net Receivables" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.account_receivables_turnover_days = 365 / self.account_receivables_turnover_rate if self.account_receivables_turnover_rate.sum() != 0 else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.inventories_turnover_rate = self.cost_of_revenue / self.inventories if "Inventory" in self.balance_sheet.index else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.inventories_turnover_days = 365 / self.inventories_turnover_rate if self.inventories_turnover_rate.sum() != 0 else pd.Series([0,0,0,0], index=self.balance_sheet.columns)
        self.current_assets_turnover_rate = self.revenue / self.total_current_assets
        self.current_assets_turnover_days = 365 / self.current_assets_turnover_rate
        self.fixed_assets_turnover_rate = self.revenue / self.fixed_assets
        self.fixed_assets_turnover_days = 365 / self.fixed_assets_turnover_rate

        operational_cap_days = pd.concat([self.account_receivables_turnover_days, self.inventories_turnover_days,
                                          self.current_assets_turnover_days, self.fixed_assets_turnover_days,
                                          self.total_assets_turnover_days], axis=1)
        operational_cap_days.columns = ['account receivables turnover days', 'inventories turn over days',
                                        'current assets turnover days', 'fixed assets turnover days',
                                        'total assets turnover days']
        print(f"{self.ticker} Operational Capability Analysis")
        print(tabulate(operational_cap_days, headers='keys', tablefmt='grid'))
        if show_plot:
            operational_cap_days["date"] = operational_cap_days.index.strftime('%Y-%m-%d')
            operational_cap_days.plot(x='date', kind="bar", table=True, figsize=(9, 6))
            plt.show()

    def analyze_solvency(self, show_plot=False):
        # solvency analysis
        self.current_ratio = self.total_current_assets / self.total_current_liabilities
        self.acid_test_ratio = (self.total_current_assets - self.inventories) / self.total_current_liabilities
        self.times_interest_earned = self.Ebit / self.interest_expense * -1
        self.asset_to_liability_ratio = self.total_liabilities / self.total_assets

        solvency = pd.concat([self.current_ratio, self.acid_test_ratio, self.times_interest_earned,
                              self.asset_to_liability_ratio], axis=1)
        solvency.columns = ['current ratio (short term solvency)', 'acid test ratio (short term solvency)',
                            'times interest earned (pay interest solvency)',
                            'asset-to-liability ratio (general solvency)']
        print(f"{self.ticker} Solvency Analysis")
        print(tabulate(solvency, headers='keys', tablefmt='grid'))
        if show_plot:
            solvency["date"] = solvency.index.strftime('%Y-%m-%d')
            solvency.plot(x='date', kind="bar", figsize=(9, 6))
            plt.show()

    def analyze_extreme_situations(self, show_plot=False):
        """
        This analysis assumes that the company has negative cashflow, and a portion of positive cashflow.
        """
        negative_cashflows = self.cash_flows_statement[self.cash_flows_statement < 0].sum()
        positive_cashflows = self.cash_flows_statement[self.cash_flows_statement > 0].sum()

        i = 0
        different_positive_cashflow_levels = []
        columns = []
        while (positive_cashflows.values[0]*i + negative_cashflows.values[0])/365 < 0:
            different_positive_cashflow_levels.append(self.total_cash/((positive_cashflows*i + negative_cashflows)/365).abs())
            columns.append(f"survival days with {round(i*100, 0)}% positive cashflow")
            i += 0.05

        survival_days = pd.concat(different_positive_cashflow_levels, axis=1).head(1)
        survival_days.columns = columns
        print(f"{self.ticker} Extreme Situtaion Surval Anlaysis")
        print(tabulate(survival_days, headers='keys', tablefmt='grid'))
        if show_plot:
            survival_days["date"] = survival_days.index.strftime('%Y-%m-%d')
            survival_days.plot(x='date', kind="bar", figsize=(9, 6))
            plt.show()

    def analyze_investment_value(self, risk_free_return, latest_five_years_stock_market_return, show_plot=False):
        """
        This analysis calculates return on invest capital (ROIC), excess return, and economic profit
        :param risk_free_return: use T-bill 3 month return. Look it up here:
        https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield
        :param latest_five_years_stock_market_return: use any S&P 500 ETF past 5 year return.
        """
        wacc, roic, excess_return, economic_profit = self.__get_excess_return_and_economic_profit(risk_free_return, latest_five_years_stock_market_return)

        # this method is only valid for the latest WACC, ROIC, as it uses the latest enterprise value (market cap).
        invest_value_of_company = pd.concat([wacc, roic, excess_return, economic_profit], axis=1).head(1)
        invest_value_of_company.columns = ["WACC", "ROIC", "excess return", "economic profit"]
        print(f"{self.ticker} Investment Value Analysis")
        print(tabulate(invest_value_of_company, headers='keys', tablefmt='grid'))
        if show_plot:
            invest_value_of_company["date"] = invest_value_of_company.index.strftime('%Y-%m-%d')
            invest_value_of_company.plot(x='date', kind="bar", figsize=(9, 6))
            plt.show()

    def __get_excess_return_and_economic_profit(self, risk_free_return, latest_five_years_stock_market_return):
        # calculate weighted average capital cost (WACC)

        # to deal with missing data for short & long debt, I used an estimation for the missing values
        # this estimation will take non-empty values average to fill in the missing values
        short_term_debt_estimation_for_missing_value = 0 if self.short_term_debt.isna().sum() == self.short_term_debt.shape[0] else self.short_term_debt.sum() / (self.short_term_debt.shape[0] -self.short_term_debt.isna().sum() )
        long_term_debt_estimation_for_missing_value = 0 if self.long_term_debt.isna().sum() == self.long_term_debt.shape[0] else self.long_term_debt.sum() / (self.long_term_debt.shape[0] -self.long_term_debt.isna().sum() )

        interest_earning_debt = self.short_term_debt.fillna(short_term_debt_estimation_for_missing_value) + self.long_term_debt.fillna(long_term_debt_estimation_for_missing_value)
        company_market_capital = self.info['marketCap']
        interest_rate = 0 if interest_earning_debt.sum() == 0 else self.interest_expense / interest_earning_debt * -1
        income_tax = self.income_tax / self.income_before_tax
        if self.info["beta"] is None:
            print(f"ERROR: cannot calculate WACC for {self.ticker} because beta is not found")
            return pd.Series([0,0,0,0]), pd.Series([0,0,0,0]), pd.Series([0,0,0,0]), pd.Series([0,0,0,0])
        average_equity_capital_cost = risk_free_return + self.info['beta']*(latest_five_years_stock_market_return - risk_free_return)  # this is CAPM model)
        wacc = interest_earning_debt/(interest_earning_debt + company_market_capital) * interest_rate * (1 - income_tax) + company_market_capital/(interest_earning_debt + company_market_capital) * average_equity_capital_cost

        # calculate return on invested capital (ROIC)
        invested_capital = interest_earning_debt + self.total_stockholders_equity
        roic = self.net_income / invested_capital

        # excess return and economic profit
        excess_return = roic - wacc
        economic_profit = excess_return * invested_capital

        return wacc, roic, excess_return, economic_profit

    @staticmethod
    def choose_stock_based_on_excess_return(company_tickers_list, risk_free_return, latest_five_years_stock_market_return, show_plot=False):
        company_list = []
        for ticker in company_tickers_list:
            try:
                company_list.append(Company(ticker))
            except Exception:
                print(f" - {ticker} has problems when loading from yahoo finance")
        company_excessreturn_economicprofit = []
        for a_company in company_list:
            try:
                wacc, roic, excess_return, economic_profit = a_company.__get_excess_return_and_economic_profit(risk_free_return, latest_five_years_stock_market_return)
                company_excessreturn_economicprofit.append([a_company.ticker, wacc.head(1), roic.head(1), excess_return.head(1).values[0], economic_profit.head(1).values[0]])
            except Exception:
                print(f" - {a_company.ticker} has problems when calculating excess returns")
        dataframe = pd.DataFrame(company_excessreturn_economicprofit)
        dataframe.columns = ["ticker","wacc", "roic", "excess return", "economic profit"]
        dataframe = dataframe.sort_values(by="excess return", ascending=False)
        dataframe = dataframe.reset_index(drop=True)
        print(f"Companies ordered by their excess returns")
        print(tabulate(dataframe, headers='keys', tablefmt='grid'))
        if show_plot:
            dataframe.plot(x='ticker', y='excess return', kind="bar", figsize=(9, 6))
            plt.show()

    @staticmethod
    def compare_companies_balance_sheet(company_ticker_list):
        assets = []
        liabilities = []
        equities = []
        for ticker in company_ticker_list:
            try:
                com = Company(ticker)
                a, l, e = com.print_balance_sheet(show_table=False)
                assets.append(a)
                liabilities.append(l)
                equities.append(e)
            except Exception:
                print(f" - {ticker} has problems when loading from yahoo finance")
        assets = pd.concat(assets, axis=1)
        liabilities = pd.concat(liabilities, axis=1)
        equities = pd.concat(equities, axis=1)
        print(tabulate(assets, headers='keys', tablefmt='grid'))
        print(tabulate(liabilities, headers='keys', tablefmt='grid'))
        print(tabulate(equities, headers='keys', tablefmt='grid'))












