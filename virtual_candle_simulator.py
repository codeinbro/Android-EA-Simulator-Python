# virtual_candle_simulator_bidask_android.py
# Plot OHLC candlestick chart with Bid/Ask lines (red/green)

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc

def plot_candlestick_with_bid_ask(df):
    """
    Plot OHLC candlestick chart with last candle Bid/Ask lines.
    Bid (red) and Ask (green), no volume plot.
    DataFrame must contain: DATETIME, OPEN, HIGH, LOW, CLOSE, SPREADE
    """
    if df.empty:
        print("DataFrame is empty. Nothing to plot.")
        return

    # Convert DATETIME to datetime object
    df['DateTime'] = pd.to_datetime(df['DATETIME'])
    df = df.set_index('DateTime')

    # Ensure numeric
    df[['OPEN', 'HIGH', 'LOW', 'CLOSE', 'SPREAD']] = df[['OPEN','HIGH','LOW','CLOSE','SPREAD']].apply(pd.to_numeric)
    df['DateNum'] = mdates.date2num(df.index)

    # Last candle prices
    last_close = df['CLOSE'].iloc[-1]
    last_spread = df['SPREAD'].iloc[-1]
    bid_price = last_close - last_spread / 2
    ask_price = last_close + last_spread / 2

    fig, ax = plt.subplots(figsize=(12,6))

    # Plot candles
    candlestick_ohlc(ax, df[['DateNum','OPEN','HIGH','LOW','CLOSE']].values, width=0.005, colorup='green', colordown='red')
    ax.set_ylabel('Price')
    ax.set_title('Candlestick Chart with Bid/Ask Lines (Android style)')
    ax.grid(True)

    # Plot Bid/Ask horizontal lines
    ax.axhline(bid_price, color='red', linestyle='--', label=f'Bid {bid_price:.2f}')
    ax.axhline(ask_price, color='green', linestyle='--', label=f'Ask {ask_price:.2f}')
    ax.legend(loc='upper left')

    # Format x-axis
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    try:
        df = pd.read_csv("candlestick_data.csv")
        plot_candlestick_with_bid_ask(df)
    except FileNotFoundError:
        print("CSV file not found. Please run candle_generator.py first.")