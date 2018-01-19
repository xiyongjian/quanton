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

if True:
    from pandas_datareader.google.daily import GoogleDailyReader
    @property
    def url(self):
        print("call @property get url, %s, %s" % (self, type(self)))
        return 'http://finance.google.com/finance/historical'
    GoogleDailyReader.url = url

if True :
    class Batch :
        def __init__(self, sn, symbols, factor_names, total_steps):
            self.sn = sn
            self.total_steps = total_steps
            self.factors = {}
            for factor in factor_names :
                df = pd.DataFrame(np.zeros((total_steps, len(symbols))), index=range(total_steps), columns=symbols)
                self.factors[factor] = df
            self.symbols = symbols;
            self.mask = pd.Series((True for i in range(len(symbols))));
            pass

        def dump(self):
            print("batch sn : %d"%self.sn)
            print("total_steps : %d, current_step : %d"%(self.total_steps, self.current_step))
            print("symbols : %s"%self.symbols)
            print("mask, type %s, value  : %s"%(type(self.mask), self.mask))
            # print("factors : %s"%self.factors)
            for name, factor in self.factors.items() :
                print("factor name %s, value :\n%s"%(name, factor))

        def prepare(self, sn, data):
            '''
            calculate neccessary factor we need
            :param data:
                data is passed as parameter of handle_data
            :return:
            '''
            # print("sn %d, prepare data for %d"%(sn, self.sn))
            idx = sn - self.sn
            assert idx + 1 <= self.total_steps, "current index %d + 1 must <= total_steps %d"%(idx, self.total_steps)
            for name, df in self.factors.items() :
                if name == 'sma5' :
                    df.iloc[idx] = data.history(self.symbols, "close", 5, '1d').mean()
                    pass
                elif name == 'sma20' :
                    df.iloc[idx] = data.history(self.symbols, "close", 20, '1d').mean()
                    pass

            self.current_data = data
            self.current_step = idx + 1    # step is 1 based!
            pass

        def get(self, name, pos) :
            assert pos <= 0, "batch get() pos (%d) must <= 0"%pos
            params = ['sma5', 'sma20', 'price']
            assert name in params, 'name %s must be within params [%s]'%(name, params)
            #  total step 4      1 2 3 4
            #                          | -- 3  # actual pos for pos 0
            #                        | ---- 2  # actual pos for pos -1
            #                    |--------- 0
            idx = self.total_steps + pos - 1
            assert idx < self.total_steps, \
                "idx %d (from pos %d) must < total_steps %d"%(idx, pos, self.total_steps)
            if name == 'price' :
                return self.current_data.history(self.symbols, 'close', self.total_steps, '1d').iloc[idx]
                pass
            elif name == 'sma5' :
                return self.factors['sma5'].iloc[idx]
                pass
            elif name == 'sma20' :
                return self.factors['sma20'].iloc[idx]
                pass

def prepare_batches(sn, context, data) :
    batches = context.batches;
    total_steps = context.strategy.total_steps
    batch = Batch(sn, context.symbols, ("sma5", "sma20"), total_steps)
    batches[sn] = batch
    # print("prepare_batches, sn %d, total batches %d"%(sn, len(batches)))

    # remove old/finished batch
    bsns = [bsn for bsn in batches.keys()]
    for bsn in bsns :
        if sn - bsn + 1 > total_steps : # current step  out of total_steps
            del batches[bsn]

    for batch_sn, batch in batches.items() :
        batch.prepare(sn, data)
        pass
    pass

class Strategy() :
    def __init__(self, proc_steps):
        self.proc_steps = proc_steps
        self.total_steps = len(proc_steps)
        pass

    def perform(self, batch) :
        current_step = batch.current_step;
        assert current_step <= batch.total_steps, \
            "batch %d, current step %d must <= total steps %d"%(batch.sn, current_step, batch.total_steps)
        assert current_step <= len(self.proc_steps), \
            "current step %d must <= len of procs %d"%(current_step, len(self.proc_steps))

        index = current_step - 1
        statement = self.proc_steps[index]
        if statement != "" :    # not empty, eval it
            try :
                x = eval(statement)
                print("eval statement : %s, result : %s, type %s"%(statement, x, type(x)));
            except Exception as e :
                print("eval statement : %s"%statement);
                raise e

            batch.mask = batch.mask & x
        pass

stocks = ['603997']

def initialize(context):
    context.symbols = [symbol(s) for s in stocks]
    context.batches = {}
    context.sn = 0;
    context.strategy = createStrategy(createStatements())
    pass

def handle_data(context, data):
    sn = context.sn
    sn = sn + 1
    context.sn = sn

    if sn < 25 :
        return

    print("\n-------- SN %d -----------"%sn)
    prepare_batches(sn, context, data)
    strategy = context.strategy
    for batch_sn, batch in context.batches.items() :
        strategy.perform(batch)     # will call order or sell
        pass

    ##################################################################
    # for debug only
    if False and sn == 29 :       # for debug/testing only
        for batch_sn, batch in context.batches.items() :
            batch.dump();
        print("history 5 : \n%s"%data.history(context.symbols, 'close', 5, '1d'))

    if False and sn >= 28 :
        print("portfolio, %s"%context.portfolio)
        order(context.symbols[0], 10)

    # test Factor
    ##################################################################

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
    proc_steps = []
    statements = str.splitlines()
    for i, s in enumerate(statements):
        print("%2d statement : %s"%(i, s))
        t = re.sub(r'(\w+\d*)\[([-]*\d+)\]', r'batch.get("\1", \2)', s)
        t = t.strip()
        print("    translate : %s"%t)
        proc_steps.append(t)

    return Strategy(proc_steps)

def createStatements() :
    return \
""" (price[0] > sma5[0] + 0.5) & (price[0] < sma20[0])

price[0] > price[-1]
"""
    pass

if __name__ == '__main__' :
    print("it's __main__, do something")

    print('load data')
    data = OrderedDict()
    # df = pd.read_csv('data/603997.csv', index_col='date', parse_dates=['date']).tail(2770)
    df = pd.read_csv('data/603997.csv', index_col='date', parse_dates=['date']).tail(100)
    df['test'] = [i for i in range(len(df.index))]
    print(df.columns)
    print(df.head(5))
    data['603997'] = df
    panel = pd.Panel(data)
    algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)

    print('run algorithm')
    perf_manual = algo_obj.run(panel)
    # print(perf_manual)
    print('done')

