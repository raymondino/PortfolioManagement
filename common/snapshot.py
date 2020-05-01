import numpy as np

class Snapshot:
    """
    This class represents the portfolio snapshot at the time point when you invest
    """
    def __init__(self, weights, previous_snapshot, assets_price_at_current_date, enable_rebalance, rebalance_offset,
                 investment_amount):
        """
        construct a snapshot object
        :param weights: the weight for each asset in this portfolio
        :param previous_snapshot: the snapshot of the invest date right before current invest date
        :param assets_price_at_current_date: assets prices at current invest date. It's of type pandas.Series
        :param enable_rebalance: enable rebalance or not
        :param rebalance_offset: the offset value to initiate a rebalance
        :param investment_amount: fixed investment amount
        :return: a snapshot object
        """
        self.assets_share_after_rebalance = []  # asset shares after rebalance
        self.assets_share_from_investment_amount = []  # asset shares bought by investment_amount
        self.assets_final_share = []  # assets_share_after_rebalance + assets_share_from_investment_amount
        self.book_value = 0
        self.assets_value = []
        self.rebalanced = "[NOT]"
        self.money_invested = 0

        # get the datetime for this snapshot
        self.snapshot_datetime = assets_price_at_current_date.name.date()
        # accumulate the total investment so far
        self.total_investment = investment_amount if previous_snapshot is None else (previous_snapshot.total_investment + investment_amount)
        # if rebalance is enabled and needed
        if enable_rebalance and self.__need_to_rebalance(weights, assets_price_at_current_date, previous_snapshot, rebalance_offset):
            # we can rebalance this snapshot
            self.__rebalance(weights, assets_price_at_current_date, previous_snapshot)
        else:
            # else, we will keep shares the same as previous snapshot or keep shares 0 if previous snapshot is None
            self.assets_share_after_rebalance = [0] * len(weights) if previous_snapshot is None else previous_snapshot.assets_final_share
        # invest the investment_amount based on current assets weights and prices
        self.__invest(weights, assets_price_at_current_date, investment_amount)
        # get the book value of this snapshot after investing
        self.book_value = np.dot(self.assets_share_after_rebalance, assets_price_at_current_date.values.tolist())
        self.book_value += investment_amount
        # finalize the asset shares for this snapshot
        self.assets_final_share = [s1+s2 for (s1, s2) in zip(self.assets_share_after_rebalance, self.assets_share_from_investment_amount)]
        self.assets_value = [p*s for (p, s) in zip(self.assets_final_share, assets_price_at_current_date.values.tolist())]

    def __need_to_rebalance(self, weights, assets_price_at_current_date, previous_snapshot, rebalance_offset):
        if previous_snapshot is None:
            return False
        book_value_at_rebalance = np.dot(assets_price_at_current_date, previous_snapshot.assets_final_share)
        for i in range(0, len(weights)):
            offset_ratio = abs((assets_price_at_current_date[i] * previous_snapshot.assets_final_share[i] / book_value_at_rebalance) - weights[i])
            if offset_ratio >= rebalance_offset:
                self.rebalanced = "[REB]"
                return True
        return False

    def __rebalance(self, weights, assets_price_at_current_date, previous_snapshot):
        book_value_at_rebalance = np.dot(assets_price_at_current_date, previous_snapshot.assets_final_share)
        for i in range(0, len(weights)):
            self.assets_share_after_rebalance.append(weights[i]*book_value_at_rebalance/assets_price_at_current_date[i])

    def __invest(self, weights, assets_price_at_current_date, investment_amount):
        #  money_invested is made to be negative purposely because when calculating average return using XIRR,
        #  invested cash is required to be negative, vested money are positive
        self.money_invested = -1 * investment_amount
        for i in range(0, len(weights)):
            self.assets_share_from_investment_amount.append(
                weights[i] * investment_amount / assets_price_at_current_date[i])