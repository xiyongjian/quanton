'''
another simple and workable version
'''
from collections import OrderedDict
import pytz
from datetime import timedelta
from zipline import TradingAlgorithm
import pandas as pd
from zipline.api import (order, symbol)

if True:
    from pandas_datareader.google.daily import GoogleDailyReader


    @property
    def url(self):
        print("call @property get url, %s, %s" % (self, type(self)))
        return 'http://finance.google.com/finance/historical'


    GoogleDailyReader.url = url

count = 0


def initialize(context):
    context.symbols = [symbol(s) for s in ['AAPL', 'IBM', 'MSFT', 'GOOG']]
    pass


def handle_data(context, data):
    global count
    count = count + 1
    if count == 500:
        print("handle_data : ", data)
        print("handle_data, current time : ", data.current_dt)
        print("APPL : ", data.current(symbol('AAPL'), 'price'))
        print("IBM : ", data.current(symbol('IBM'), 'price'))
        print("MSFT : ", data.current(symbol('MSFT'), 'price'))
        print("GOOG : ", data.current(symbol('GOOG'), 'price'))
        order(symbol('AAPL'), 10)
        print(data.history(context.symbols, 'price', 10, '1d'))
        print(type(data.history(context.symbols, 'price', 10, '1d')))


data = OrderedDict()
data['AAPL'] = pd.read_csv('data/AAPL.csv', index_col='date', parse_dates=['date']).tail(2000)
data['IBM'] = pd.read_csv('data/IBM.csv', index_col='date', parse_dates=['date']).tail(2000)
data['GOOG'] = pd.read_csv('data/GOOG.csv', index_col='date', parse_dates=['date']).tail(2000)
data['MSFT'] = pd.read_csv('data/MSFT.csv', index_col='date', parse_dates=['date']).tail(2000)
panel = pd.Panel(data)
algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
perf_manual = algo_obj.run(panel)
# print(perf_manual)
