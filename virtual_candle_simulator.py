# candle_simulator_last_price_spread.py
# Display candlesticks from CSV with spread only at last price
# Android / Pydroid friendly

import matplotlib.pyplot as plt
import pandas as pd

# ========================
# Configurable parameters
# ========================
input_file = 'generated_candles.csv'  # CSV dari candle generator
margin = 15  # extra margin untuk sumbu harga

# ========================
# Baca CSV
# ========================
df = pd.read_csv(input_file, parse_dates=['timestamp'])
df.set_index('timestamp', inplace=True)

# ========================
# Plot candlestick chart
# ========================
fig, ax = plt.subplots(figsize=(14,6))
ax.set_ylim(df['low'].min()-margin, df['high'].max()+margin)

x_pos = list(range(len(df)))

for i, (idx, row) in enumerate(df.iterrows()):
    color = 'green' if row['close'] >= row['open'] else 'red'
    
    # High-Low line
    ax.plot([x_pos[i], x_pos[i]], [row['low'], row['high']], color='black', linewidth=1)
    
    # Open-Close rectangle
    rect_height = row['close'] - row['open']
    bottom = row['open'] if rect_height >=0 else row['close']
    ax.bar(x_pos[i], abs(rect_height), bottom=bottom, width=0.6, color=color, edgecolor='black')

# Last price & spread
last_price = df['close'].iloc[-1]
last_spread = df['spread'].iloc[-1]
ax.axhline(last_price, color='blue', linestyle='--', linewidth=1.5, label=f'Last Price: {last_price}')
ax.axhline(last_price + last_spread, color='orange', linestyle='-', linewidth=1.5, label=f'Spread: {last_spread}')

# X-axis labels
step = max(1, len(df)//10)
ax.set_xticks(x_pos[::step])
ax.set_xticklabels([ts.strftime('%Y-%m-%d %H:%M') for ts in df.index[::step]], rotation=45)

ax.set_ylabel('Price')
ax.set_title(f'Virtual Candle Simulator ({len(df)} candles) with Last Price Spread')
ax.legend()
plt.tight_layout()
plt.show()