import os
import pickle
from LongPosition import LongPosition

class Trader:
    def __init__(self, long_file='long.pkl', history_file='history.pkl'):
        ##  Loading the long dictionary...
        self.long_dict = {}
        if os.path.exists(long_file):
            self.long_dict = self.loadPickle(long_file)
        ##  Loading the history dictionary...
        self.history_dict = {}
        if os.path.exists(history_file):
            self.history_dict = self.loadPickle(history_file)

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

if __name__ == "__main__":
    trader = Trader()
    # trader.addLong('XRP', 0.09, 0.08, 0.12, 1, 1000)
    trader.removeLong(10)
    print('Long Dictionary:')
    print(trader.loadPickle('long.pkl'))
    print('History Dictionary:')
    print(trader.loadPickle('history.pkl'))