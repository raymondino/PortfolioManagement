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
        self.profitability = None
        self.operation = None
        self.solvency = None
        self.growth = None
        self.investing = None
        self.insights_summary = None
        self.dcf_valuation = 0

    def __get_company_value(self):
        if self.company_value is None:
            ev_url = f"https://financialmodelingprep.com/api/v3/enterprise-value/{self.ticker}"
            ev_items = ["date", "Stock Price", "Number of Shares", "Market Capitalization", "Enterprise Value"]
            data = requests.get(ev_url + ("?period=quarter" if self.quarter else "")).json()["enterpriseValues"]
            data = pd.DataFrame.from_dict(data)[ev_items]
            data = data[data.date.isin(self.balance_sheet.balance_sheet.columns)]
            self.company_value = data.set_index('date').T
            self.company_value = self.company_value[1:].apply(pd.to_numeric, errors="coerce")
        return self.company_value

    def __print__insights(self):
        print_table_title(f"{self.ticker} Profitability")
        print(self.profitability.applymap(percentify).to_string(max_rows=100, max_cols=100))
        print_table_title(f"{self.ticker} Operation")
        print(self.operation.applymap(decimalize).to_string(max_rows=100, max_cols=100))
        print_table_title(f"{self.ticker} Solvency")
        print(self.solvency.applymap(decimalize).to_string(max_rows=100, max_cols=100))
        print_table_title(f"{self.ticker} Growth")
        print(self.growth.applymap(percentify).to_string(max_rows=100, max_cols=100))
        print_table_title(f"{self.ticker} Investing")
        print(self.investing.applymap(mix_number).to_string(max_rows=100, max_cols=100))
        if not self.quarter:
            print_table_title(f"{self.ticker} DCF")
            print(f"${self.dcf_valuation}")
            if self.dcf_valuation < 0:
                print("might be WACC < 0.025, leading to the terminal value to be negative, thus DCF is negative")
                print("might be FCF or net income is negative, leading to negative future FCF, thus DCF is negative")

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
        if not self.quarter:
            self.get_dcf_valuation()
        self.__print__insights()

    def get_profitability_insights(self):
        if self.profitability is None:
            self.profitability = pd.concat([
                self.income_statement.data["Gross Margin"],
                self.income_statement.data["Cost of Revenue"] / self.income_statement.data["Revenue"],
                self.income_statement.data["Net Income"] / self.income_statement.data["Revenue"],
                self.income_statement.data["Operating Expenses"] / self.income_statement.data["Revenue"],
                self.income_statement.data["Net Income"] / self.balance_sheet.data["Total shareholders equity"],
                self.income_statement.data["Net Income"] / self.balance_sheet.data["Total assets"]
            ], axis=1)
            self.profitability.columns = [
                "Gross Margin", "Cost Margin", "Net Income Margin", "Expenses Margin", "ROE", "ROA"
            ]
            self.profitability = self.profitability.sort_index().iloc[:(self.year if not self.quarter else 3 * self.year)].T
            self.profitability.columns = self.balance_sheet.balance_sheet.columns
            self.profitability = self.profitability.replace([np.inf, -np.inf], 0).fillna(0)
            self.profitability.insert(loc=0, column="mean", value=self.profitability.mean(axis=1))

    def get_operation_insights(self):
        if self.operation is None:
            self.operation = pd.concat([
                365 / (self.income_statement.data["Revenue"] / self.balance_sheet.data["Receivables"].rolling(2).mean().shift(-1)),
                365 / (self.income_statement.data["Cost of Revenue"] / self.balance_sheet.data["Inventories"].rolling(2).mean().shift(-1)),
                356 / (self.income_statement.data["Revenue"] / self.balance_sheet.data["Total assets"].rolling(2).mean().shift(-1))
            ], axis=1)
            self.operation.columns = [
                "Receivables Turnover Days", "Inventories Turnover Days", "Total Assets Turnover Days"
            ]
            self.operation = self.operation.sort_index().iloc[:(self.year if not self.quarter else 3 * self.year)].T
            self.operation.columns = self.balance_sheet.balance_sheet.columns
            self.operation = self.operation.replace([np.inf, -np.inf], 0).fillna(0)
            self.operation.insert(loc=0, column="mean", value=self.operation.mean(axis=1))

    def get_solvency_insights(self):
        if self.solvency is None:
            self.solvency = pd.concat([
                self.balance_sheet.data["Total liabilities"] / self.balance_sheet.data["Total assets"],
                self.balance_sheet.data["Total current assets"] / self.balance_sheet.data["Total current liabilities"],
                (self.balance_sheet.data["Total current assets"] - self.balance_sheet.data["Inventories"]) / self.balance_sheet.data["Total current liabilities"]
            ], axis=1)
            self.solvency.columns = ["Liability/Asset Ratio", "Current Ratio", "Acid-test Ratio"]
            self.solvency = self.solvency.sort_index().iloc[:(self.year if not self.quarter else 3 * self.year)].T
            self.solvency = self.solvency.replace([np.inf, -np.inf], 0).fillna(0)
            self.solvency.columns = self.balance_sheet.balance_sheet.columns
            self.solvency.insert(loc=0, column="mean", value=self.solvency.mean(axis=1))

    def get_growth_insights(self):
        if self.growth is None:
            self.growth = pd.concat([
                self.income_statement.data["Revenue Growth"],
                self.income_statement.data["Net Income"].pct_change(-1).dropna()*np.sign(self.income_statement.data["Net Income"].shift(periods=-1).dropna()),
                self.income_statement.data["Operating Income"].pct_change(-1).dropna()*np.sign(self.income_statement.data["Operating Income"].shift(periods=-1).dropna()),
                self.cashflow_statement.data["Free Cash Flow"].pct_change(-1).dropna()*np.sign(self.cashflow_statement.data["Free Cash Flow"].shift(periods=-1).dropna())
            ], axis=1)
            self.growth.columns = [
                "Revenue Growth", "Net Income Growth", "Operating Income Growth", "Free Cash Flow Growth"
            ]
            self.growth = self.growth.sort_index().iloc[:(self.year if not self.quarter else 3 * self.year)].T
            self.growth = self.growth.replace([np.inf, -np.inf], 0).fillna(0)
            self.growth.columns = self.balance_sheet.balance_sheet.columns
            self.growth.insert(loc=0, column="mean", value=self.growth.mean(axis=1))

    def get_investing_insights(self, beta, risk_free_return):
        # find the 13 week T-bill return rate at https://finance.yahoo.com/bonds
        if self.investing is None:
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
            interest_rate = (self.income_statement.income_statement.loc["Interest Expense"] / total_debt).replace([np.inf, -np.inf], 0).fillna(0)
            income_tax = self.income_statement.income_statement.loc["Income Tax Expense"] / \
                         self.income_statement.income_statement.loc["Income Before Tax"]
            capm = risk_free_return + float(beta)*(market_return - risk_free_return)
            wacc = total_debt/(total_debt+market_cap)*interest_rate*(1-income_tax)+market_cap/(total_debt+market_cap)*capm
            invested_capital = total_debt + self.balance_sheet.balance_sheet.loc["Total shareholders equity"]
            roic = self.income_statement.income_statement.loc["Net Income"]/invested_capital
            excess_return = roic - wacc.apply(lambda x : x if x >= 0 else -x)

            economic_profit = excess_return * invested_capital
            self.investing = pd.concat([wacc, roic, excess_return, economic_profit], axis=1)
            self.investing.columns = ["wacc", "roic", "excess return", "economic profit"]
            self.investing["stockholders equity growth"] = self.balance_sheet.balance_sheet.loc["Total shareholders equity growth"]
            self.investing = pd.concat([self.investing.T, dividend])
            self.investing = self.investing.apply(pd.to_numeric, errors='coerce').replace([np.inf, -np.inf], 0).fillna(0)
            self.investing.insert(loc=0, column="mean", value=self.investing.mean(axis=1))
            self.investing = pd.concat([self.investing, self.company_value])

    def get_dcf_valuation(self):
        if self.dcf_valuation == 0:
            if self.profitability is None:
                self.get_profitability_insights()
            if self.growth is None:
                self.get_growth_insights()
            if self.investing is None:
                print("\nERROR: cannot get DFC valuation without running investing insights first")
                return
            try:
                current_outstanding_shares = self.__get_company_value().loc["Number of Shares"][0]
                latest_revenue = self.income_statement.income_statement.loc["Revenue"][0]
                average_revenue_growth_of_past_5_years = self.growth.loc["Revenue Growth"][0]
                average_net_income_margin_of_past_5_years = self.profitability.loc["Net Income Margin"][0]
                average_ratio_of_free_cash_flow_over_net_income = (self.cashflow_statement.cashflow_statement.loc["Free Cash Flow"]/self.income_statement.income_statement.loc["Net Income"]).mean()
                predicted_net_income_for_coming_5_years = [
                    latest_revenue * (1 + average_revenue_growth_of_past_5_years) * average_net_income_margin_of_past_5_years,
                    latest_revenue * (1 + average_revenue_growth_of_past_5_years) ** 2 * average_net_income_margin_of_past_5_years,
                    latest_revenue * (1 + average_revenue_growth_of_past_5_years) ** 3 * average_net_income_margin_of_past_5_years,
                    latest_revenue * (1 + average_revenue_growth_of_past_5_years) ** 4 * average_net_income_margin_of_past_5_years,
                    latest_revenue * (1 + average_revenue_growth_of_past_5_years) ** 5 * average_net_income_margin_of_past_5_years
                ]
                predicted_free_cash_flow_for_coming_5_years = [x * average_ratio_of_free_cash_flow_over_net_income for x in predicted_net_income_for_coming_5_years]
                perpectual_growth = 0.025
                average_wacc_of_past_5_years = self.investing.loc['wacc'][0]
                terminal_value = predicted_free_cash_flow_for_coming_5_years[4] / (average_wacc_of_past_5_years - perpectual_growth)
                predicted_value = 0
                for idx, val in enumerate(predicted_free_cash_flow_for_coming_5_years):
                    predicted_value += predicted_free_cash_flow_for_coming_5_years[idx]/(1+average_wacc_of_past_5_years)**(idx+1)

                predicted_value += terminal_value/(1+average_wacc_of_past_5_years)**5
                self.dcf_valuation = predicted_value / current_outstanding_shares if current_outstanding_shares != 0 else 0
            except Exception:
                self.dcf_valuation = -1

    def get_dcf_valuation_simple(self):
        if self.dcf_valuation == 0:
            if self.growth is None:
                self.get_growth_insights()
            try:
                current_outstanding_shares = self.__get_company_value().loc["Number of Shares"][0]
                average_fcf_growth = self.growth.loc["Free Cash Flow Growth"].mean()
                latest_fcf = self.cashflow_statement.cashflow_statement.loc["Free Cash Flow"][0]
                predicted_fcf = [
                    latest_fcf * (1 + average_fcf_growth),
                    latest_fcf * (1 + average_fcf_growth) ** 2,
                    latest_fcf * (1 + average_fcf_growth) ** 3,
                    latest_fcf * (1 + average_fcf_growth) ** 4,
                    latest_fcf * (1 + average_fcf_growth) ** 5
                ]
                perpectual_growth = 0.025
                average_wacc_of_past_5_years = self.investing.loc['wacc'][0]
                terminal_value = predicted_fcf[3] / (average_wacc_of_past_5_years - perpectual_growth)
                predicted_value = 0
                for idx, val in enumerate(predicted_fcf):
                    predicted_value += predicted_fcf[idx]/(1+average_wacc_of_past_5_years)**(idx+1)
                predicted_value += terminal_value/(1+average_wacc_of_past_5_years)**5
                self.dcf_valuation = predicted_value / current_outstanding_shares
            except Exception:
                self.dcf_valuation = -1

    def get_summary(self, beta, risk_free_return):
        if self.insights_summary is None:
            self.get_profitability_insights()
            self.get_operation_insights()
            self.get_solvency_insights()
            self.get_growth_insights()
            self.get_investing_insights(beta, risk_free_return)
            self.get_dcf_valuation()

        p = self.profitability[self.profitability.columns[0:2]]
        o = self.operation[self.operation.columns[0:2]]
        s = self.solvency[self.solvency.columns[0:2]]
        g = self.growth[self.growth.columns[0:2]]
        i = self.investing[self.investing.columns[0:2]]
        self.insights_summary = pd.concat([p, o, s, g, i], axis=0)
        self.insights_summary.loc["DCF"] = ["NaN", self.dcf_valuation]
        self.insights_summary.columns = pd.MultiIndex.from_tuples([(self.ticker, 'mean'), (self.ticker, 'latest')])