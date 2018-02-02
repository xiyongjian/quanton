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

# sn : serial number, or step number,  unit is handle_data's time span
#    initial start sn
# span : total sn in this batch, define moving rolling window [sn, sn + span)
#       span should be 2x of actual requirement for optimzation
#       span/2 tomoving upper..
class Batch :
    def __init__(self, base_sn, symbols, factor_names, span):
        self.base_sn = base_sn
        self.span = span
        self.window_size = span * 2 + 1
        self.factors = {}
        for factor in factor_names :
            df = pd.DataFrame(np.zeros((self.window_size, len(symbols))), index=range(base_sn, base_sn + self.window_size), columns=symbols)
            self.factors[factor] = df
        self.symbols = symbols;
        self.watch_lists = {}   # or move this list to stetegy? we may have multiple Batch??
        self.orders = []
        # each items as dict format : 'sn', 'type"/buy or sell, 'symbol', 'volume'
        pass

    # name : watch_lists name
    # until_sn : get all symbols until this sn
    # return : symbol list in the list until_sn
    def get_watch_list_at(self, name, pos) :
        assert pos <= 0, "get_watch_list_at, pos %d must <= 0"%pos
        until_sn = self.current_sn + pos
        ret = set()
        if name in self.watch_lists :
            for sn, l in self.watch_lists[name].items() :
                if sn == until_sn :
                    ret.update(l);
        return list(ret)

    def get_watch_list(self, name, pos) :
        assert pos <= 0, "get_watch_list, pos %d must <= 0"%pos
        until_sn = self.current_sn + pos
        ret = set()
        if name in self.watch_lists :
            for sn, l in self.watch_lists[name].items() :
                if sn <= until_sn :
                    ret.update(l);
        return list(ret)

    def set_watch_list(self, name, watch_list) :
        self.watch_lists[name] = {self.current_sn : watch_list}
        pass

    def add_watch_list(self, name, watch_list) :
        self.watch_lists[name][self.current_sn] = watch_list
        pass

    def reset_watch_list(self, name) :
        self.watch_lists[name] = {}

    def dump(self):
        print("batch base_sn : %d"%self.base_sn)
        print("span : %d, window_size : %d"%(self.span, self.window_size))
        print("current_sn : %d"%(self.current_sn))
        print("symbols : %s"%self.symbols)
        for name, factor in self.factors.items() :
            print("factor name %s, value :\n%s"%(name, factor))
        for name, wl in self.watch_lists.items() :
            print("watchlie %s, value :\n%s"%(name, wl))

    def prepare(self, sn, data):
        '''
        calculate neccessary factor we need
        :param data:
            data is passed as parameter of handle_data
        :return:
        '''
        # print("sn %d, prepare data for %d"%(sn, self.sn))
        # rolling watch_list, remove old (current_sn - sn > 60) ones
        idx = sn - self.base_sn
        if idx + 1 == self.window_size :    # current windows is full, clean first half and rolling up
            size = self.span    # int(self.window_size / 2 - 1)    # rollling size
            log.info("rolling window at size %d"%size)

            current_end_sn = self.base_sn + self.window_size
            new_base_sn = self.base_sn + size
            new_end_sn = new_base_sn + self.window_size
            log.info("rolling from [%d %d] to [%d %d]"%(self.base_sn, current_end_sn, new_base_sn, new_end_sn))
            for factor, df in self.factors.items() :
                new_df = pd.DataFrame(np.zeros((new_end_sn - current_end_sn, len(self.symbols))), \
                                      index=range(current_end_sn, new_end_sn), columns=self.symbols)
                self.factors[factor] = pd.concat([ df.loc[range(new_base_sn, current_end_sn)], new_df ])
                pass

            self.base_sn = new_base_sn
            idx = sn - self.base_sn
            self.set_watch_list("ALL", self.symbols)
            pass

        # prepare watch list
        for n, l in self.watch_lists.items() :
            remove_sns = [ i for i in l.keys() if i + self.span < sn ]
            if remove_sns : # if not empty
                log.info("remove from list %s, sn : %s"%(n, remove_sns))
                for s in remove_sns :
                    del l[s]

        assert idx + 1 <= self.window_size, "current index %d + 1 must <= window_size %d"%(idx, self.window_size)
        for name, df in self.factors.items() :
            if name == 'sma5' :
                df.iloc[idx] = data.history(self.symbols, "close", 5, '1d').mean()
                pass
            elif name == 'sma20' :
                df.iloc[idx] = data.history(self.symbols, "close", 20, '1d').mean()
                pass
            elif name == 'slope5' :
                # calculate slope in previous 5 points
                pass

        self.current_data = data
        self.current_sn = sn
        pass

    # todo : get_watch_list_param_hist(self, watch_list, name, from , to)
    def get_watch_list_param(self, watch_list, name, pos) :
        assert watch_list in self.watch_lists, "watch_list %s must be in watch_lists [%s]"%(watch_list, self.watch_lists.keys())
        symbols = set()
        for sn, l in self.watch_lists[watch_list].items() :
            symbols.update(l);
        # log.info("symbols %s"%symbols)
        # log.info("get name %s pos %d : %s"%(name, pos, self.get(name, pos)))
        # log.info("get name %s pos %d type : %s"%(name, pos, type(self.get(name, pos))))
        return self.get(name, pos)[list(symbols)];
        pass

    # todo : get_hist(self, name, from, to)
    def get(self, name, pos) :
        assert pos <= 0, "batch get() pos (%d) must <= 0"%pos
        params = ['sma5', 'sma20', 'price']
        assert name in params, 'name %s must be within params [%s]'%(name, params)
        #  total sn   4      1 2 3 4
        #                    |--------- 1  base_sn
        #                          | -- 4  current_sn, idx = 3
        # if pos = -1            | -----3, pos -1, , idx = 2
        idx = self.current_sn - self.base_sn + pos
        assert idx < self.window_size, \
            "idx %d (from pos %d) must < window_size %d"%(idx, pos, self.window_size)
        if name == 'price' :
            return self.current_data.history(self.symbols, 'close', 1 - pos, '1d').iloc[0]
            pass
        elif name == 'sma5' :
            return self.factors['sma5'].iloc[idx]
            pass
        elif name == 'sma20' :
            return self.factors['sma20'].iloc[idx]
            pass

if __name__ == '__main__' :
    # logging setup
    # handler = logbook.StreamHandler(sys.stdout, level=logbook.INFO)
    # handler.formatter.format_string = '{record.time}|{record.level_name}|{record.filename}|{record.module}|{record.func_name}|{record.lineno}|{record.message}'
    handler = logbook.StreamHandler(sys.stdout, level=logbook.DEBUG)
    handler.formatter.format_string = '{record.time}|{record.level_name}|{record.module}|{record.func_name}|{record.lineno}|{record.message}'
    handler.push_application()
    log = logbook.Logger("zipline_astock01")
    # or using this : with handler.applicationbound():

    log.info("Batch builtin testing")
