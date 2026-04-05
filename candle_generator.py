# final_candle_generator.py
# Generate 20 realistic candlestick OHLC data for main reference

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_candles(
    num_candles=20,             # default 20 candles
    start_price=4000.0,
    timeframe_minutes=15,
    base_volatility=0.005,      # average % change per candle
    wick_ratio=0.3,
    spread_ratio_min=0.0003,
    spread_ratio_max=0.001,
    volume_min=100,
    volume_max=5000,
    trading_hours=(9, 17)       # hours of active trading (9AM-5PM)
):
    """
    Generate realistic candlestick OHLC data for primary reference.

    Returns:
    - pd.DataFrame with columns: DATETIME, OPEN, HIGH, LOW, CLOSE, SPREAD, VOLUME
    """
    data = []
    prev_close = start_price
    current_datetime = datetime.now().replace(second=0, microsecond=0)

    for _ in range(num_candles):
        # Skip non-trading hours
        while not (trading_hours[0] <= current_datetime.hour < trading_hours[1]) or current_datetime.weekday() >= 5:
            current_datetime += timedelta(minutes=timeframe_minutes)

        # Dynamic volatility: simulate session variation
        volatility = base_volatility * np.random.uniform(0.5, 1.5)
        change_pct = np.random.normal(0, volatility)
        close_price = prev_close * (1 + change_pct)
        open_price = prev_close

        body = abs(close_price - open_price)

        # Wick proportional + noise
        high_wick = np.random.uniform(0, body * wick_ratio + 1)
        low_wick = np.random.uniform(0, body * wick_ratio + 1)
        high_price = max(open_price, close_price) + high_wick
        low_price = min(open_price, close_price) - low_wick

        # Spread proportional to price + small random
        spread = prev_close * np.random.uniform(spread_ratio_min, spread_ratio_max)

        # Volume proportional to body + noise
        volume_factor = min(body / (prev_close * base_volatility * 3), 1)
        volume = int(volume_min + (volume_max - volume_min) * volume_factor * np.random.uniform(0.8, 1.2))

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
    df = generate_candles()  # default 20 candle
    df.to_csv("candlestick_data.csv", index=False)
    print("🔥 Ultra realistic candles generated!")
    print(df)