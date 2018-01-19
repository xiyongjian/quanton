'''
run single stock (IBM or a stock 603993
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

# stocks = ['IBM']

def initialize(context):
    context.symbols = [symbol(s) for s in ['IBM']]
    pass


def handle_data(context, data):
    global count
    count = count + 1
    if count == 1:
        print("handle_data, count %d, data %s"%(count, data))
        print("handle_data, current time : ", data.current_dt)
        print("IBM : ", data.current(symbol('IBM'), 'price'))
        order(symbol('IBM'), 10)
        #print(data.history(context.symbols, 'price', 10, '1d'))
        #print(type(data.history(context.symbols, 'price', 10, '1d')))


data = OrderedDict()
data['IBM'] = pd.read_csv('data/IBM.csv', index_col='date', parse_dates=['date']).tail(2770)
panel = pd.Panel(data)
algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
perf_manual = algo_obj.run(panel)
# print(perf_manual)
