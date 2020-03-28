import yfinance as yf


class Asset:
    def __init__(self, ticker):
        """
        This function will get the adjusted close price for a stock. Will get the full history of daily adjust
        stock price.
        :param ticker: stock ticker name
        """
        self.ticker = ticker
        self.ohlc = "Open"  # Adj Close
        # self.data = yf.Ticker(ticker).history(interval="1mo", start="2009-12-01", end="2019-12-01", auto_adjust=False)[[self.ohlc]].dropna(axis=0,how='all')
        self.data = yf.Ticker(ticker).history(period="max", interval="1mo", auto_adjust=False)[[self.ohlc]].dropna(axis=0,how='all')
        self.data = self.data.rename(columns={self.ohlc: self.ticker})
        self.data = self.data[(self.data[[self.ticker]] != 0).all(axis=1)]  # remove 0 valued price
        self.data["Date"] = self.data.index
        self.data[self.ticker+"_shift"] = self.data[self.ticker].shift(1)
        self.data[self.ticker+"_change"] = self.data[self.ticker]/self.data[self.ticker+"_shift"]-1
        self.price = self.data[[self.ticker]]
        self.price_change = self.data[[self.ticker+"_change"]]
