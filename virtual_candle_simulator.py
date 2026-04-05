# virtual_candle_simulator.py
# Read candlestick CSV data and plot OHLC chart with volume

import matplotlib
matplotlib.use('TkAgg')  # Or 'Qt5Agg', 'Agg' for non-GUI environments
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc

def plot_candlestick(df):
    """
    Plot OHLC candlestick chart from DataFrame.
    DataFrame must contain: DATETIME, OPEN, HIGH, LOW, CLOSE, VOLUME, SPREAD
    """
    if df.empty:
        print("DataFrame is empty. Nothing to plot.")
        return

    # Convert DATETIME to datetime object
    df['DateTime'] = pd.to_datetime(df['DATETIME'])
    df = df.set_index('DateTime')

    # Convert prices to numeric
    df[['OPEN', 'HIGH', 'LOW', 'CLOSE']] = df[['OPEN', 'HIGH', 'LOW', 'CLOSE']].apply(pd.to_numeric)

    # Convert datetime to float for candlestick plotting
    df['DateNum'] = mdates.date2num(df.index)

    # Create figure and axes
    fig, (ax_candle, ax_volume) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                               gridspec_kw={'height_ratios': [3, 1]})

    # Plot candlesticks
    candlestick_ohlc(ax_candle, df[['DateNum', 'OPEN', 'HIGH', 'LOW', 'CLOSE']].values,
                     width=0.005, colorup='green', colordown='red')

    ax_candle.set_ylabel('Price')
    ax_candle.set_title('Candlestick Chart')
    ax_candle.grid(True)

    # Plot volume
    ax_volume.bar(df['DateNum'], df['VOLUME'], width=0.005, color='blue', alpha=0.4)
    ax_volume.set_ylabel('Volume')
    ax_volume.set_xlabel('Date and Time')
    ax_volume.grid(True)

    # Format x-axis
    ax_candle.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax_candle.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    try:
        df = pd.read_csv("candlestick_data.csv")
        plot_candlestick(df)
    except FileNotFoundError:
        print("CSV file not found. Please run candle_generator.py first.")