import yfinance as yf


class AssetFactory():
    @staticmethod
    def get_asset(ticker, ohlc="Open", period='max', interval='1mo', start=None, end=None):
        asset = Asset()
        return asset.set_ticker(ticker).set_ohlc(ohlc).set_period(period).set_start_date(start).set_end_date(end).set_interval(interval).get_data()


class Asset:
    def __init__(self):
        self.ticker = None
        self.ohlc = None
        self.period = None
        self.interval = None
        self.start_date = None
        self.end_date = None
        self.price = None
        self.price_change = None

    def set_ticker(self, t):
        self.ticker = t
        return self

    def set_ohlc(self, o):
        self.ohlc = o
        return self

    def set_period(self, p):
        self.period = p
        return self

    def set_interval(self, i):
        self.interval = i
        return self

    def set_start_date(self, s):
        self.start_date = s
        return self

    def set_end_date(self, e):
        self.end_date = e
        return self

    def get_data(self):
        data = yf.Ticker(self.ticker).history(period=self.period, interval=self.interval, start=self.start_date, end=self.end_date, auto_adjust=False)[[self.ohlc]].dropna(axis=0, how='all')
        data = data.rename(columns={self.ohlc: self.ticker})
        self.price = data[[self.ticker]][data[self.ticker] > 0.000001]
        self.price_change = self.price.pct_change().dropna(axis=0, how='all')
        return self
