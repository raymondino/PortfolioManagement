import numpy as np
import matplotlib.pylab as pl
from scipy.optimize import minimize


class MPT:
    def __init__(self, allocate_risk_free_asset=False, risk_free_annual_yield=None):
        self.portfolio = None
        self.risk_free_daily_yield = 0
        if allocate_risk_free_asset and risk_free_annual_yield is not None:
            self.risk_free_daily_yield = pow(1 + risk_free_annual_yield, 1/365) - 1

    def fit(self, portfolio, show_details=True):
        self.portfolio = portfolio
        self.daily_mean_return = np.matmul(np.array(portfolio.asset_weights), portfolio.full_asset_price_history_change.mean().to_numpy().transpose())
        self.daily_risk = np.sqrt(np.matmul(np.matmul(np.array(portfolio.asset_weights), portfolio.get_assets_covariance().to_numpy()), np.array(portfolio.asset_weights).transpose()))
        self.sharpe_ratio = (self.daily_mean_return - self.risk_free_daily_yield) / self.daily_risk
        self.plot_efficient_frontier(show_details)

    def plot_efficient_frontier(self, show_details, customized_weights=[]):
        # step 1: get the combination list of weights
        def get_all_weight_combo(cur_weight, weight_combos):
            if 1-sum(cur_weight) < 0:
                return
            if len(cur_weight) == len(self.portfolio.assets) - 1:
                cur_weight.append(round(1-sum(cur_weight), 2))
                weight_combos.append(cur_weight.copy())
                del cur_weight[-1]
                return
            for i in np.arange(0, 1-sum(cur_weight)+0.01, 0.01):
                cur_weight.append(round(i, 2))
                get_all_weight_combo(cur_weight, weight_combos)
                del cur_weight[-1]
        weight_combos = []
        get_all_weight_combo([], weight_combos)

        # step 2: calculate portfolio return and risk for mean-variance curve
        mean = []
        std = []
        for weights in weight_combos:
            mean.append(np.matmul(np.array(weights), self.portfolio.full_asset_price_history_change.mean().to_numpy().transpose()))
            std.append(np.sqrt(np.matmul(np.matmul(np.array(weights), self.portfolio.get_assets_covariance().to_numpy()), np.array(weights).transpose())))

        # step 3: calculate the man-variance for the optimized portfolio
        risk_optimized_weights = self.__optimize_risk()
        risk_optimized_portfolio_mean = np.matmul(np.array(risk_optimized_weights), self.portfolio.full_asset_price_history_change.mean().to_numpy().transpose())
        risk_optimized_portfolio_risk = np.sqrt(np.matmul(np.matmul(np.array(risk_optimized_weights), self.portfolio.get_assets_covariance().to_numpy()), np.array(risk_optimized_weights).transpose()))
        sharpe_optmized_weights = self.__optimize_sharpe_ratio()
        sharpe_optimized_portfolio_mean = np.matmul(np.array(sharpe_optmized_weights), self.portfolio.full_asset_price_history_change.mean().to_numpy().transpose())
        sharpe_optimized_portfolio_risk = np.sqrt(np.matmul(np.matmul(np.array(sharpe_optmized_weights), self.portfolio.get_assets_covariance().to_numpy()), np.array(sharpe_optmized_weights).transpose()))

        # step 4: plot mean-variance curve
        fig = pl.figure(figsize=(9, 6))
        plots = []
        for asset in self.portfolio.assets:
            plots.append(pl.plot(asset.get_risk(), asset.get_return_mean(), label=f"{asset.ticker}", marker='x'))
        plots.append(pl.plot(risk_optimized_portfolio_risk, risk_optimized_portfolio_mean, label="min risk portfolio", marker='o'))
        plots.append(pl.plot(sharpe_optimized_portfolio_risk, sharpe_optimized_portfolio_mean, label="max sharpe ratio portfolio", marker='o'))
        plots.append(pl.plot(std, mean))

        # step 5: print report
        if show_details:
            print("MPT portfolio optimization")
            print(f"investing assets: {[asset.ticker for asset in self.portfolio.assets]}")
            print(f"risk optimized weights: {list(np.around(np.array(risk_optimized_weights),2))}")
            print(f"risk optimized daily return: {risk_optimized_portfolio_mean}")
            print(f"risk optimized daily risk: {risk_optimized_portfolio_risk}")
            print(f"sharpe ratio optimized weights: {list(np.around(np.array(sharpe_optmized_weights),2))}")
            print(f"sharpe ratio optimized daily return: {sharpe_optimized_portfolio_mean}")
            print(f"sharpe ratio optimized daily risk: {sharpe_optimized_portfolio_risk}")

        # step 6: if allocating risk free asset
        if self.risk_free_daily_yield > 0:
            mean1 = []
            std1 = []
            plots.append(pl.plot(0, self.risk_free_daily_yield, label="risk free asset", marker='x'))
            for w in np.arange(0, 1.01, 0.01):
                mean1.append(np.matmul(np.array([w, 1-w]), np.array([self.risk_free_daily_yield, sharpe_optimized_portfolio_mean]).transpose()))
                std1.append((1-w) * sharpe_optimized_portfolio_risk)
            plots.append(pl.plot(std1, mean1))
            if show_details:
                print(f"allocate 10% risk free asset: return = {mean1[11]}, risk = {std1[11]}")
                print(f"allocate 15% risk free asset: return = {mean1[16]}, risk = {std1[16]}")
                print(f"allocate 20% risk free asset: return = {mean1[21]}, risk = {std1[21]}")
                print(f"allocate 25% risk free asset: return = {mean1[26]}, risk = {std1[26]}")
                print(f"allocate 30% risk free asset: return = {mean1[31]}, risk = {std1[31]}")
                print(f"allocate 35% risk free asset: return = {mean1[36]}, risk = {std1[36]}")
                print(f"allocate 40% risk free asset: return = {mean1[41]}, risk = {std1[41]}")
                print(f"allocate 45% risk free asset: return = {mean1[46]}, risk = {std1[46]}")
                print(f"allocate 50% risk free asset: return = {mean1[51]}, risk = {std1[51]}")
                print(f"allocate 55% risk free asset: return = {mean1[56]}, risk = {std1[56]}")
                print(f"allocate 60% risk free asset: return = {mean1[61]}, risk = {std1[61]}")
                print(f"allocate 65% risk free asset: return = {mean1[66]}, risk = {std1[66]}")
                print(f"allocate 70% risk free asset: return = {mean1[71]}, risk = {std1[71]}")
                print(f"allocate 75% risk free asset: return = {mean1[76]}, risk = {std1[76]}")
                print(f"allocate 80% risk free asset: return = {mean1[81]}, risk = {std1[81]}")
                print(f"allocate 85% risk free asset: return = {mean1[86]}, risk = {std1[86]}")
                print(f"allocate 90% risk free asset: return = {mean1[91]}, risk = {std1[91]}")
                print(f"allocate 95% risk free asset: return = {mean1[96]}, risk = {std1[96]}")

        # step 7: show the plot
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
