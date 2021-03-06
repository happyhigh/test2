from pprint import pprint
from re import X
import time
from datetime import datetime
from ccxt.binance import binance
import pyupbit
import ccxt
import telegram
import requests, json
import threading

ticker = ['SOL','EOS','XRP','DOGE','BTT','ADA','SAND']

# changing ticker name for exchange market
upbit_ticker = [] 
binance_ticker = []
for i in ticker:
            upbit_ticker.append('KRW-'+i)
            binance_ticker.append(i+'/USDT')

class MonitoringKP(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cycle = 60 * 2
        # self.cycle = 5

    def run(self):   
        binance = ccxt.binance()
        while True:
            debug('kimchi premium monitoring', 1)

            # recv binance price
            binance_pirce = binance.fetch_tickers(binance_ticker)

            # recv upbit price
            upbit_price = pyupbit.get_current_price(upbit_ticker)
            # print(upbit_price)
            # print(upbit_price['KRW-SOL'])

            # calculate kimchi premium
            e = get_exchange_rate() # 현재환율

            kp = {}
            message = 'kimchi premium monitoring\n'
            for i in ticker:
                binance_pirce_krw = binance_pirce[i+'/USDT']['close'] * e         # binance margin values for KRW
                kp[i] = upbit_price['KRW-'+i] / binance_pirce_krw * 100 - 100     # calc kp

            # find max, min kp
            all_values = kp.values()
            max_values = max(all_values)
            min_values = min(all_values)
            max_token = find_key(kp, max_values)
            min_token = find_key(kp, min_values)
            message += 'o max kp[%s] : %s\n'%(max_token, round(max_values, 3))
            message += 'o min kp[%s] : %s\n'%(min_token, round(min_values, 3))
            message += 'o cal kp : %s\n'%(round(max_values-min_values, 3))
            debug(message, 2)
            send_message(message)

            time.sleep(self.cycle)

    

def find_key(dict, val):
        return next(key for key, value in dict.items() if value == val)

# hedge monitoring
class MonitoringHedge(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cycle = 60 * 2
        # self.cycle = 5

    def run(self):   
        binance = ccxt.binance()
        while True:
            debug('binance hedge monitoring', 1)
            send_message('binance hedge monitoring')
            time.sleep(self.cycle)



def future_monitoring():
    pass

# hedge exit
def future_exit():
    pass

# print debugging message
debugging = True
def debug(msg, level):
    global debugging

    if debugging:
        if level == 1:
            print(datetime.now().strftime('%m-%d %H:%M:%S'), msg)
        elif level == 2:
            # print("\t", datetime.now().strftime('%m-%d %H:%M:%S'), msg)
            print("\t", datetime.now().strftime('%M:%S'), msg)


# upbit exchange rate "USD/KRW"
def get_exchange_rate():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    exchange =requests.get(url, headers=headers).json()
    # print(exchange[0]['basePrice'])
    return exchange[0]['basePrice']

# send telegram message
telegram_token = '5031482380:AAFE6M7kGiKblwFW0Le80K9S80ebl7OSqzY'
telegram_chatid = '1345959203'
bot = telegram.Bot(token=telegram_token)

def send_message(text):
    bot.sendMessage(telegram_chatid, text=text)

def Autoplay():
    message = 'trading 2 pair'
    debug(message, 1)
    send_message(message)
    
    # exchanged fee(%)
    upbit_fee = 0.05
    binance_fee = 0

    # wanted profit
    profit = 0.1

    # once trade price(USDT)
    trading_usdt = 800
    trading_krw = 1000000


def main():
    while True:
        Autoplay()
        time.sleep(60*2)

if __name__ == "__main__":
    debug("START Wallet", 1)

    # monitoring_kp_threading
    monitoring_kp = MonitoringKP()
    monitoring_kp.setDaemon(True)
    monitoring_kp.start()

    monitoring_hg = MonitoringHedge()
    monitoring_hg.setDaemon(True)
    monitoring_hg.start()

    main()