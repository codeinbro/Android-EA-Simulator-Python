# virtual_candle_simulator.py
# Read candlestick CSV data and plot OHLC chart

import matplotlib
matplotlib.use('TkAgg')  # Or 'Qt5Agg', 'Agg' for non-GUI environments
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc

def plot_candlestick(df):
    """
    Plot OHLC candlestick chart from DataFrame.
    DataFrame must contain: DATE, TIME, OPEN, HIGH, LOW, CLOSE
    """
    if df.empty:
        print("DataFrame is empty. Nothing to plot.")
        return

    # Combine date and time
    df['DateTime'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'])
    df = df.set_index('DateTime')

    # Convert prices to numeric
    df[['OPEN', 'HIGH', 'LOW', 'CLOSE']] = df[['OPEN', 'HIGH', 'LOW', 'CLOSE']].apply(pd.to_numeric)

    # Convert datetime to float for candlestick plotting
    df['DateNum'] = mdates.date2num(df.index)

    fig, ax = plt.subplots(figsize=(12,6))
    candlestick_ohlc(ax, df[['DateNum', 'OPEN', 'HIGH', 'LOW', 'CLOSE']].values,
                     width=0.005, colorup='green', colordown='red')

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Date and Time')
    plt.ylabel('Price')
    plt.title('Candlestick Chart')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    try:
        df = pd.read_csv("candlestick_data.csv")
        plot_candlestick(df)
    except FileNotFoundError:
        print("CSV file not found. Please run candle_generator.py first.")