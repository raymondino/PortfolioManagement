import datetime as dt
import seaborn as sns
from datetime import datetime
from core.asset import *
from common.financial_insight import *


class Company:
    spy = Asset("SPY", interval="1mo")
    spy.get_price()

    def __init__(self, ticker, quarter=False, year=5):
        self.ticker = ticker
        self.quarter=quarter
        self.year = year
        self.financial_insights = None
        self.beta = 0
        self.industry = ""
        self.current_market_cap = ""
        self.current_price = ""
        self.sector = ""
        self.stock_average_annual_return = 0
        self.stock_average_annual_risk = 0
        try_times = 0
        try:
            while try_times < 3:
                data = requests.get(f"https://financialmodelingprep.com/api/v3/company/profile/{ticker}").json()[
                    "profile"]
                self.beta = data['beta']
                self.industry = data['industry']
                self.current_market_cap = data['mktCap']
                self.current_price = data['price']
                self.sector = data['sector']
                stock = Asset(self.ticker, interval="1mo")
                stock.get_price()
                self.beta = stock.get_beta(spy=Company.spy)
                self.stock_average_annual_return = stock.daily_price_change.mean()[0]*12  # it's monthly data
                self.stock_average_annual_risk = stock.daily_price_change.std()[0] * pow(12, 1/2)
                print(f" -- {self.ticker} got 5 year monthly, annual return & risk")
                break
        except Exception as e:
            print(f" -- {self.ticker} cannot get price/profile/beta/return/risk, retrying")

            try_times += 1

    def print_financials(self):
        if self.financial_insights is None:
            self.financial_insights = FinancialInsight(self.ticker, quarter=self.quarter, year=self.year)
        self.financial_insights.print_financials()

    def print_quantitative_analysis(self, risk_free_return):
        if self.financial_insights is None:
            self.financial_insights = FinancialInsight(self.ticker)
        self.financial_insights.print_quantitative_fundamentals(self.beta, risk_free_return)

    def get_fundamentals_summary(self, risk_free_return):
        if self.financial_insights is None:
            self.financial_insights = FinancialInsight(self.ticker)
        self.financial_insights.get_summary(self.beta, risk_free_return)
        return self.financial_insights.insights_summary

    def serialize_fundamentals_summary(self, risk_free_return):
        if self.financial_insights is None:
            self.financial_insights = FinancialInsight(self.ticker)
        self.financial_insights.get_summary(self.beta, risk_free_return)
        return f"{self.ticker}\t{self.current_market_cap}\t{self.industry}\t{self.sector}\t{self.current_price}\t" + \
               '\t'.join([str(x) for x in self.financial_insights.insights_summary[(self.ticker, "mean")][0:22].values])\
               + f"\t{self.financial_insights.dcf_valuation}\t{self.beta}\t{self.stock_average_annual_return}" \
                 f"\t{self.stock_average_annual_risk}\n"

    def plot_stock_price_with_revenue(self, quarter=True):
        if self.financial_insights is None:
            self.financial_insights = FinancialInsight(self.ticker, quarter=quarter, year=self.year)
        dates = self.financial_insights.balance_sheet.balance_sheet.columns
        updated_dates = []  # it's possible that earning call day happens at off-market date, so need to adjust the date
        c = Asset(self.ticker, ohlc="Close")
        c.get_price()
        for date in dates:
            # earning call usually happens 1 months after each quarter, so need to offset 21 days for the stock price
            date = (datetime.strptime(date, "%Y-%m-%d") + dt.timedelta(days=21)).strftime("%Y-%m-%d")
            while date not in c.daily_price.index:  # in case any date is not trading day, use the next trading day
                date = (datetime.strptime(date, "%Y-%m-%d") + dt.timedelta(days=1)).strftime("%Y-%m-%d")
            updated_dates.append(date)  # silent assumption: the date order is from most recent to least recent

        revenue = self.financial_insights.income_statement.income_statement.loc["Revenue"]
        net_income = self.financial_insights.income_statement.income_statement.loc["Net Income"]
        operating_income = self.financial_insights.income_statement.income_statement.loc["Operating Income"]
        free_cash_flow = self.financial_insights.cashflow_statement.cashflow_statement.loc["Free Cash Flow"]
        revenue.index = updated_dates  # silent assumption: the date order is from most recent to least recent
        net_income.index = updated_dates  # silent assumption: the date order is from most recent to least recent
        operating_income.index = updated_dates  # silent assumption: the date order is from most recent to least recent
        free_cash_flow.index = updated_dates  # silent assumption: the date order is from most recent to least recent
        c_stock_price_at_earning_call_dates = c.daily_price[c.daily_price.index.isin(updated_dates)][self.ticker].sort_index(ascending=False)
        c_stock_price_at_earning_call_dates.index = updated_dates
        data = pd.concat([c_stock_price_at_earning_call_dates, revenue, net_income, operating_income, free_cash_flow], axis=1).iloc[::-1]

        xs = data.index.values.tolist()
        ys = data['Revenue'].values.tolist()
        zs = data[self.ticker].values.tolist()

        fig, ax = plt.subplots()
        ax.bar(xs, ys, color="red")
        ax.set_xlabel("year", fontsize=14)
        ax.set_ylabel("Revenue", color="red", fontsize=14)
        ax2 = ax.twinx()
        ax2.plot(xs, zs, color="blue", marker="o")
        ax2.set_ylabel("Stock Price", color="blue", fontsize=14)
        for x, y in zip(xs, zs):
            label = "{:.2f}".format(y)
            plt.annotate(label,  # this is the text
                         (x, y),  # this is the point to label
                         textcoords="offset points",  # how to position the text
                         xytext=(0, 10),  # distance from text to points (x,y)
                         ha='center')  # horizontal alignment can be left, right or center

        for i, v in enumerate(ys):
            ax.text(i - .35,
                      v / ys[i] + 1000,
                      f"{round(ys[i]/1000000000, 4)} B",
                      fontsize=8,
                      fontweight='bold',
                      color='white')
        plt.title(f"{self.ticker} Price and Revenue")

        corr = data.corr()
        fig, ax = plt.subplots()
        colormap = sns.diverging_palette(220, 10, as_cmap=True)
        sns.heatmap(corr, cmap=colormap, annot=True, fmt=".4f")
        plt.xticks(range(len(corr.columns)), corr.columns)
        plt.yticks(range(len(corr.columns)), corr.columns)
        plt.show()