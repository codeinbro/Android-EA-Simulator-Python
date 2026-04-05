# candle_generator.py
# Generate realistic random candles with OHLC + Volume + Spread + Timestamp
# Open of next candle = Close of previous candle
# Output CSV default: generated_candles.csv
# Android / Pydroid friendly
# Comments in English

import random
import csv
from datetime import datetime, timedelta

# ========================
# Configurable parameters
# ========================
num_candles = 20           # number of candles to generate
price_start = 150          # starting price for first candle
price_variation = 5        # max price change per candle
volume_min = 100           # minimum volume
volume_max = 5000          # maximum volume
spread_min = 0.5           # minimum spread
spread_max = 2.0           # maximum spread
interval_minutes = 1       # interval between candles in minutes

# Output CSV file
output_file = 'generated_candles.csv'

# ========================
# Start timestamp
# ========================
start_time = datetime.now()  # starting time for the first candle

# ========================
# Generate candles
# ========================
candles = []
prev_close = price_start

for i in range(num_candles):
    # Open = previous candle close
    o = prev_close
    # High and Low within variation from Open
    h = round(o + random.uniform(0, price_variation), 2)
    l = round(o - random.uniform(0, price_variation), 2)
    # Close somewhere between Low and High
    c = round(random.uniform(l, h), 2)
    # Volume and spread
    v = random.randint(volume_min, volume_max)
    s = round(random.uniform(spread_min, spread_max), 2)
    # Timestamp
    timestamp = start_time + timedelta(minutes=i*interval_minutes)
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    candles.append({
        'timestamp': timestamp_str,
        'open': o,
        'high': h,
        'low': l,
        'close': c,
        'volume': v,
        'spread': s
    })

    prev_close = c  # set close as next open

# ========================
# Save to CSV
# ========================
with open(output_file, 'w', newline='') as f:
    fieldnames = ['timestamp','open','high','low','close','volume','spread']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(candles)

print(f"{num_candles} connected candles created and saved to {output_file}")