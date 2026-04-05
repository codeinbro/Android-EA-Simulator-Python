# candle_generator_to_csv.py
# Generate realistic connected candles and save to CSV
# Android / Pydroid friendly

import random
import csv
from datetime import datetime, timedelta

# ========================
# Configurable parameters
# ========================
num_candles = 50      # total candles
price_start = 4000.0  # starting price
price_variation = 10.0 # max change per candle
volume_min = 100
volume_max = 5000
spread_min = 0.5
spread_max = 2.0
timeframe = 'H1'      # H1 / H4 / D1

# Output CSV file
output_file = 'generated_candles.csv'

# ========================
# Timeframe to minutes
# ========================
timeframe_map = {'H1':60, 'H4':240, 'D1':1440}
interval_minutes = timeframe_map.get(timeframe.upper(), 60)

# ========================
# Generate candles
# ========================
candles = []
prev_close = price_start
trend = 0
start_time = datetime.now()

for i in range(num_candles):
    # Small trend to avoid random jumps
    trend += random.uniform(-price_variation/4, price_variation/4)
    
    o = round(prev_close + trend, 2)
    h = round(max(o, o + random.uniform(0, price_variation/2)), 2)
    l = round(min(o, o - random.uniform(0, price_variation/2)), 2)
    c = round(random.uniform(l, h), 2)
    
    v = random.randint(volume_min, volume_max)
    s = round(random.uniform(spread_min, min(spread_max, price_variation/5)), 2)
    
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
    
    prev_close = c  # next candle open

# ========================
# Save to CSV
# ========================
with open(output_file, 'w', newline='') as f:
    fieldnames = ['timestamp','open','high','low','close','volume','spread']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(candles)

print(f"{num_candles} realistic candles generated and saved to {output_file}")