
'''
convert data, 5-min to 1 day index, refer AAPL, to latest one.
'''
import pandas as pd

if False :
    df = pd.DataFrame.from_csv("data/StockPrice_5Min_Subset.csv")
    print(df.columns)
    print(df.index)

cut_number = 2770     # # of tail rows to cut
df_in = pd.read_csv('data/StockPrice_5Min_Subset.csv', index_col='date', parse_dates=['date']).tail(cut_number)
df_ibm = pd.read_csv('data/IBM.csv', index_col='date', parse_dates=['date']).tail(cut_number)

print(df_in.columns)
print(df_ibm.columns)

stock = df_in['code'][0]
print("stock : ", stock)

# print(df_in.head(10))
# drop unused columns
df = df_in.drop(['Unnamed: 0', 'name', 'code'], axis=1)
# add ibm's date index as column
df['date'] = df_ibm.index
# set new index and discard the old one
df = df.set_index('date')
print(df.head(10))
print(df_ibm.head(10))

print("stock : ", stock)
file = "data/%s.csv"%stock
print("write to stock csv : ", file)
df.to_csv(file);

df_ibm.to_csv("data/aIBM.csv")
