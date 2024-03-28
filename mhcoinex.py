import json 
import requests
import numpy as np 
import hashlib
import time 
import datetime
import telegram

def isBuy(l):
    return True if l['type'] == 'buy' else False
def isSell(l):
    return True if l['type'] == 'sell' else False


class MHCoinex:
    def __init__(self):
        print('MHCoinex is at service!')
        self.access_id = "B5374B2B6F624406A2AC54695492B6A4"
        self.secret_key = "C5FB3E92F013B970C8B7816E451D85FD977EA5210DF062E7"
        self.order_ids = []

    def getMarketStatistics(self, market='xrp'):
        url = f'https://api.coinex.com/v1/market/ticker?market={market}usdt'
        response = requests.get(url)
        result = json.loads(response.text)
        return result

    def getBalance(self):
        current_time = int(time.time()*1000)
        sign_str = f"access_id={self.access_id}&tonce={current_time}&secret_key={self.secret_key}"
        url = 'https://api.coinex.com/v2/assets/spot/balance'
        body = {"access_id":self.access_id,
            "tonce": str(current_time)}

        md5 = hashlib.md5(sign_str.encode())
        headers =  {"Content-Type":"application/json", "authorization": md5.hexdigest().upper()}
        response = requests.get(url, params=body, headers=headers)
        print('response: ', response)
        print('response.text: ', response.text)
        result = json.loads(response.text)
        return result
    
    def setOrder(self, amount=60, price=1.2, type_='buy', market="XRP"):
        url = 'https://api.coinex.com/v1/order/limit'
        current_time = int(time.time()*1000)
        body = {"access_id":self.access_id,
            "amount": str(amount),  # order count
            "price": str(price),   # order price
            'type': type_,    # order type
            "market":market.upper()+'USDT',  # market type
            "tonce": str(current_time)}

        sign_str = f"access_id={self.access_id}&amount={amount}&market={market.upper()}USDT&price={price}&tonce={current_time}&type={type_}&secret_key={self.secret_key}"
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
            return result, id_
        else:
            return result, None

    def buy(self, market, amount_usd):
        """
        Easy way to buy a coin with a specific amount of USD.
        It calculates the amount of the coin based on the last sell price in the market.
        Example:
            buy('XRP', 100)
        """
        buy_price = self.getLastBuyPrice(market)
        amount = amount_usd / buy_price
        amount = round(amount, 4) if amount > 1 else amount
        result, id_ = self.setOrder(amount=amount, price=buy_price, type_='buy', market=market)
        for i in range(10):
            time.sleep(5)
            status, amount, price = self.getOrderStatus(id_, market)
            if status == 'done':
                return id_, status, amount, price
        ##  If the order is not done, cancel it...
        res = self.cancelOrder(id_, 'buy', market)
        return id_, status, amount, price
    
    def sell(self, market, amount):
        """
        Easy way to sell a coin with a specific amount of the coin.
        Example:
            sell('XRP', 100)
        """
        sell_price = self.getLastSellPrice(market)
        result, id_ = self.setOrder(amount=amount, price=sell_price, type_='sell', market=market)
        for i in range(10):
            time.sleep(5)
            status, amount, price = self.getOrderStatus(id_, market)
            if status == 'done':
                return id_, status, amount, price
        ##  If the order is not done, cancel it...
        res = self.cancelOrder(id_, 'sell', market)
        return id_, status, amount, price

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

    def getLatestTransactions(self, market='xrp'):
        url = f'https://api.coinex.com/v1/market/deals?market={market.capitalize()}USDT'
        response = requests.get(url)
        result = json.loads(response.text)
        if result['code'] == 0:
            buy_list = list(filter(isBuy, result['data']))
            sell_list = list(filter(isSell, result['data']))
            return buy_list, sell_list
        else:
            return list(), list()

    def getLatestUnexecutedOrders(self, market='xrp'):
        url = 'https://api.coinex.com/v1/order/pending'
        current_time = int(time.time()*1000)
        body = {"access_id":self.access_id,
            "market":market.upper() + 'USDT',  # market type
            'page': "1",   
            "limit": "100",
            "tonce": str(current_time)}

        sign_str = f"access_id={self.access_id}&limit=100&market={market.upper()}USDT&page=1&tonce={current_time}&secret_key={self.secret_key}"
        md5 = hashlib.md5(sign_str.encode())
        headers =  {"Content-Type":"application/json", "authorization": md5.hexdigest().upper()}
        response = requests.get(url, params=body, headers=headers)
        result = json.loads(response.text)
        ##  result['data']['data'][0]['status'] can be 'not_deal' or 'done'
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
        amount, price = None, None
        if code == 0:
            amount = float(result['data']['amount'])
            price = float(result['data']['price'])
            status = result['data']['status']
            return status, amount, price  ##  status in ['cancel', 'done', 'not_deal']
        else:
            return 'error', amount, price

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
        print('response: ', response)
        print('response.text: ', response.text)
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
            "market":market.upper()+'USDT',  # market type
            'type': type_,   
            "tonce": str(current_time)}

        sign_str = f"access_id={self.access_id}&id={str(id)}&market={market.upper()}USDT&tonce={current_time}&type={type_}&secret_key={self.secret_key}"
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
    
    def getLastBuyPrice(self, market='doge', method='transactions'):
        if method is None:  ##  Get the last buy price from the market statistics...
            return self.getMarketStatistics(market)['data']['ticker']['buy']
        buy_list, sell_list = self.getLatestTransactions(market)
        sell_prices = [float(sell['price']) for sell in sell_list]
        sell_prices.sort()
        # print('sell_prices: ', sell_prices)
        return sell_prices[len(sell_prices) // 3]
    
    def getLastSellPrice(self, market='doge', method='transactions'):
        if method is None:
            return self.getMarketStatistics(market)['data']['ticker']['sell']
        buy_list, sell_list = self.getLatestTransactions(market)
        buy_prices = [float(buy['price']) for buy in buy_list]
        buy_prices.sort()
        # print('buy_prices: ', buy_prices)
        return buy_prices[len(buy_prices) // 3]

    
        



if __name__ == '__main__':
    mhc = MHCoinex()
    buy_price = mhc.getLastBuyPrice('doge')
    print(f'doge buy price: ', buy_price)
    # res = mhc.getLatestUnexecutedOrders('DOGE')
    # print(res)
    
    # id_, status, amount, price = mhc.buy('DOGE', 20)
    # print('outside buy: id', id_)
    # print('outside buy: status', status)
    # print('outside buy: amount', amount)
    # print('outside buy: price', price)
    # res = mhc.getOrderStatus(id_, 'DOGE')
    # print(res)
    amount = 92.1944
    id_ = 114782770740
    id_, status, amount, price = mhc.sell('DOGE', amount)
    print('outside sell: id', id_)
    print('outside sell: status', status)
    print('outside sell: amount', amount)
    print('outside sell: price', price)


    # sell_price = mhc.getLastSellPrice('doge')
    # print(f'doge sell price: ', sell_price)
    # res = mhc.getBalance()
    # print(res)
    # res = mhc.getUserDeals('doge')
    # print(res)
    # res = mhc.getLatestTransactions('doge')
    # print(res)
    # mhc.setStopOrder(60, price=1, stop_price=1.2, signals=SIGNALS)

    # result = mhc.getUserDeals('ADA')
    # print(result)
    
    