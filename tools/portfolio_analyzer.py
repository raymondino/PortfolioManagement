import os
import json
import numpy as np
from core.portfolio import *
from scipy.optimize import minimize


def get_portfolio_performance(json_file_path, report_name, report_file_path, risk_free_return, target_weights):
    if not os.path.exists(json_file_path):
        print(f"cannot load data from {json_file_path}")
        return

    with open(json_file_path, encoding='utf-8') as fp:
        data = pd.DataFrame.from_dict(json.load(fp))
        data = data.set_index(data['date'])[data.columns[1:]]
        cost = data.apply(lambda x: x.apply(lambda y: y['price']*y['share']))
        shares = data.apply(lambda x: x.apply(lambda y: y['share']))
        average_cost_basis = cost.sum() / shares.sum()

        daily_prices = []
        daily_change_index = None
        for c in data.columns:
            a = Asset(c, ohlc="Close")
            a.get_price(start_date=data.index[0])  # assuming the 1st index is the 1st invest day
            daily_prices.append(a.daily_price)
            if daily_change_index is None:
                daily_change_index = a.daily_price_change.index

        daily_prices = pd.concat(daily_prices, axis=1)
        book_value = []
        book_value_change = []

        cur_shares = pd.Series([0]*len(data.columns)).reindex(data.columns, fill_value=0)
        for i in range(len(daily_prices)):
            date = daily_prices.index[i].strftime("%Y-%m-%d")
            if date in data.index:
                cur_shares += shares.loc[date]
                book_value.append(cur_shares * daily_prices.iloc[i])
                if i > 0:
                    book_value_change.append(book_value[-1].sum()/(book_value[-2].sum() + (shares.loc[date] * daily_prices.iloc[i]).sum()) - 1)

            elif i > 0:
                book_value.append(cur_shares*daily_prices.iloc[i])
                book_value_change.append(book_value[-1].sum() / book_value[-2].sum() - 1)

        book_value = pd.concat(book_value, axis=1)
        book_value_change = pd.Series(book_value_change)
        book_value_change.index = daily_change_index
        print(f"current invest = {cost.sum().sum()}")
        print(f"current book   = {round(book_value.iloc[:,-1].sum(), 2)}")
        print(f"current profit = {round(book_value.iloc[:,-1].sum() - cost.sum().sum(), 2)}")
        print(f"current assets = {data.columns.values.tolist()}")
        print(f"current cost basis    = {[round(v, 2) for v in average_cost_basis.values.tolist()]}")
        print(f"current price (close) = {daily_prices.iloc[-1].values.tolist()}")
        print(f"price - cost basis    = {[round(v, 2) for v in (daily_prices.iloc[-1] - average_cost_basis).values.tolist()]}")
        print(f"target weights  = {target_weights}")
        print(f"current weights = {[round(v, 4) for v in (book_value.iloc[:,-1]/book_value.iloc[:,-1].sum()).values.tolist()]}")
        qs.reports.html(book_value_change, "IVV", title=report_name, output=report_file_path, rf=risk_free_return)


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

