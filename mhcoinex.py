import json 
import requests
import numpy as np 
import hashlib
import time 
import schedule
import datetime
import temp as tp
import telegram

def isBuy(l):
    return True if l['type'] == 'buy' else False
def isSell(l):
    return True if l['type'] == 'sell' else False


class MHCoinex:
    def __init__(self):
        print('MHCoinex is at service!')
        self.access_id = "060D4B77867B4DB8BC9EE978E18EA91E"
        self.secret_key = "54C01878C7A76019DD8BC0E428D6E30B2265D49243F87AF9"
        self.order_ids = []

    def getMarketStatistics(self, market='xrp'):
        url = f'https://api.coinex.com/v1/market/ticker?market={market}usdt'
        response = requests.get(url)
        result = json.loads(response.text)
        return result

    def setOrder(self, amount=60, price=1.2, type_='buy', market="XRP", signals=None):
        url = 'https://api.coinex.com/v1/order/limit'
        current_time = int(time.time()*1000)
        body = {"access_id":"060D4B77867B4DB8BC9EE978E18EA91E",
            "amount": str(amount),  # order count
            "price": str(price),   # order price
            'type': type_,    # order type
            "market":market+'USDT',  # market type
            "tonce": str(current_time)}

        sign_str = f"access_id={self.access_id}&amount={amount}&market={market}USDT&price={price}&tonce={current_time}&type={type_}&secret_key={self.secret_key}"
        md5 = hashlib.md5(sign_str.encode())
        headers =  {"Content-Type":"application/json", "authorization": md5.hexdigest().upper()}
        response = requests.post(url, json=body, headers=headers)
        result = json.loads(response.text)
        code = result['code']
        if code:
            print(result)
            print('setorder code:', code)
            print(body)
        if code == 0:
            id_ = result['data']['id']
            if signals:
                signals[market]['history'][type_]['id'] = id_
                signals[market]['history'][type_]['price'] = price
                signals[market]['history'][type_]['done'] = False
                signals[market]['history'][type_]['time'] = datetime.datetime.now()
                signals[market]['pending'] = type_
                signals[market]['trading'] = True
            return result, id_
        else:
            if signals:
                signals[market]['history'][type_]['id'] = None
                signals[market]['history'][type_]['done'] = False
            return result, None

    def setStopOrder(self, amount=60, price=1.2, stop_price=1.3, type_='buy', market="XRP", signals=None):
        url = 'https://api.coinex.com/v1/order/stop/limit'
        current_time = int(time.time()*1000)
        body = {"access_id":"060D4B77867B4DB8BC9EE978E18EA91E",
            "amount": str(amount),  # order count
            "price": str(price),   # order price
            'stop_price': str(stop_price),
            'type': type_,    # order type
            "market":market+'USDT',  # market type
            "tonce": str(current_time)}

        sign_str = f"access_id={self.access_id}&amount={amount}&market={market}USDT&price={price}&stop_price={stop_price}&tonce={current_time}&type={type_}&secret_key={self.secret_key}"
        md5 = hashlib.md5(sign_str.encode())
        headers =  {"Content-Type":"application/json", "authorization": md5.hexdigest().upper()}
        response = requests.post(url, json=body, headers=headers)
        result = json.loads(response.text)
        code = result['code']
        if code:
            print(result)
            print('setorder code:', code)
            print(body)
        if code == 0:
            print('stop_price done ok!')
        return result

    def getLatestTransactions(self):
        url = 'https://api.coinex.com/v1/market/deals?market=XRPUSDT'
        response = requests.get(url)
        result = json.loads(response.text)
        if result['code'] == 0:
            buy_list = list(filter(isBuy, result['data']))
            sell_list = list(filter(isSell, result['data']))
            return buy_list, sell_list
        else:
            return list(), list()

    def getLatestUnexecutedOrders(self, market='XRPUSDT'):
        url = 'https://api.coinex.com/v1/order/pending'
        current_time = int(time.time()*1000)
        body = {"access_id":self.access_id,
            "market":market,  # market type
            'page': "1",   
            "limit": "100",
            "tonce": str(current_time)}

        sign_str = f"access_id={self.access_id}&limit=100&market={market}&page=1&tonce={current_time}&secret_key={self.secret_key}"
        md5 = hashlib.md5(sign_str.encode())
        headers =  {"Content-Type":"application/json", "authorization": md5.hexdigest().upper()}
        response = requests.get(url, params=body, headers=headers)
        result = json.loads(response.text)
        return result
   
    def getOrderStatus(self, id_, market='XRP'):
        url = 'https://api.coinex.com/v1/order/status'
        current_time = int(time.time()*1000)
        body = {"access_id":self.access_id,
            "id": str(id_),
            "market":market+'USDT',  # market type
            "tonce": str(current_time)}

        sign_str = f"access_id={self.access_id}&id={str(id_)}&market={market}USDT&tonce={current_time}&secret_key={self.secret_key}"
        md5 = hashlib.md5(sign_str.encode())
        headers =  {"Content-Type":"application/json", "authorization": md5.hexdigest().upper()}
        response = requests.get(url, params=body, headers=headers)
        result = json.loads(response.text)
        code = result['code']
        if code == 0:
            status = result['data']['status']
            return status
        else:
            return 'error'

    def getUserDeals(self, market='XRP'):
        url = 'https://api.coinex.com/v1/order/user/deals'
        current_time = int(time.time()*1000)
        body = {"access_id":self.access_id,
            "page" : "1",
            "limit" : "10",
            "market":market+'USDT',  # market type
            "tonce": str(current_time)}

        sign_str = f"access_id={self.access_id}&limit=10&market={market}USDT&page=1&tonce={current_time}&secret_key={self.secret_key}"
        md5 = hashlib.md5(sign_str.encode())
        headers =  {"Content-Type":"application/json", "authorization": md5.hexdigest().upper()}
        response = requests.get(url, params=body, headers=headers)
        result = json.loads(response.text)
        code = result['code']
        if code == 0:
            data = result['data']['data']
            return data 
        else:
            return None
        
    def isThereAnyOrder(self):
        last = self.getLatestUnexecutedOrders()['data']['data']
        return True if len(last) else False

    def cancelOrder(self, id, type_, market='XRP'):
        url = 'https://api.coinex.com/v1/order/pending'
        current_time = int(time.time()*1000)
        body = {"access_id":self.access_id,
            "id": str(id),
            "market":market+'USDT',  # market type
            'type': type_,   
            "tonce": str(current_time)}

        sign_str = f"access_id={self.access_id}&id={str(id)}&market={market}USDT&tonce={current_time}&type={type_}&secret_key={self.secret_key}"
        md5 = hashlib.md5(sign_str.encode())
        headers =  {"Content-Type":"application/json", "authorization": md5.hexdigest().upper()}
        # response = requests.get(url, params=body, headers=headers)
        response = requests.delete(url, params=body, headers=headers)
        result = json.loads(response.text)
        return result
    
    def cancelAllOrders(self, market='XRP'):
        url = 'https://api.coinex.com/v1/order/pending'
        current_time = int(time.time()*1000)
        body = {"access_id":self.access_id,
            "account_id": "0",
            "market":market+'USDT',  # market type
            "tonce": str(current_time)}

        sign_str = f"access_id={self.access_id}&account_id=0&market={market}USDT&tonce={current_time}&secret_key={self.secret_key}"
        md5 = hashlib.md5(sign_str.encode())
        headers =  {"Content-Type":"application/json", "authorization": md5.hexdigest().upper()}
        # response = requests.get(url, params=body, headers=headers)
        response = requests.delete(url, params=body, headers=headers)
        result = json.loads(response.text)
        print('All orders cancelled!: ', result)
        return result

    def getBuyAndSellPrices(self):
        buy, sell = self.getLatestTransactions()
        avg_buy, avg_sell = 0, 0
        for i in range(len(buy)):
            avg_buy += float(buy[i]['price'])
        for i in range(len(sell)):
            avg_sell += float(sell[i]['price'])
        avg_buy /= len(buy)
        avg_sell /= len(sell)
        return avg_buy, avg_sell
        



