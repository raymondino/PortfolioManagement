import pandas as pd
import seaborn as sns
from core.asset import *


class Portfolio:
    def __init__(self):
        self.assets = []
        self.asset_shares = {}
        self.asset_weights = []
        self.full_asset_price_history = None
        self.full_asset_price_history_change = None

    def invest(self, asset_tickers, strategy=None, customized_weights=None, show_details=False, show_plot=False,
               period=None, start_date=None, end_date=None):
        self.assets = []
        for ticker in asset_tickers:
            a = Asset(ticker)
            if period is not None:
                a.get_price(period=period)
            elif start_date or end_date is not None:
                a.get_price(start_date=start_date, end_date=end_date)
            else:
                a.get_price()
            self.assets.append(a)
            self.asset_shares[ticker] = 0

        if customized_weights is not None and len(customized_weights) == len(asset_tickers):
            self.asset_weights = customized_weights
        elif len(self.asset_weights) == 0:
            self.asset_weights = [1/len(asset_tickers)] * len(asset_tickers)

        self.full_asset_price_history = self.assets[0].daily_price
        self.full_asset_price_history_change = self.assets[0].daily_price_change
        for i in range(1, len(self.assets)):
            self.full_asset_price_history = pd.merge(self.full_asset_price_history, self.assets[i].daily_price, left_index=True, right_index=True)
            self.full_asset_price_history_change = pd.merge(self.full_asset_price_history_change, self.assets[i].daily_price_change, left_index=True, right_index=True)
        self.full_asset_price_history = self.full_asset_price_history.dropna(axis=0,how='all')
        self.full_asset_price_history_change = self.full_asset_price_history_change.dropna(axis=0,how='all')

        if strategy is not None:
            strategy.fit(self, customized_weights=customized_weights, show_details=show_details, show_plot=show_plot)

    def get_assets_correlation(self):
        return self.full_asset_price_history_change.corr(method="pearson")

    def get_assets_covariance(self):
        return self.full_asset_price_history_change.cov()

    def plot_asset_correlation(self):
       corr = self.get_assets_correlation()
       fig, ax = plt.subplots(figsize=(10, 10))
       colormap = sns.diverging_palette(220, 10, as_cmap=True)
       sns.heatmap(corr, cmap=colormap, annot=True, fmt=".4f")
       plt.xticks(range(len(corr.columns)), corr.columns)
       plt.yticks(range(len(corr.columns)), corr.columns)
       plt.show()

    def plot_asset_covariance(self):
        conv = self.get_assets_covariance()
        fig, ax = plt.subplots(figsize=(10, 10))
        colormap = sns.diverging_palette(220, 10, as_cmap=True)
        sns.heatmap(conv, cmap=colormap, annot=True, fmt=".4f")
        plt.xticks(range(len(conv.columns)), conv.columns)
        plt.yticks(range(len(conv.columns)), conv.columns)
        plt.show()