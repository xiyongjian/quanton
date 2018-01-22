'''
run single A-Stock 603997
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

if True:
    from pandas_datareader.google.daily import GoogleDailyReader
    @property
    def url(self):
        print("call @property get url, %s, %s" % (self, type(self)))
        return 'http://finance.google.com/finance/historical'
    GoogleDailyReader.url = url

if True :
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
            pass

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
                pass

            assert idx + 1 <= self.window_size, "current index %d + 1 must <= window_size %d"%(idx, self.window_size)
            for name, df in self.factors.items() :
                if name == 'sma5' :
                    df.iloc[idx] = data.history(self.symbols, "close", 5, '1d').mean()
                    pass
                elif name == 'sma20' :
                    df.iloc[idx] = data.history(self.symbols, "close", 20, '1d').mean()
                    pass

            self.current_data = data
            self.current_sn = sn
            pass

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

def prepare_batch(sn, context, data) :
    batch = context.batch;
    print("prepare_batch, sn %d, batch base_sn %d"%(sn, batch.base_sn))
    batch.prepare(sn, data);
    # todo : check batch base_sn and sn, remove/rolling 1/2 span upward
    # todo : check batch's watchlist, remove symbols old than span

stocks = ['603997']

def initialize(context):
    context.symbols = [symbol(s) for s in stocks]
    context.sn = 0
    batch = Batch(context.sn + 1, context.symbols, ("sma5", "sma20"), 30)
    context.batch = batch
    # context.strategy = createStrategy(createStatements())
    context.strategy = createStrategy(createStatements())
    context.strategy.initialize(context.batch)
    pass

def handle_data(context, data):
    sn = context.sn
    sn = sn + 1
    context.sn = sn

    if sn < 25 :
        return

    log.info("-------- SN %d -----------"%sn)
    prepare_batch(sn, context, data)
    # strategy = context.strategy
    # strategy.perform(batch)     # will call order or sell

    ##################################################################
    # for debug only
    if sn == 99 :       # for debug/testing only
        context.batch.dump();
        print("history 5 : \n%s"%data.history(context.symbols, 'close', 5, '1d'))
        print("current : \n%s"%data.current(context.symbols, 'close'))

    if False and sn >= 28 :
        print("portfolio, %s"%context.portfolio)
        order(context.symbols[0], 10)

    # test Factor
    ##################################################################

class Strategy() :
    def __init__(self, procedures):
        self.procedures = procedures
        self.total_steps = len(procedures)
        pass

    def initialize(self, batch) :
        log.info("Strategy init batch, setup watchlist")
        batch.watch_lists = {};
        for p in self.procedures :
            batch.watch_lists[p['input']] = [];
            batch.watch_lists[p['output']] = [];
        log.info("build watchlist : %s"%batch.watch_lists)

    def perform(self, batch) :
        ## leave here for reference
        #    try :
        #        x = eval(statement)
        #        print("eval statement : %s, result : %s, type %s"%(statement, x, type(x)));
        #    except Exception as e :
        #        print("eval statement : %s"%statement);
        #        raise e
        pass

# match expressiong
# example : sma[0] - 0.5
# match = re.match(r' *(\w+)\[(\d+)\]( *[+\-\*/] *\d+(\.\d+)*)', expr)
# self.eval_expr = "batch.get('%s', %s) %s"%(match.group(1), match.group(2), match.group(3));

def createStrategy(str) :
    '''
    example statements :
        'sma5[0] + price[-1] > sma20[0] + 2'
    been translated to :
        batch.get("sma5", 0) + batch.get("price", -1) > batch.get("sma20", 0) + 2
    :param statements:
    :return:
    '''
    procedures = []
    statements = str.splitlines()
    inputs = set()
    outputs = set()
    for i, s in enumerate(statements):
        log.info("%2d statement : %s"%(i, s))
        # t = re.sub(r'([^\d\W]\w*)\[([-]*\d+)\]', r'batch.get("\1", \2)', s)
        # t = t.strip()
        if s.startswith("#") or s.strip() == "":
            log.info("comments or empty, pass")
            continue;
        ss = s.split(",")
        proc = {}
        proc['name'] = ss[0].strip()
        proc['type'] = ss[1].strip()
        proc['input'] = ss[2].strip()
        t = re.sub(r'([^\d\W]\w*)\[([-]*\d+)\]', r'batch.get(LIST, "\1", \2)', ss[3])
        t = re.sub(r'LIST', "'%s'"%proc['input'], t)
        proc['condition'] = t
        proc['output'] = ss[4].strip()
        dump_proc(proc)
        inputs.add(proc['input'])
        outputs.add(proc['output'])
        procedures.append(proc)

    log.info("total input : %s"%inputs)
    log.info("total output : %s"%outputs)

    return Strategy(proc_steps)

def dump_proc(proc) :
    assert proc['type'] in ['filter', 'gate'], "proc type %s must be 'filter' or 'gate'"%proc['type']
    log.info("proc name %s, type %s, input %s, output %s, condition %s"\
             %(proc['name'], proc['type'], proc['input'], proc['output'], proc['condition']))
    pass

def createStatements() :
    return \
'''
# comment line, ignore (emtpy line ignor either)
# proposed scripting :
0, gate, ALL  ,   (sma20[0] > price[0]),  list_0
1, filter, list_0, (sma5[0] > price[0]),  list_1
2, gate,  list_1, (sma5[0] > sma20[0]), buy
'''

if __name__ == '__main__' :
    if True :
        log.info("do some testing ONLY")
        createStrategy(createStatements())
        quit()

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
    algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)

    log.info('run algorithm')
    perf_manual = algo_obj.run(panel)
    # print(perf_manual)
    log.info('done')
