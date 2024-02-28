#########################################################################################
##                                                                                     ##
##                                Mohammad Hossein Amini                               ##
##                              Title: LongPosition Class                              ##
##                                   Date: 2024/02/28                                  ##
##                                                                                     ##
#########################################################################################

##  Description: 


class LongPosition:
    def __init__(self, id, coin, entry, loss_price, profit_price, total_risk_percentage=1., total_budget=1000., started=False):
        self.id = id
        self.coin = coin
        self.entry = entry
        self.loss_price = loss_price
        self.profit_price = profit_price
        self.total_risk_percentage = total_risk_percentage
        self.total_budget = total_budget
        self.loss_percentage = (self.entry - self.loss_price) / self.entry * 100
        self.profit_percentage = (self.profit_price - self.entry) / self.entry * 100
        self.risk_reward_ratio = self.profit_percentage / self.loss_percentage
        self.position_amount = self.total_budget * self.total_risk_percentage / self.loss_percentage  ##  In USD...
        self.started = started

    def __repr__(self):
        msg = f"""
        {"-"*50}
            Long Position:
                ID: {self.id},
                Coin: {self.coin},
                Entry Price: {self.entry},
                Loss Price: {self.loss_price} ({self.loss_percentage: .2f}%),
                Profit Price: {self.profit_price} ({self.profit_percentage: .2f}%),
                Risk Reward Ratio: {self.risk_reward_ratio: .2f},
                Total Risk Percentage: {self.total_risk_percentage}%,
                Total Budget: {self.total_budget} USD,
                Position Amount: {self.position_amount: .2f} USD
                Started: {self.started}
        {"-"*50}
        """
        return msg

if __name__ == "__main__":
    long = LongPosition(1, "DOGE", 0.09, 0.08, 0.12, 1, 1000)
    print(long)