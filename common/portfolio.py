import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from common.asset import *


class Portfolio:
    def __init__(self):
        self.assets = []
        self.asset_shares = {}
        self.asset_weights = []
        self.full_asset_price_history = []
        self.full_asset_price_history_change = []

    def invest(self, asset_tickers, period=None, start_date=None, end_date=None):
        for ticker in asset_tickers:
            self.assets.append(AssetFactory.get_asset(ticker, period=period, start=start_date, end=end_date))
            self.asset_shares[ticker] = 0
        self.asset_weights = [1/len(asset_tickers)] * len(asset_tickers) if len(asset_tickers) > 0 and len(self.asset_weights) == 0 else self.asset_weights

        self.full_asset_price_history = self.assets[0].price
        self.full_asset_price_history_change = self.assets[0].price_change
        for i in range(1, len(self.assets)):
            self.full_asset_price_history = pd.merge(self.full_asset_price_history, self.assets[i].price, left_index=True, right_index=True)
            self.full_asset_price_history_change = pd.merge(self.full_asset_price_history_change, self.assets[i].price_change, left_index=True, right_index=True)
        self.full_asset_price_history = self.full_asset_price_history.dropna(axis=0,how='all')
        self.full_asset_price_history_change = self.full_asset_price_history_change.dropna(axis=0,how='all')
        return self

    def using_strategy(self, investing_strategy, show_details=False, show_plots=False):
        investing_strategy.fit(self, show_details, show_plots)
        return self

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