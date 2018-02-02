'''
run single A-Stock 603997, version 3
gate for list_0 let in
all other conditions apply following, sequentially -> buy list
'''
from collections import OrderedDict
import pytz
from datetime import timedelta
from zipline import TradingAlgorithm
import pandas as pd
from zipline.api import (order, symbol)
import numpy as np
import re

import sys
import logbook
# logging setup
if True :
    # handler = logbook.StreamHandler(sys.stdout, level=logbook.INFO)
    # handler.formatter.format_string = '{record.time}|{record.level_name}|{record.filename}|{record.module}|{record.func_name}|{record.lineno}|{record.message}'
    handler = logbook.StreamHandler(sys.stdout, level=logbook.DEBUG)
    handler.formatter.format_string = '{record.time}|{record.level_name}|{record.module}|{record.func_name}|{record.lineno}|{record.message}'
    handler.push_application()
    log = logbook.Logger("zipline_astock01")
    # or using this : with handler.applicationbound():

if __name__ == '__main__' :
    log.info("it's __main__, do something")

    log.info('load data')
    data = OrderedDict()
    # df = pd.read_csv('data/603997.csv', index_col='date', parse_dates=['date']).tail(2770)
    df = pd.read_csv('data/603997.csv', index_col='date', parse_dates=['date']).tail(100)
    df['test'] = [i for i in range(len(df.index))]
    log.info(df.columns)
    log.info(df.head(5))
    data['603997'] = df
    panel = pd.Panel(data)
    print(panel.major_axis.time)
    print(type(panel.major_axis.time))
    times = panel.major_axis.time
    print("==", np.all(times == times[0]))
    print(panel.major_axis.date)
    print(type(panel.major_axis))
    print(panel.major_axis[0])
