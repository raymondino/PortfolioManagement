import os
import json
import numpy as np
from core.portfolio import *
from scipy.optimize import minimize


def get_portfolio_performance(json_file_path, report_file_path, risk_free_return):
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
        qs.reports.html(p, "IVV", title=report_name, output=report_file_path, rf=risk_free_return)


def back_test_portfolio(asset_tickers, asset_weights, report_name, report_file_path, risk_free_return, initial_fund=10000):
    p = Portfolio()
    p.invest(asset_tickers, customized_weights=asset_tickers, ohlc="Close")
    p.asset_shares = np.ceil([x*initial_fund for x in asset_weights] / p.full_asset_price_history.iloc[0])
    book_value = p.full_asset_price_history*p.asset_shares
    print(f"invested           {book_value.iloc[0].sum()}")
    print(f"current book value {book_value.iloc[book_value.shape[0]-1].sum()}")
    qs.reports.html(book_value.sum(axis=1).pct_change().dropna(), "IVV", title=report_name, output=report_file_path, rf=risk_free_return)


def fund_allocation_optimizer(portfolios, risk_free_yearly_yield):
    returns = []
    names = []
    for name, p in portfolios.items():
        names.append(name)
        returns.append((p.full_asset_price_history_change*p.asset_weights).sum(axis=1))
    returns = pd.concat(returns, axis=1).dropna()

    def sharpe_ratio(param):
        daily_mean_return = np.matmul(param, returns.mean().to_numpy().transpose())
        daily_risk = np.sqrt(np.matmul(np.matmul(param, returns.cov().to_numpy()), param.transpose()))
        return -1 * (daily_mean_return - pow(1 + risk_free_yearly_yield, 1/365) + 1) / daily_risk
    param = np.array([1/len(names)]*len(names))
    bnds = tuple([(0, 1)] * (len(param)))
    cons = [{'type': 'eq', 'fun': lambda param: np.sum(param) - 1}]
    ans = minimize(sharpe_ratio, param, bounds=bnds, constraints=cons)
    optimized_daily_return = np.matmul(np.array(ans.x), returns.mean().to_numpy().transpose())
    optimized_daily_risk = np.sqrt(np.matmul(np.matmul(np.array(ans.x), returns.cov().to_numpy()), np.array(ans.x).transpose()))
    print("==============================")
    print(names)
    print(f"sharpe ratio optimized weights: {list(np.around(np.array(ans.x), 4))}")
    print(f"sharpe ratio optimized annualized return: {round(optimized_daily_return * 252, 6)}")
    print(f"sharpe ratio optimized annualized risk: {round(optimized_daily_risk * np.sqrt(252), 6)}")
    print(f"sharpe ratio: {round((252 * optimized_daily_return - (pow(1 + risk_free_yearly_yield, 1/365) - 1)) / (optimized_daily_risk * np.sqrt(252)), 6)}")

