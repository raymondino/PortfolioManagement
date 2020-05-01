import yfinance as yf


class Asset:
    def __init__(self, ticker):
        self.ticker = ticker
        self.ohlc = "Open"
        self.daily_price = None
        self.daily_price_change = None

    def get_price(self, period="5y", start_date=None, end_date=None):
        if self.daily_price or self.daily_price_change is None:
            data = yf.Ticker(self.ticker).history(period=period, interval="1d", start=start_date, end=end_date,
                                                  auto_adjust=False)[[self.ohlc]].dropna(axis=0, how="all")
            data = data.rename(columns={self.ohlc: self.ticker})
            self.daily_price = data[[self.ticker]][data[self.ticker] > 0.000001]
            self.daily_price_change = self.daily_price.pct_change().dropna(axis=0, how="all")

    def get_expected_daily_return_and_risk(self, start=None):
        if self.daily_price_change is None:
            self.get_price(start_date=start)
        return [self.daily_price_change[self.ticker].mean(), self.daily_price_change[self.ticker].std()]

    def get_beta(self, year=5):
        spy = Asset("SPY")
        spy.get_price()
        if self.daily_price_change is None:
            self.get_price()
        return (spy.daily_price_change["SPY"].cov(self.daily_price_change[self.ticker])/spy.daily_price_change.var())[0]
