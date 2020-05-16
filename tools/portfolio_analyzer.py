import os
import json
import numpy as np
from core.portfolio import *


def get_portfolio_performance(json_file_path, report_file_path):
    if not os.path.exists(json_file_path):
        print(f"cannot load data from {json_file_path}")
        return
    assets = []
    asset_tickers = []
    with open(json_file_path, encoding='utf-8') as fp:
        data = json.load(fp)
        report_name = data["name"]
        start_date = data["date"]
        for asset in data["assets"]:
            asset_tickers.append(asset["ticker"])
            a = Asset(asset["ticker"], ohlc="Close")
            a.get_price(start_date=start_date)
            a.daily_price.iloc[0] = asset["price"]
            assets.append(a.daily_price*asset["shares"])

        # portfolio = Portfolio()
        # portfolio.invest(asset_tickers, start_date=start_date)
        assets = pd.concat(assets, axis=1)
        # book_value = assets.sum(axis=1)
        # for i in range(0, assets.shape[0]):
        #     weights = (assets.iloc[i] / book_value[i]).values.tolist()
        p = assets.sum(axis=1).pct_change().dropna()
        qs.reports.html(p, "IVV", title=report_name, output=report_file_path)


def back_test_portfolio(asset_tickers, asset_weights, report_name, report_file_path, initial_fund=10000):
    p = Portfolio()
    p.invest(asset_tickers, customized_weights=asset_tickers)
    p.asset_shares = np.ceil([x*initial_fund for x in asset_weights] / p.full_asset_price_history.iloc[0])
    book_value = p.full_asset_price_history*p.asset_shares
    print(f"invested           {book_value.iloc[0].sum()}")
    print(f"current book value {book_value.iloc[book_value.shape[0]-1].sum()}")
    qs.reports.html(book_value.sum(axis=1).pct_change().dropna(), "IVV", title=report_name, output=report_file_path)