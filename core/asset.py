import pandas as pd
import yfinance as yf


class Asset:
    def __init__(self, ticker):
        self.ticker = ticker
        self.ohlc = 'Open'
        self.daily_price = None
        self.daily_price_change = None

    def get_price(self, period='max', start_date=None, end_date=None):
        if self.daily_price or self.daily_price_change is None:
            data = yf.Ticker(self.ticker).history(period=period, interval='1d', start=start_date, end=end_date,
                                                  auto_adjust=False)[[self.ohlc]].dropna(axis=0, how='all')
            data = data.rename(columns={self.ohlc: self.ticker})
            self.daily_price = data[[self.ticker]][data[self.ticker] > 0.000001]
            self.daily_price_change = self.daily_price.pct_change().dropna(axis=0, how='all')

    def get_expected_daily_return_and_risk_from_all_history(self, start=None):
        if self.daily_price_change is None:
            self.get_price(start_date=start)
        return [self.daily_price_change[self.ticker].mean(), self.daily_price_change[self.ticker].std()]

