# candle_generator.py
# Generate 25 random but realistic candlestick OHLC data and save to CSV

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_random_candles(num_candles=25, start_price=120000.0, timeframe_minutes=15, max_body=3000.0, wick_ratio=0.3):
    """
    Generate random candlestick OHLC data with realistic rules.

    Parameters:
    - num_candles: total candles to generate (default 25)
    - start_price: starting price for first candle (default 120000)
    - timeframe_minutes: interval per candle in minutes (default 15)
    - max_body: maximum body size (open-close) per candle (default 3000)
    - wick_ratio: maximum wick as fraction of body (default 0.3)

    Returns:
    - pd.DataFrame with columns: DATE, TIME, OPEN, HIGH, LOW, CLOSE
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
        high_wick = np.random.uniform(0, body_range * wick_ratio + 0.1)  # tiny offset for small candles
        low_wick = np.random.uniform(0, body_range * wick_ratio + 0.1)

        high_price = max(open_price, close_price) + high_wick
        low_price = min(open_price, close_price) - low_wick

        # Append candle
        data.append({
            "DATE": current_datetime.strftime("%Y-%m-%d"),
            "TIME": current_datetime.strftime("%H:%M:%S"),
            "OPEN": round(open_price, 2),
            "HIGH": round(high_price, 2),
            "LOW": round(low_price, 2),
            "CLOSE": round(close_price, 2)
        })

        # Prepare for next candle
        prev_close = close_price
        current_datetime += timedelta(minutes=timeframe_minutes)

    return pd.DataFrame(data)

if __name__ == "__main__":
    # Generate 25 realistic random candles
    df = generate_random_candles()
    df.to_csv("candlestick_data.csv", index=False)
    print("25 random candlestick data saved to random_candles.csv")
    print(df)