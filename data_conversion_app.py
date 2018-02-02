'''
convert data, csv multiple stock minutes data to panel, index with date
'''
import pandas as pd

def step01() :
    file = "e:\\tmp\\quant\\data\\StockData_v2.csv"
    path = "e:\\tmp\\quant\\data\\"

    df = pd.read_csv(file)
    print(df.shape)
    print(df.index[:20])
    print(df.columns)
    print(df.code.unique())

    datas = {}
    columns = [ c.strip() for c in df.columns ]
    print(columns)
    df.rename(columns = lambda x : x.strip(), inplace = True)

    rem_thousand_sep_and_cast_to_float = lambda x: pd.np.float(x.replace(",", ""))

    def convert(x):
        try:
            return pd.np.float(x.replace(",", ""))
        except Exception as e:
            return None

    for s in df.code.unique() :
        t = df[df['code'] == s][['time', 'open', 'high', 'low', 'close', 'volume']]
        print("stock %s, shape %s"%(s, t.shape))
        t['time'] = pd.to_datetime(t['time'])
        t.set_index('time', inplace = True)
        t.sort_index(ascending=True, inplace=True)
        print(type(t))
        # print(t['open'])
        print(t.head(10))
        datas[s] = t
        print("index type  %s"%(type(t.index)))
        print("index ", t.index[:10])
        print("index ", t.index.values[:10])

        t['volume'] = t['volume'].map(convert)
        t.to_csv(path + s + ".csv")
        pass
    pass
    print("done")

def step02() :
    file = "e:\\tmp\\quant\\data\\601336.SH.csv"
    df = pd.read_csv(file)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace = True)
    print(type(df.index))
    print(df.head(10))
    print(df.info())
    df.to_csv(file + ".conv.csv")

    if False :
        dt = pd.to_datetime(df.index)
        print(type(dt))
        print(dt[:10])

    pass

def step03() :
    file = "e:\\tmp\\quant\\data\\601336.SH.csv.conv.csv"
    df = pd.read_csv(file)
    df['time'] = pd.to_datetime(df['time'])
    print(type(df['time']))
    print(df.head(10))
    df.set_index('time', inplace = True)
    print(df.info())

    df.sort_index(ascending=True, inplace=True)
    dt = df.index
    print(type(dt))
    print(type(dt[1]))

    clock_file = "e:\\tmp\\quant\\data\\clock.csv"
    print("write datetime index to clock file : ", clock_file)
    pd.Series(dt).to_csv(clock_file)

def step04() :
    clock_file = "e:\\tmp\\quant\\data\\clock.csv"
    series = pd.Series.from_csv(clock_file)
    print(type(series))
    series = pd.to_datetime(series)
    print(type(series.values))
    print(series[:10])

if __name__ == "__main__" :
    step03()

    pass
