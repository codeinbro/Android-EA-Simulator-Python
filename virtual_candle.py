# virtual_candle.py
# Simple virtual candlestick simulator for Android / Python

import matplotlib.pyplot as plt
import time

# Sample candlestick data: [open, high, low, close]
candles = [
    [100, 105, 98, 102],
    [102, 107, 101, 106],
    [106, 108, 103, 104],
    [104, 105, 100, 101]
]

opens = []
highs = []
lows = []
closes = []

plt.ion()  # enable interactive mode

fig, ax = plt.subplots()

for i, c in enumerate(candles):
    opens.append(c[0])
    highs.append(c[1])
    lows.append(c[2])
    closes.append(c[3])

    ax.clear()
    # Draw candles up to current index
    for j in range(len(opens)):
        color = 'green' if closes[j] >= opens[j] else 'red'
        # draw high-low line
        ax.plot([j, j], [lows[j], highs[j]], color='black')
        # draw open-close rectangle
        ax.bar(j, closes[j]-opens[j], bottom=opens[j], width=0.5, color=color)

    ax.set_xticks(range(len(opens)))
    ax.set_xticklabels([f'C{k+1}' for k in range(len(opens))])
    ax.set_ylabel('Price')
    ax.set_title('Virtual Candlestick Simulator')
    plt.pause(1)  # pause 1 second to show candle progressively

plt.ioff()  # turn off interactive mode
plt.show()