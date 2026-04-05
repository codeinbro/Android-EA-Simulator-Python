# market_data_bridge.py
import pandas as pd
from time import sleep

class MarketDataBridge:
    """
    MarketDataBridge simulates a broker feed for MT5-like EA testing.
    It converts candlestick data from a generator into a full tick feed,
    including bid/ask, spread, volume, symbol info, account info, and optional fields.
    This allows testing EA strategies without a live broker connection.
    """

    def __init__(self, candle_df, default_spread=0.0001, default_volume=100, timeframe_minutes=15):
        """
        Initialize the bridge with a DataFrame from the candle generator.

        Parameters:
        - candle_df: pd.DataFrame containing columns DATETIME, OPEN, HIGH, LOW, CLOSE, SPREAD, VOLUME
        - default_spread: value to use if SPREAD is missing
        - default_volume: value to use if VOLUME is missing
        - timeframe_minutes: candle timeframe, used to generate DATETIME if missing
        """
        self.candles = candle_df.reset_index(drop=True)
        self.index = 0
        self.default_spread = default_spread
        self.default_volume = default_volume
        self.timeframe_minutes = timeframe_minutes

        # Default symbol information (can be customized)
        self.symbol_info = {
            "POINT": 0.01,           # minimal price change
            "DIGITS": 2,             # number of decimal places
            "CONTRACT_SIZE": 100000, # standard lot size
            "TICK_VALUE": 10,        # value per tick
            "MARGIN_REQ": 1000,      # margin for 1 lot
            "SWAP_LONG": -0.5,       # overnight swap long
            "SWAP_SHORT": -0.3,      # overnight swap short
            "COMMISSION": 2          # per trade commission
        }

        # Default account information
        self.account_info = {
            "BALANCE": 10000,
            "EQUITY": 10000,
            "FREE_MARGIN": 10000,
            "LEVERAGE": 100,
            "CURRENCY": "USD"
        }

        # If DATETIME missing entirely, set start time for generated timestamps
        if "DATETIME" not in self.candles.columns or self.candles["DATETIME"].isnull().all():
            from datetime import datetime
            self.start_time = datetime.now().replace(second=0, microsecond=0)
        else:
            self.start_time = None

    def get_next_tick(self, simulate_realtime=False, sleep_seconds=1):
        """
        Returns the next tick in MT5-like format.

        Parameters:
        - simulate_realtime: if True, delays tick generation by sleep_seconds to simulate real-time
        - sleep_seconds: delay per tick in seconds

        Returns:
        - dict: a tick containing DATETIME, OHLC, BID, ASK, SPREAD, VOLUME,
                SYMBOL_INFO, ACCOUNT_INFO, NEWS_EVENT, SESSION_INFO
        - None: when no more ticks are available
        """

        if self.index >= len(self.candles):
            # End of data
            return None

        row = self.candles.iloc[self.index]

        # Handle missing or NaN values for OHLC, SPREAD, VOLUME, DATETIME
        from datetime import timedelta, datetime

        # Use CLOSE if available, else fallback to OPEN, else 0
        close = row["CLOSE"] if not pd.isna(row.get("CLOSE", None)) else row.get("OPEN", 0)
        open_price = row["OPEN"] if not pd.isna(row.get("OPEN", None)) else close
        high = row["HIGH"] if not pd.isna(row.get("HIGH", None)) else max(open_price, close)
        low = row["LOW"] if not pd.isna(row.get("LOW", None)) else min(open_price, close)
        spread = row["SPREAD"] if not pd.isna(row.get("SPREAD", None)) else self.default_spread
        volume = int(row["VOLUME"]) if not pd.isna(row.get("VOLUME", None)) else self.default_volume

        # Generate timestamp if missing
        if self.start_time:
            datetime_val = (self.start_time + timedelta(minutes=self.index * self.timeframe_minutes)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            datetime_val = row["DATETIME"] if not pd.isna(row.get("DATETIME", None)) else "1970-01-01 00:00:00"

        # Calculate BID and ASK from CLOSE ± half spread
        bid = close - (spread / 2)
        ask = close + (spread / 2)

        tick = {
            "DATETIME": datetime_val,
            "OPEN": open_price,
            "HIGH": high,
            "LOW": low,
            "CLOSE": close,
            "BID": round(bid, 5),
            "ASK": round(ask, 5),
            "SPREAD": round(spread, 5),
            "VOLUME": volume,
            "SYMBOL_INFO": self.symbol_info,     # static symbol info
            "ACCOUNT_INFO": self.account_info,   # static account info
            "NEWS_EVENT": None,                  # optional
            "SESSION_INFO": "London"             # optional, can be dynamic
        }

        self.index += 1

        # Simulate real-time tick if requested
        if simulate_realtime:
            sleep(sleep_seconds)

        return tick


# Example usage
if __name__ == "__main__":
    # Load candlestick CSV generated from final_candle_generator.py
    df = pd.read_csv("candlestick_data.csv")

    # Initialize the MarketDataBridge with DataFrame
    bridge = MarketDataBridge(df)

    # Generate and print ticks until the end
    while True:
        tick = bridge.get_next_tick(simulate_realtime=True, sleep_seconds=0.5)
        if tick is None:
            break
        print(tick)