if __name__ == '__main__':
    CNT = [0]
    SIGNALS = {'ADA': {'enable': True, 'buy_amount': 10, 'sell_amount': 10, 'pending':'sell', 'trading': False, 'ma_loss_amount': 1.5, 'ma_gain_amount': 2, 'ma_gain_sell': None, 'ma_loss_sell': None, 'under_gain_amount': 0.02, 'above_gain_amount': 0.0075, 'under_loss_amount': 0.015, 'above_loss_amount': 0.01, 'last_buy':None, 'gain_amount': 0.01, 'loss_amount': 0.007, 'gain_percentage': 0.7, 'loss_percentage':0.35, 'gain_cnt':0, 'cci':list(), 'ma4':list(), 'ma20':list(), 'history':{'buy':{'done': True, 'id': None, 'price': 0, 'temp': False}, 'sell':{'done': True, 'id': None, 'price': 0}}}, 
           'XRP': {'enable': False, 'buy_amount': 120, 'sell_amount': 120, 'pending':'buy', 'trading': False, 'ma_loss_amount': 1.5, 'ma_gain_amount': 2, 'ma_gain_sell': None, 'ma_loss_sell': None, 'last_buy':None, 'gain_amount': 0.01, 'loss_amount': 0.007, 'gain_percentage': 0.7, 'loss_percentage':0.35, 'gain_cnt':0, 'cci':list(), 'ma4':list(), 'ma20':list(), 'history':{'buy':{'done': True, 'id': None, 'price': 0, 'temp': False}, 'sell':{'done': True, 'id': None, 'price': 0}}}}
    mhc = MHCoinex()
    # mhc.setStopOrder(60, price=1, stop_price=1.2, signals=SIGNALS)
    result = mhc.getUserDeals('ADA')
    print(result)
    tradesIchimoku(mhc, CNT, SIGNALS)
    