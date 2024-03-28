import os
import pickle
from LongPosition import LongPosition
from mhcoinex import MHCoinex

class Trader:
    def __init__(self, long_file='long.pkl', history_file='history.pkl', coinex=None):
        ##  Loading the long dictionary...
        self.long_dict = {}
        if os.path.exists(long_file):
            self.long_dict = self.loadPickle(long_file)
        ##  Loading the history dictionary...
        self.history_dict = {}
        if os.path.exists(history_file):
            self.history_dict = self.loadPickle(history_file)
        ##  Coinex object...
        self.coinex = coinex

    def addLong(self, coin, entry, loss_price, profit_price, total_risk_percentage=1., total_budget=1000., started=False):
        id_ = len(self.history_dict) + 1
        long_position = LongPosition(id_, coin=coin, entry=entry, loss_price=loss_price, profit_price=profit_price, total_risk_percentage=total_risk_percentage, total_budget=total_budget, started=started)
        ##  Updaing and saving the long and history dictionaries...
        self.long_dict[id_] = long_position
        self.history_dict[id_] = long_position
        self.updateData()

    def removeLong(self, id_):
        ##  Removing the long position from the long dictionary...
        if id_ in self.long_dict:
            self.long_dict.pop(id_)
        else:
            print(f'Long position with ID {id_} does not exist!')
        ##  Updating and saving the long and history dictionaries...
        self.updateData()

    def updateData(self):
        ##  Updating the long dictionary...
        self.savePickle('long.pkl', self.long_dict)
        ##  Updating the history dictionary...
        self.savePickle('history.pkl', self.history_dict)

    def loadPickle(self, filename):
        with open(filename, 'rb') as f:
            res = pickle.load(f)
        return res
    
    def savePickle(self, filename, data):
        with open(filename, 'wb') as f:
            pickle.dump(data, f)

    def process(self):
        ##  To process both active and inactive long positions...
        ##  For inactive long positions...
        for id in self.getInactiveIDs():
            stat, msg = self.processInactive(id, self.long_dict[id])
            if msg:
                self.log(msg)
        ##  For active long positions...
        # for id in self.getActiveIDs():
        #     stat, msg = self.processActive(id, self.long_dict[id])
        #     if msg:
        #         self.log(msg)

    def processActive(self, id, long_position):
        ##  To process active long positions...
        sell_price = self.coinex.getLastSellPrice(long_position.coin)
        if sell_price <= long_position.loss_price:
            sell_state = self.sell(long_position.coin, long_position.position_amount)
            if sell_state:
                long_position.status = 'stopped'
                self.updateData()
                return True, f'Long position with ID {long_position.id} has been stopped for loss!'
            return False, f'Long position with ID {long_position.id} did not stopped correctly for loss!'
        elif sell_price >= long_position.profit_price:
            sell_state = self.sell(long_position.coin, long_position.position_amount)
            if sell_state:
                long_position.status = 'stopped'
                self.updateData()
                return True, f'Long position with ID {long_position.id} has been stopped for profit!'
            return False, f'Long position with ID {long_position.id} did not stopped correctly for profit!'
        return True, None

    def processInactive(self, id, long_position):
        ##  To process inactive long positions...
        buy_price = self.coinex.getLastBuyPrice(long_position.coin)
        if buy_price >= long_position.entry:
            order_id, buy_status, amount, price = self.coinex.buy(long_position.coin, long_position.position_amount)
            if buy_status == 'done':
                long_position.status = 'started'
                long_position.order_id = order_id
                long_position.position_amount = amount
                long_position.entry = price
                long_position.update()
                self.updateData()
                return True, f'Long position with ID {long_position.id} has been started!'
            return False, f'Long position with ID {long_position.id} did not started correctly!'
        return True, None
    
    def log(self, text, photo=None):
        print(text)    

    def getActiveIDs(self):
        ids = self.long_dict.keys()
        return [id for id in ids if self.long_dict[id].status == 'started']
    
    def getInactiveIDs(self):
        ids = self.long_dict.keys()
        return [id for id in ids if self.long_dict[id].status == 'not_started']



if __name__ == "__main__":
    coinex = MHCoinex()
    trader = Trader(coinex=coinex)
    # trader.addLong('XRP', 0.09, 0.08, 0.12, 1, 1000, True)
    # trader.removeLong(10)
    print('Long Dictionary:')
    print(trader.loadPickle('long.pkl'))
    # print('History Dictionary:')
    # print(trader.loadPickle('history.pkl'))
    print('Active IDs:')
    print(trader.getActiveIDs())
    print('Inactive IDs:')
    print(trader.getInactiveIDs())
