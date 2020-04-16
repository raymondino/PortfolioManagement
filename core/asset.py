import pandas as pd
import yfinance as yf


class Asset:
    def __init__(self, ticker):
        self.ticker = 0
        self.daily_price = None
        self.daily_price_change = None

    def get_price(self, period='max', start_date=None, end_date=None):
        data = yf.Ticker(self.ticker).history(period=period, interval='1d', start=start_date, end=end_date,
                                              auto_adjust=False)[[self.ohlc]].dropna(axis=0, how='all')
        data = data.rename(columns={'Open': self.ticker})
        self.daily_price = data[[self.ticker]][data[self.ticker] > 0.000001]
        self.daily_price_change = self.price.pct_change().dropna(axis=0, how='all')

