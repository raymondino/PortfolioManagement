import random
import yfinance as yf
import matplotlib.pyplot as plt


class Asset:
    def __init__(self, ticker, ohlc="Open", interval="1d"):
        self.ticker = ticker
        self.ohlc = ohlc
        self.interval = interval
        self.daily_price = None
        self.daily_price_change = None

    def get_price(self, period="5y", interval="1mo", start_date=None, end_date=None):
        data = yf.Ticker(self.ticker).history(period=period, interval=self.interval, start=start_date, end=end_date,
                                              auto_adjust=False)[[self.ohlc]].dropna(axis=0, how="all")
        data = data.rename(columns={self.ohlc: self.ticker})
        self.daily_price = data[[self.ticker]][data[self.ticker] > 0.000001]
        self.daily_price_change = self.daily_price.pct_change().dropna(axis=0, how="all")

    def get_expected_yearly_return_risk_beta(self, start=None):
        if self.daily_price_change is None:
            self.get_price(start_date=start)
        return [self.daily_price_change[self.ticker].mean()*252, self.daily_price_change[self.ticker].std()*pow(252, 1/2), self.get_beta()]

    # get 5-year monthly beta
    def get_beta(self, spy=None):
        if spy is None:
            spy = Asset("SPY", interval="1mo")
            spy.get_price()
        original_interval = self.interval
        self.interval = '1mo'
        self.get_price()
        self.interval = original_interval
        return (spy.daily_price_change["SPY"].cov(self.daily_price_change[self.ticker])/spy.daily_price_change.var())[0]

    @staticmethod
    def plot_yearly_return_risk(assets_list):
        if assets_list is None or len(assets_list) == 0:
            print("No assets passed")
            return
        fig = plt.figure(figsize=(15, 10))
        plots = []
        for asset in assets_list:
            try:
                a = Asset(asset)
                a.get_price()
                print(f"{a.ticker} annual return={round(a.daily_price_change.mean()[0]*252, 4)}, "
                      f"daily risk={round(a.daily_price_change.std()[0]*pow(252, 1/2), 4)}")
                clr = "#"+"".join([random.choice("0123456789ABCDEF") for j in range(6)])
                plots.append(plt.plot(a.daily_price_change.std(), a.daily_price_change.mean(), label=f"{a.ticker} 5Y",
                                      marker="^", color=clr))
                retn = a.daily_price_change.rolling("252D").mean()[252::253]
                risk = a.daily_price_change.rolling("252D").std()[252::253]
                plots.append(plt.scatter(x=risk, y=retn, s=15, alpha=0.8, color=clr, marker="x"))
            except Exception:
                print(f"ERROR: cannot get price data for {asset}")
        plt.title("252-day return and risk over past 5 years")
        plt.xlabel("risk")
        plt.ylabel("return")
        plt.legend(loc="best")
        plt.show()

    @staticmethod
    def print_yearly_return_risk(assets_list):
        if assets_list is None or len(assets_list) == 0:
            print("No assets passed")
            return
        for asset in assets_list:
            try:
                a = Asset(asset)
                a.get_price()
                retn = a.daily_price_change.rolling("252D").mean()[252::253].values.tolist()
                risk = a.daily_price_change.rolling("252D").std()[252::253].values.tolist()
                rr = [f"({round(x[0]*252*100, 5)}%,{round(y[0]*pow(252, 1/2)*100, 5)}%)" for (x, y) in zip(retn, risk)]
                print(f"{a.ticker}{(5-len(a.ticker))*' '}average annual return={round(a.daily_price_change.mean()[0]*252, 4)}, "
                      f"daily risk={round(a.daily_price_change.std()[0]*pow(252, 1/2), 4)}, {rr}")
            except Exception:
                print(f"ERROR: cannot get price data for {asset}")

