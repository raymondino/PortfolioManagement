import numpy as np
import pandas as pd
import matplotlib.pylab as pl
from scipy.optimize import minimize
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt


class MPT:
    def __init__(self, risk_free_annual_yield=None):
        self.portfolio = None
        self.risk_free_daily_yield = 0
        if risk_free_annual_yield is not None:
            self.risk_free_daily_yield = pow(1 + risk_free_annual_yield, 1/365) - 1

    def fit(self, portfolio, customized_weights=[], show_details=True, show_plot=False):
        self.portfolio = portfolio
        self.plot_efficient_frontier(show_details, show_plot, customized_weights)

    def get_stats(self, weights):
        yearly_expected_return = round(np.matmul(np.array(weights), self.portfolio.full_asset_price_history_change.mean().to_numpy().transpose())*252, 6)
        yearly_risk = round(np.sqrt(np.matmul(np.matmul(np.array(weights), self.portfolio.get_assets_covariance().to_numpy()), np.array(weights).transpose()))*np.sqrt(252), 6)
        yearly_sharpe_ratio = (yearly_expected_return - self.risk_free_daily_yield) / yearly_risk
        return yearly_expected_return, yearly_risk, yearly_sharpe_ratio

    def get_sortino_ratio(self, weights):
        portfolio_daily_return = (weights * self.portfolio.full_asset_price_history_change).sum(axis=1)
        sortino_optimized_portfolio_mean_return = portfolio_daily_return.mean() - self.risk_free_daily_yield
        sortino_optimized_portfolio_risk = np.sqrt(((portfolio_daily_return[portfolio_daily_return < self.risk_free_daily_yield]-self.risk_free_daily_yield)**2).sum() / len(portfolio_daily_return))
        sortino_ratio = (sortino_optimized_portfolio_mean_return / sortino_optimized_portfolio_risk)
        return sortino_optimized_portfolio_mean_return, sortino_ratio

    def plot_efficient_frontier(self, show_details, show_plots, customized_weights=None):
        # step 1: calculate the man-variance for the optimized portfolio
        risk_optimized_weights = self.__optimize_risk() if customized_weights == None or len(customized_weights) == 0 else customized_weights
        risk_optimized_portfolio_mean = np.matmul(np.array(risk_optimized_weights), self.portfolio.full_asset_price_history_change.mean().to_numpy().transpose())
        risk_optimized_portfolio_risk = np.sqrt(np.matmul(np.matmul(np.array(risk_optimized_weights), self.portfolio.get_assets_covariance().to_numpy()), np.array(risk_optimized_weights).transpose()))

        sharpe_optimized_weights = self.__optimize_sharpe_ratio() if customized_weights == None or len(customized_weights) == 0 else customized_weights
        sharpe_optimized_portfolio_mean = np.matmul(np.array(sharpe_optimized_weights), self.portfolio.full_asset_price_history_change.mean().to_numpy().transpose())
        sharpe_optimized_portfolio_risk = np.sqrt(np.matmul(np.matmul(np.array(sharpe_optimized_weights), self.portfolio.get_assets_covariance().to_numpy()), np.array(sharpe_optimized_weights).transpose()))

        sortino_optimized_weights = self.__optimize_sortino_ratio() if customized_weights == None or len(customized_weights) == 0 else customized_weights
        portfolio_daily_return = (sortino_optimized_weights * self.portfolio.full_asset_price_history_change).sum(axis=1)
        sortino_optimized_portfolio_mean = portfolio_daily_return.mean() - self.risk_free_daily_yield
        sortino_optimized_portfolio_risk = np.sqrt(((portfolio_daily_return[portfolio_daily_return < self.risk_free_daily_yield]-self.risk_free_daily_yield)**2).sum() / len(portfolio_daily_return))

        # step 2: report
        if show_details:
            print("======MPT optimization========")
            print(f"investing assets: {[asset.ticker for asset in self.portfolio.assets]}")
            print(f"risk optimized weights: {list(np.around(np.array(risk_optimized_weights),4))}")
            print(f"risk optimized annualized return: {round(risk_optimized_portfolio_mean*252, 6)}")  # there about 252 trading days per year
            print(f"risk optimized annualized risk: {round(risk_optimized_portfolio_risk*np.sqrt(252), 6)}")
            print("==============================")
            print(f"sortino ratio optimized weights: {list(np.around(np.array(sortino_optimized_weights), 4))}")
            print(f"sortino ratio daily: {round((sortino_optimized_portfolio_mean / sortino_optimized_portfolio_risk), 6)}")
            print(f"sortino ratio annualized: {round((sortino_optimized_portfolio_mean * pow(252, 1/2) / sortino_optimized_portfolio_risk), 6)}")

        # step 3: if allocating risk free asset
        mean1 = []
        std1 = []
        if self.risk_free_daily_yield > 0:
            for w in np.arange(0, 1.01, 0.01):
                mean1.append(np.matmul(np.array([w, 1-w]), np.array([self.risk_free_daily_yield, sharpe_optimized_portfolio_mean]).transpose()))
                std1.append((1-w) * sharpe_optimized_portfolio_risk)
            if show_details:
                print("==============================")
                print(f"sharpe ratio optimized weights: {list(np.around(np.array(sharpe_optimized_weights), 4))}")
                print(f"sharpe ratio optimized annualized return: {round(sharpe_optimized_portfolio_mean * 252, 6)}")
                print(f"sharpe ratio optimized annualized risk: {round(sharpe_optimized_portfolio_risk * np.sqrt(252), 6)}")
                print(f"sharpe ratio: {round((252 * sharpe_optimized_portfolio_mean - self.risk_free_daily_yield) / (sharpe_optimized_portfolio_risk * np.sqrt(252)), 6)}")
                print("==============================")
                print(f"allocate 10% risk free asset: annualized return = {round(mean1[11]*252,6)}, annualized risk = {round(std1[11]*np.sqrt(252),6)}")
                print(f"allocate 15% risk free asset: annualized return = {round(mean1[16]*252,6)}, annualized risk = {round(std1[16]*np.sqrt(252),6)}")
                print(f"allocate 20% risk free asset: annualized return = {round(mean1[21]*252,6)}, annualized risk = {round(std1[21]*np.sqrt(252),6)}")
                print(f"allocate 25% risk free asset: annualized return = {round(mean1[26]*252,6)}, annualized risk = {round(std1[26]*np.sqrt(252),6)}")
                print(f"allocate 30% risk free asset: annualized return = {round(mean1[31]*252,6)}, annualized risk = {round(std1[31]*np.sqrt(252),6)}")
                print(f"allocate 35% risk free asset: annualized return = {round(mean1[36]*252,6)}, annualized risk = {round(std1[36]*np.sqrt(252),6)}")
                print(f"allocate 40% risk free asset: annualized return = {round(mean1[41]*252,6)}, annualized risk = {round(std1[41]*np.sqrt(252),6)}")
                print(f"allocate 45% risk free asset: annualized return = {round(mean1[46]*252,6)}, annualized risk = {round(std1[46]*np.sqrt(252),6)}")
                print(f"allocate 50% risk free asset: annualized return = {round(mean1[51]*252,6)}, annualized risk = {round(std1[51]*np.sqrt(252),6)}")
                print(f"allocate 55% risk free asset: annualized return = {round(mean1[56]*252,6)}, annualized risk = {round(std1[56]*np.sqrt(252),6)}")
                print(f"allocate 60% risk free asset: annualized return = {round(mean1[61]*252,6)}, annualized risk = {round(std1[61]*np.sqrt(252),6)}")
                print(f"allocate 65% risk free asset: annualized return = {round(mean1[66]*252,6)}, annualized risk = {round(std1[66]*np.sqrt(252),6)}")
                print(f"allocate 70% risk free asset: annualized return = {round(mean1[71]*252,6)}, annualized risk = {round(std1[71]*np.sqrt(252),6)}")
                print(f"allocate 75% risk free asset: annualized return = {round(mean1[76]*252,6)}, annualized risk = {round(std1[76]*np.sqrt(252),6)}")
                print(f"allocate 80% risk free asset: annualized return = {round(mean1[81]*252,6)}, annualized risk = {round(std1[81]*np.sqrt(252),6)}")
                print(f"allocate 85% risk free asset: annualized return = {round(mean1[86]*252,6)}, annualized risk = {round(std1[86]*np.sqrt(252),6)}")
                print(f"allocate 90% risk free asset: annualized return = {round(mean1[91]*252,6)}, annualized risk = {round(std1[91]*np.sqrt(252),6)}")
                print(f"allocate 95% risk free asset: annualized return = {round(mean1[96]*252,6)}, annualized risk = {round(std1[96]*np.sqrt(252),6)}")

        # step 4: plot mean-variance curve and capital market line
        if show_plots:
            # step 4.1: get the combination list of weights
            def get_all_weight_combo(cur_weight, weight_combos):
                if 1 - sum(cur_weight) < 0:
                    return
                if len(cur_weight) == len(self.portfolio.assets) - 1:
                    cur_weight.append(round(1 - sum(cur_weight), 2))
                    weight_combos.append(cur_weight.copy())
                    del cur_weight[-1]
                    return
                for i in np.arange(0, 1 - sum(cur_weight) + 0.01, 0.01):
                    cur_weight.append(round(i, 2))
                    get_all_weight_combo(cur_weight, weight_combos)
                    del cur_weight[-1]

            weight_combos = []
            get_all_weight_combo([], weight_combos)

            # step 4.2: calculate portfolio return and risk for mean-variance curve
            # for loop will be slow when plotting >= 4 assets
            mean = []
            std = []
            for weights in weight_combos:
                mean.append(np.matmul(np.array(weights), self.portfolio.full_asset_price_history_change.mean().to_numpy().transpose()))
                std.append(np.sqrt(np.matmul(np.matmul(np.array(weights), self.portfolio.get_assets_covariance().to_numpy()), np.array(weights).transpose())))

            # step 4.3: plot mean-variance curve
            fig = pl.figure(figsize=(9, 6))
            plots = []
            if show_plots:
                for asset in self.portfolio.assets:
                    plots.append(pl.plot(self.portfolio.full_asset_price_history_change[asset.ticker].std().item(), self.portfolio.full_asset_price_history_change[asset.ticker].mean().item(), label=f"{asset.ticker}", marker='x'))
                plots.append(pl.plot(risk_optimized_portfolio_risk, risk_optimized_portfolio_mean, label="min risk portfolio", marker='o'))
                plots.append(pl.plot(std, mean))

            # step 4.4: plot market capital line
            if self.risk_free_daily_yield > 0:
                plots.append(pl.plot(sharpe_optimized_portfolio_risk, sharpe_optimized_portfolio_mean, label="max sharpe ratio portfolio", marker='o'))
                plots.append(pl.plot(0, self.risk_free_daily_yield, label="risk free asset", marker='x'))
                plots.append(pl.plot(std1, mean1))

            # step 4.5: show the plot
            if show_plots:
                pl.title("Efficient Frontier")
                pl.xlabel("daily risk ($\sigma_p$)")
                pl.ylabel("expected daily return ($E_p$)")
                pl.legend(loc='best')
                fig.show()
                pl.show()

    def __optimize_risk(self):
        def risk(param):
            return np.sqrt(np.matmul(np.matmul(np.array(param), self.portfolio.get_assets_covariance().to_numpy()), np.array(param).transpose()))
        param = self.portfolio.asset_weights
        bnds = tuple([(0, 1)] * (len(param)))
        cons = ({'type': 'eq', 'fun': lambda param: np.sum(param) - 1})
        ans = minimize(risk, param, bounds=bnds, constraints=cons)
        return ans.x

    def __optimize_sharpe_ratio(self):
        def sharpe_ratio(param):
            daily_mean_return = np.matmul(np.array(param), self.portfolio.full_asset_price_history_change.mean().to_numpy().transpose())
            daily_risk = np.sqrt(np.matmul(np.matmul(np.array(param), self.portfolio.get_assets_covariance().to_numpy()), np.array(param).transpose()))
            return -1 * (daily_mean_return - self.risk_free_daily_yield) / daily_risk
        param = self.portfolio.asset_weights
        bnds = tuple([(0, 1)] * (len(param)))
        cons = ({'type': 'eq', 'fun': lambda param: np.sum(param) - 1})
        ans = minimize(sharpe_ratio, param, bounds=bnds, constraints=cons)
        return ans.x

    def __optimize_sortino_ratio(self):
        def sortino_ratio(param):
            portfolio_daily_return = (param * self.portfolio.full_asset_price_history_change).sum(axis=1)
            downside = ((portfolio_daily_return[portfolio_daily_return < self.risk_free_daily_yield] - self.risk_free_daily_yield)**2).sum() / len(portfolio_daily_return)
            return -1 * (portfolio_daily_return.mean() - self.risk_free_daily_yield) / np.sqrt(downside)
        param = self.portfolio.asset_weights
        bnds = tuple([(0, 1)] * (len(param)))
        cons = ({'type': 'eq', 'fun': lambda param: np.sum(param) - 1})
        ans = minimize(sortino_ratio, param, bounds=bnds, constraints=cons)
        return ans.x

    def evaluate(self, asset_list):
        # step 0: get the inception date for the latest listed (最后一个上市的) asset in the portfolio
        self.portfolio.invest(asset_list)
        inception_date_of_the_latest_listed_asset = self.portfolio.full_asset_price_history.index[0].strftime('%Y-%m-%d')

        # step 1: generate a series of dates for evaluation, each with a period of one year
        inception_date = datetime.strptime(inception_date_of_the_latest_listed_asset, '%Y-%m-%d')
        dates = []
        evaluation_date = inception_date + relativedelta(years=1)
        dates.append(evaluation_date.strftime('%Y-%m-%d'))
        today = datetime.today()
        while evaluation_date + relativedelta(years=1) < today:
            evaluation_date += relativedelta(years=1)
            dates.append(evaluation_date.strftime('%Y-%m-%d'))
        dates.append(today.strftime('%Y-%m-%d'))

        # step 2: use all the history data to get the optimized weights before the evaluation date.
        # You plan to invest only two assets: MSFT & FB. MSFT inception date is 1986-3-13, FB is 2012-05-18.
        # By using the historical data between [2012-05-18, 2013-05-18], we can get the optimized weights for investing
        # in the next year (2013-05-18 - 2014-05-18).
        # We will then use all historical data from [2012-05-18, 2014-05-18] to get the optimized weights for investing
        # in the next year (2014-05-18 - 2015-05-18). We wil keep doing this to get the optimized weights, and will use
        # these weights to invest the next year only.
        predicted_minrisk_weights_history = []
        predicted_maxsharpe_weights_history = []
        predicted_maxsortino_weights_history = []
        for date in dates[0:-1]:
            self.portfolio.invest([asset.ticker for asset in self.portfolio.assets], start_date=inception_date, end_date=date)
            predicted_minrisk_weights_history.append(self.__optimize_risk())
            predicted_maxsharpe_weights_history.append(self.__optimize_sharpe_ratio())
            predicted_maxsortino_weights_history.append(self.__optimize_sortino_ratio())

        # step 3: get the predicted sharpe/risk/return with the weights from step 2, also get the actual optimal
        # portfolio using the full year data of the evaluation year.
        predicted_minrisk_risk_history = []
        predicted_minrisk_return_history = []
        predicted_minrisk_sharpe_history = []
        predicted_maxsharpe_risk_history = []
        predicted_maxsharpe_return_history = []
        predicted_maxsharpe_sharpe_history = []
        predicted_maxsortino_return_history = []
        predicted_maxsortino_sortino_history = []
        actual_minrisk_risk_history = []
        actual_minrisk_return_history = []
        actual_minrisk_sharpe_history = []
        actual_maxsharpe_risk_history = []
        actual_maxsharpe_return_history = []
        actual_maxsharpe_sharpe_history = []
        actual_maxsortino_return_history = []
        actual_maxsortino_sortino_history = []

        for i in range(0, len(dates)-1):
            self.portfolio.invest([asset.ticker for asset in self.portfolio.assets], start_date=dates[i], end_date=dates[i+1])

            # use the optimized weights from historical data on the actual data to get the stats that you'll get if
            # investing with these optimized weights
            predicted_minrisk_return, predicted_minrisk_risk, predicted_minrisk_sharpe = self.get_stats(predicted_minrisk_weights_history[i])
            predicted_minrisk_risk_history.append(predicted_minrisk_risk)
            predicted_minrisk_return_history.append(predicted_minrisk_return)
            predicted_minrisk_sharpe_history.append(predicted_minrisk_sharpe)

            predicted_maxsharpe_return, predicted_maxsharpe_risk, predicted_maxsharpe_sharpe = self.get_stats(predicted_maxsharpe_weights_history[i])
            predicted_maxsharpe_risk_history.append(predicted_maxsharpe_risk)
            predicted_maxsharpe_return_history.append(predicted_maxsharpe_return)
            predicted_maxsharpe_sharpe_history.append(predicted_maxsharpe_sharpe)

            predicted_maxsortino_return, predicted_maxsortino_sortino = self.get_sortino_ratio(predicted_maxsortino_weights_history[i])
            predictedmaxsortino

            # get the actual optimized stats only for this year data --> this is the ceiling of the portfolio
            # performance of this year
            min_risk_weights = self.__optimize_risk()
            min_risk_return, min_risk_risk, min_risk_sharpe = self.get_stats(min_risk_weights)
            actual_minrisk_risk_history.append(min_risk_risk)
            actual_minrisk_return_history.append(min_risk_return)
            actual_minrisk_sharpe_history.append(min_risk_sharpe)

            max_sharpe_weights = self.__optimize_sharpe_ratio()
            max_sharpe_return, max_sharpe_risk, max_sharpe_sharpe = self.get_stats(max_sharpe_weights)
            actual_maxsharpe_risk_history.append(max_sharpe_risk)
            actual_maxsharpe_return_history.append(max_sharpe_return)
            actual_maxsharpe_sharpe_history.append(max_sharpe_sharpe)

        # step 4: plot
        # the purpose is to see how the predicted weights and the actual weights differ. In fact, if we want to use MPT
        # for portfolio optimization, we will use the optimized weights computed from all the previous history data to
        # invest for the next year. The core question that this evaluation tries to answer is, how reliable it is to
        # use the optimized weights derived from the full history data when applying these weights in the next year?
        # the predicted stats of the portfolio are using the history-optimized weights to invest, the actual stats are
        # using the latest 1 year of data. By comparing these two values, we can understand to what extend MPT can help
        # predict the optimal portfolio for the next year.
        data = {"predicted_minrisk_risk": predicted_minrisk_risk_history,
                "best_minrisk_risk": actual_minrisk_risk_history,
                "predicted_minrisk_return": predicted_minrisk_return_history,
                "best_minrisk_return": actual_minrisk_return_history,
                "predicted_minrisk_sharpe": predicted_minrisk_sharpe_history,
                "best_minrisk_sharpe":actual_minrisk_sharpe_history,
                "predicted_maxsharpe_risk":predicted_maxsharpe_risk_history,
                "best_maxsharpe_risk":actual_maxsharpe_risk_history,
                "predicted_maxsharpe_return": predicted_maxsharpe_return_history,
                "best_maxsharpe_return": actual_maxsharpe_return_history,
                "predicted_maxsharpe_sharpe": predicted_maxsharpe_sharpe_history,
                "best_maxsharpe_sharpe": actual_maxsharpe_sharpe_history
                }
        df = pd.DataFrame(data, index=dates[1:])
        tickers = [asset.ticker for asset in self.portfolio.assets]
        df[['predicted_minrisk_risk', 'best_minrisk_risk']].plot(style=['r*-','bo-'], title=f"{tickers} predicted optimized RISK v.s. actual optimized RISK")
        df[['predicted_minrisk_return', 'best_minrisk_return']].plot(style=['r*-','bo-'], title=f"{tickers} predicted v.s. actual RETURN by minimizing RISK")
        df[['predicted_maxsharpe_sharpe', 'best_maxsharpe_sharpe']].plot(style=['r*-','bo-'], title=f"{tickers} predicted optimized SHARPE v.s. actual optimized SHARPE")
        df[['predicted_maxsharpe_return', 'best_maxsharpe_return']].plot(style=['r*-','bo-'], title=f"{tickers} predicted v.s. actual RETURN by maximizing SHARPE")
        plt.show()


