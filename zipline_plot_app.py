from zipline.api import order, record, symbol

from matplotlib import style

style.use('ggplot')

def initialize(context):
    context.sab = symbol('JSE:SAB')
    context.stx = symbol('JSE:STX40')

def handle_data(context, data):
    # Save values for later inspection
    price_sab = data.history(context.sab, "price", bar_count=30, frequency="1d")
    pct_change_sab = (price_sab.ix[-1] - price_sab.ix[0]) / price_sab.ix[0]
    price_stx = data.history(context.stx, "price", bar_count=30, frequency="1d")
    pct_change_stx = (price_stx.ix[-1] - price_stx.ix[0]) / price_stx.ix[0]
    record(SAB=pct_change_sab,
           STX=pct_change_stx)

def analyze(context=None, results=None):

    import matplotlib.pyplot as plt
    fig, (ax1) = plt.subplots(1, 1)
    ax1.plot(results.STX, lw=2,  color="#179349")
    ax1.plot(results.SAB, lw=2)
    ax1.fill_between(results.STX.index, results.STX, color="#179349", alpha=0.5)
    ax1.set_ylabel('Price percentage change')
    plt.show()

