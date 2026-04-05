# candle_generator.py
# Generate 25 random but realistic candlestick OHLC data with datetime, volume, and spread

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_random_candles(num_candles=25, start_price=4000.0, timeframe_minutes=15,
                            max_body=3000.0, wick_ratio=0.3, volume_range=(100, 5000),
                            spread_range=(0.5, 2.0)):
    """
    Generate random candlestick OHLC data with datetime, volume, and spread.

    Parameters:
    - num_candles: total candles to generate
    - start_price: starting price for first candle
    - timeframe_minutes: interval per candle in minutes
    - max_body: maximum body size (open-close)
    - wick_ratio: maximum wick as fraction of body
    - volume_range: tuple (min_volume, max_volume)
    - spread_range: tuple (min_spread, max_spread)

    Returns:
    - pd.DataFrame with columns: DATETIME, OPEN, HIGH, LOW, CLOSE, VOLUME, SPREAD
    """
    data = []
    prev_close = start_price
    current_datetime = datetime.now()

    for _ in range(num_candles):
        # Random body
        close_price = prev_close + np.random.uniform(-max_body, max_body)
        open_price = prev_close

        body_range = abs(close_price - open_price)
        # Random wicks proportional to body
        high_wick = np.random.uniform(0, body_range * wick_ratio + 0.1)  # tiny offset
        low_wick = np.random.uniform(0, body_range * wick_ratio + 0.1)

        high_price = max(open_price, close_price) + high_wick
        low_price = min(open_price, close_price) - low_wick

        # Random volume and spread
        volume = np.random.randint(volume_range[0], volume_range[1])
        spread = round(np.random.uniform(spread_range[0], spread_range[1]), 2)

        # Append candle
        data.append({
            "DATETIME": current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "OPEN": round(open_price, 2),
            "HIGH": round(high_price, 2),
            "LOW": round(low_price, 2),
            "CLOSE": round(close_price, 2),
            "VOLUME": volume,
            "SPREAD": spread
        })

        # Prepare for next candle
        prev_close = close_price
        current_datetime += timedelta(minutes=timeframe_minutes)

    return pd.DataFrame(data)


if __name__ == "__main__":
    # Generate 25 realistic random candles
    df = generate_random_candles()
    df.to_csv("candlestick_data.csv", index=False)
    print("25 random candlestick data saved to candlestick_data.csv")
    print(df)