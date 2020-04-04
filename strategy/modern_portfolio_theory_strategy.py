import numpy as np
import matplotlib.pylab as pl
from scipy.optimize import minimize


class MPT:
    def __init__(self, allocate_risk_free_asset=False, risk_free_annual_yield=None):
        self.portfolio = None
        self.risk_free_daily_yield = 0
        if allocate_risk_free_asset and risk_free_annual_yield is not None:
            self.risk_free_daily_yield = pow(1 + risk_free_annual_yield, 1/365) - 1

    def fit(self, portfolio, show_details=True, show_plot=False):
        self.portfolio = portfolio
        self.daily_mean_return = np.matmul(np.array(portfolio.asset_weights), portfolio.full_asset_price_history_change.mean().to_numpy().transpose())
        self.daily_risk = np.sqrt(np.matmul(np.matmul(np.array(portfolio.asset_weights), portfolio.get_assets_covariance().to_numpy()), np.array(portfolio.asset_weights).transpose()))
        self.sharpe_ratio = (self.daily_mean_return - self.risk_free_daily_yield) / self.daily_risk
        self.plot_efficient_frontier(show_details, show_plot)

    def plot_efficient_frontier(self, show_details, show_plots, customized_weights=[]):
        # step 1: calculate the man-variance for the optimized portfolio
        risk_optimized_weights = self.__optimize_risk()
        risk_optimized_portfolio_mean = np.matmul(np.array(risk_optimized_weights), self.portfolio.full_asset_price_history_change.mean().to_numpy().transpose())
        risk_optimized_portfolio_risk = np.sqrt(np.matmul(np.matmul(np.array(risk_optimized_weights), self.portfolio.get_assets_covariance().to_numpy()), np.array(risk_optimized_weights).transpose()))
        sharpe_optmized_weights = self.__optimize_sharpe_ratio()
        sharpe_optimized_portfolio_mean = np.matmul(np.array(sharpe_optmized_weights), self.portfolio.full_asset_price_history_change.mean().to_numpy().transpose())
        sharpe_optimized_portfolio_risk = np.sqrt(np.matmul(np.matmul(np.array(sharpe_optmized_weights), self.portfolio.get_assets_covariance().to_numpy()), np.array(sharpe_optmized_weights).transpose()))

        # step 2: report
        if show_details:
            print("======MPT optimization========")
            print(f"investing assets: {[asset.ticker for asset in self.portfolio.assets]}")
            print(f"risk optimized weights: {list(np.around(np.array(risk_optimized_weights),2))}")
            print(f"risk optimized yearly return: {round(risk_optimized_portfolio_mean*252, 2)}")  # there about 252 trading days per year
            print(f"risk optimized yearly risk: {round(risk_optimized_portfolio_risk*np.sqrt(252), 2)}")
            print("==============================")
            print(f"sharpe ratio optimized weights: {list(np.around(np.array(sharpe_optmized_weights),2))}")
            print(f"sharpe ratio optimized yearly return: {round(sharpe_optimized_portfolio_mean*252, 2)}")
            print(f"sharpe ratio optimized yearly risk: {round(sharpe_optimized_portfolio_risk*np.sqrt(252), 2)}")

        # step 3: if allocating risk free asset
        mean1 = []
        std1 = []
        if self.risk_free_daily_yield > 0:
            for w in np.arange(0, 1.01, 0.01):
                mean1.append(np.matmul(np.array([w, 1-w]), np.array([self.risk_free_daily_yield, sharpe_optimized_portfolio_mean]).transpose()))
                std1.append((1-w) * sharpe_optimized_portfolio_risk)
            if show_details:
                print("==============================")
                print(f"allocate 10% risk free asset: yearly return = {round(mean1[11]*252,6)}, yearly risk = {round(std1[11]*np.sqrt(252),6)}")
                print(f"allocate 15% risk free asset: yearly return = {round(mean1[16]*252,6)}, yearly risk = {round(std1[16]*np.sqrt(252),6)}")
                print(f"allocate 20% risk free asset: yearly return = {round(mean1[21]*252,6)}, yearly risk = {round(std1[21]*np.sqrt(252),6)}")
                print(f"allocate 25% risk free asset: yearly return = {round(mean1[26]*252,6)}, yearly risk = {round(std1[26]*np.sqrt(252),6)}")
                print(f"allocate 30% risk free asset: yearly return = {round(mean1[31]*252,6)}, yearly risk = {round(std1[31]*np.sqrt(252),6)}")
                print(f"allocate 35% risk free asset: yearly return = {round(mean1[36]*252,6)}, yearly risk = {round(std1[36]*np.sqrt(252),6)}")
                print(f"allocate 40% risk free asset: yearly return = {round(mean1[41]*252,6)}, yearly risk = {round(std1[41]*np.sqrt(252),6)}")
                print(f"allocate 45% risk free asset: yearly return = {round(mean1[46]*252,6)}, yearly risk = {round(std1[46]*np.sqrt(252),6)}")
                print(f"allocate 50% risk free asset: yearly return = {round(mean1[51]*252,6)}, yearly risk = {round(std1[51]*np.sqrt(252),6)}")
                print(f"allocate 55% risk free asset: yearly return = {round(mean1[56]*252,6)}, yearly risk = {round(std1[56]*np.sqrt(252),6)}")
                print(f"allocate 60% risk free asset: yearly return = {round(mean1[61]*252,6)}, yearly risk = {round(std1[61]*np.sqrt(252),6)}")
                print(f"allocate 65% risk free asset: yearly return = {round(mean1[66]*252,6)}, yearly risk = {round(std1[66]*np.sqrt(252),6)}")
                print(f"allocate 70% risk free asset: yearly return = {round(mean1[71]*252,6)}, yearly risk = {round(std1[71]*np.sqrt(252),6)}")
                print(f"allocate 75% risk free asset: yearly return = {round(mean1[76]*252,6)}, yearly risk = {round(std1[76]*np.sqrt(252),6)}")
                print(f"allocate 80% risk free asset: yearly return = {round(mean1[81]*252,6)}, yearly risk = {round(std1[81]*np.sqrt(252),6)}")
                print(f"allocate 85% risk free asset: yearly return = {round(mean1[86]*252,6)}, yearly risk = {round(std1[86]*np.sqrt(252),6)}")
                print(f"allocate 90% risk free asset: yearly return = {round(mean1[91]*252,6)}, yearly risk = {round(std1[91]*np.sqrt(252),6)}")
                print(f"allocate 95% risk free asset: yearly return = {round(mean1[96]*252,6)}, yearly risk = {round(std1[96]*np.sqrt(252),6)}")

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
                plots.append(pl.plot(sharpe_optimized_portfolio_risk, sharpe_optimized_portfolio_mean, label="max sharpe ratio portfolio", marker='o'))
                plots.append(pl.plot(std, mean))

            # step 4.4: plot market capital line
            if self.risk_free_daily_yield > 0:
                plots.append(pl.plot(0, self.risk_free_daily_yield, label="risk free asset", marker='x'))
                plots.append(pl.plot(std1, mean1))

            # step 4.5: show the plot
            if show_plots:
                pl.title("MPT mean-curve plot")
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
