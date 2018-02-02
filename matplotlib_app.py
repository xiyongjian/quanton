import pandas as pd
import numpy as np
import matplotlib as plt

def plot_pi() :
    import numpy as np
    import matplotlib.pyplot as plt

    X = np.linspace(-np.pi, np.pi, 256, endpoint=True)
    C, S = np.cos(X), np.sin(X)

    plt.plot(X, C)
    plt.plot(X, S)

    plt.show()

def plot_pi2() :
    # Imports
    import numpy as np
    import matplotlib.pyplot as plt

    # Create a new figure of size 8x6 points, using 100 dots per inch
    plt.figure(figsize=(8, 6), dpi=80)

    # Create a new subplot from a grid of 1x1
    plt.subplot(111)

    X = np.linspace(-np.pi, np.pi, 256, endpoint=True)
    C, S = np.cos(X), np.sin(X)

    # Plot cosine using blue color with a continuous line of width 1 (pixels)
    plt.plot(X, C, color="blue", linewidth=1.0, linestyle="-")

    # Plot sine using green color with a continuous line of width 1 (pixels)
    plt.plot(X, S, color="green", linewidth=1.0, linestyle="-")

    # Set x limits
    plt.xlim(-4.0, 4.0)

    # Set x ticks
    plt.xticks(np.linspace(-4, 4, 9, endpoint=True))

    # Set y limits
    plt.ylim(-1.0, 1.0)

    # Set y ticks
    plt.yticks(np.linspace(-1, 1, 5, endpoint=True))

    # Save figure using 72 dots per inch
    # savefig("../figures/exercice_2.png",dpi=72)

    # Show result on screen
    plt.show()

def plot_random() :
    # plt.interactive(False)
    ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))

    # fig, (ax1) = plt.pyplot.subplots(1, 1)
    ts = ts.cumsum()
    ts.plot()
    plt.pyplot.show()

def plot_performance() :
    import pickle
    file = "e:\\perf.p"
    print("read performance from pickle : %s"%file)
    perf = pickle.load(open(file, 'rb'))
    print("dir perf : %s"%(str(dir(perf)).replace(",", ",\n")))

    import matplotlib.pyplot as plt
    # Plot the portfolio and asset data.
    ax1 = plt.subplot(211)
    perf.portfolio_value.plot(ax=ax1)
    # ax1.set_ylabel('Portfolio value (ZAR)')
    # Show the plot.
    # plt.pyplot.gcf().set_size_inches(18, 8)
    plt.show()

def plot01() :
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(211)
    ax.plot([1, 2, 3, 4], [10, 20, 25, 30], color='lightblue', linewidth=3)
    ax.scatter([0.3, 3.8, 1.2, 2.5], [11, 25, 9, 26], color='darkgreen', marker='^')
    ax.scatter([0.3, 3.8, 1.2, 2.5], [11-1, 25-1, 9-1, 26-1], color='darkgreen', marker='v')
    ax.set_xlim(0.5, 4.5)
    plt.show()

if __name__ == '__main__' :
    plot01()
    # plot_random();
    plot_performance()
    print("Done")
