# candle_generator.py
# Generate 25 realistic random candlestick OHLC data with spread & volume

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_realistic_candles(
    num_candles=25,
    start_price=4000.0,
    timeframe_minutes=15,
    max_change_ratio=0.02,  # max % change per candle
    wick_ratio=0.3,
    spread_min=2,
    spread_max=6,
    volume_min=100,
    volume_max=5000
):
    """
    Generate realistic candlestick OHLC data with spread & volume.

    Parameters:
    - num_candles: number of candles
    - start_price: starting price
    - timeframe_minutes: candle interval
    - max_change_ratio: max % change per candle
    - wick_ratio: max wick as fraction of body
    - spread_min, spread_max: spread in points
    - volume_min, volume_max: volume range

    Returns:
    - pd.DataFrame with columns: DATETIME, OPEN, HIGH, LOW, CLOSE, SPREAD, VOLUME
    """
    data = []
    prev_close = start_price
    current_datetime = datetime.now()

    for _ in range(num_candles):
        # Limit price change per candle
        max_change = prev_close * max_change_ratio
        close_price = prev_close + np.random.uniform(-max_change, max_change)
        open_price = prev_close

        body = abs(close_price - open_price)
        # Wick proportional to body, minimal 1 point
        high_wick = np.random.uniform(0, body * wick_ratio + 1)
        low_wick = np.random.uniform(0, body * wick_ratio + 1)

        high_price = max(open_price, close_price) + high_wick
        low_price = min(open_price, close_price) - low_wick

        spread = np.random.uniform(spread_min, spread_max)
        volume = np.random.randint(volume_min, volume_max)

        data.append({
            "DATETIME": current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "OPEN": round(open_price, 2),
            "HIGH": round(high_price, 2),
            "LOW": round(low_price, 2),
            "CLOSE": round(close_price, 2),
            "SPREAD": round(spread, 2),
            "VOLUME": volume
        })

        prev_close = close_price
        current_datetime += timedelta(minutes=timeframe_minutes)

    return pd.DataFrame(data)


if __name__ == "__main__":
    df = generate_realistic_candles()
    df.to_csv("candlestick_data.csv", index=False)
    print("25 realistic candlestick data saved to candlestick_data_realistic.csv")
    print(df)