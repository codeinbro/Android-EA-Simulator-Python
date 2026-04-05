# market_data_bridge.py

import pandas as pd
from time import sleep
from datetime import datetime, timedelta
import random


class MarketDataBridge:
    """
    Advanced MarketDataBridge (MT5-LIKE SIMULATOR)

    FEATURES:
    ---------
    - Simulates broker tick stream (BID/ASK)
    - Provides OHLC data (copy_rates)
    - Provides tick history (copy_ticks)
    - Supports streaming (like OnTick)
    - Includes symbol, account, broker info
    - Internal caching for performance

    DESIGN:
    -------
    Built to mimic MetaTrader 5 Python API so EA can be portable.
    """

    def __init__(self,
                 csv_file="candlestick_data.csv",
                 symbol="EURUSD",
                 timeframe_minutes=15,
                 ticks_per_candle=20,
                 default_spread=0.0001,
                 default_volume=100):

        # =========================
        # LOAD DATA (ONLY CSV HERE)
        # =========================
        self.candles = pd.read_csv(csv_file).reset_index(drop=True)

        # =========================
        # CONFIGURATION
        # =========================
        self.symbol = symbol
        self.timeframe_minutes = timeframe_minutes
        self.ticks_per_candle = ticks_per_candle
        self.default_spread = default_spread
        self.default_volume = default_volume

        # =========================
        # INTERNAL STATE
        # =========================
        self._ticks_cache = None
        self._current_tick_index = 0

        # =========================
        # SYMBOL INFO
        # =========================
        self._symbol_info = {
            "SYMBOL": symbol,
            "POINT": 0.01,
            "DIGITS": 2,
            "CONTRACT_SIZE": 100000,
            "TICK_VALUE": 10,
            "MARGIN_REQ": 1000,
            "SWAP_LONG": -0.5,
            "SWAP_SHORT": -0.3,
            "COMMISSION": 2
        }

        # =========================
        # ACCOUNT INFO
        # =========================
        self._account_info = {
            "ACCOUNT_NUMBER": 123456,
            "USER_ID": "EA_TEST_USER",
            "BALANCE": 10000,
            "EQUITY": 10000,
            "FREE_MARGIN": 10000,
            "LEVERAGE": 100,
            "CURRENCY": "USD"
        }

        # =========================
        # TERMINAL / BROKER INFO
        # =========================
        self._terminal_info = {
            "BROKER_NAME": "MyBroker",
            "SERVER_NAME": "DemoServer01"
        }

        # =========================
        # TIME HANDLING
        # =========================
        if "DATETIME" not in self.candles.columns:
            self.start_time = datetime.now().replace(second=0, microsecond=0)
        else:
            self.start_time = None

    # =========================================================
    # 🔥 CORE ENGINE (GENERATE TICKS ONCE)
    # =========================================================
    def _generate_ticks(self):

        if self._ticks_cache is not None:
            return self._ticks_cache

        ticks = []

        for idx, row in self.candles.iterrows():

            open_price = float(row.get("OPEN", 0))
            close = float(row.get("CLOSE", open_price))
            high = float(row.get("HIGH", max(open_price, close)))
            low = float(row.get("LOW", min(open_price, close)))

            base_spread = float(row.get("SPREAD", self.default_spread))
            volume = int(row.get("VOLUME", self.default_volume))

            # --- Handle time safely ---
            try:
                if self.start_time:
                    candle_time = self.start_time + timedelta(minutes=idx * self.timeframe_minutes)
                else:
                    candle_time = datetime.strptime(str(row["DATETIME"]), "%Y-%m-%d %H:%M:%S")
            except:
                candle_time = datetime.now()

            # --- Generate ticks ---
            for t in range(self.ticks_per_candle):

                progress = t / self.ticks_per_candle
                base_price = open_price + (close - open_price) * progress

                noise = random.uniform(-0.3, 0.3)
                price = max(min(base_price + noise, high), low)

                spread = base_spread * random.uniform(0.8, 1.5)

                bid = price - spread / 2
                ask = price + spread / 2

                tick_time = candle_time + timedelta(
                    seconds=int((t / self.ticks_per_candle) * self.timeframe_minutes * 60)
                )

                ticks.append({
                    "time": tick_time,
                    "bid": round(bid, 5),
                    "ask": round(ask, 5),
                    "last": round(price, 5),
                    "volume": random.randint(1, volume),

                    # reference OHLC
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "close": close,
                })

        self._ticks_cache = ticks
        return ticks

    # =========================================================
    # 🔥 MT5 STYLE FUNCTIONS
    # =========================================================

    def symbol_info_tick(self):
        """Return current tick"""
        return self._generate_ticks()[self._current_tick_index]

    def next_tick(self):
        """Move to next tick (OnTick simulation)"""
        ticks = self._generate_ticks()

        if self._current_tick_index < len(ticks) - 1:
            self._current_tick_index += 1

        return ticks[self._current_tick_index]

    def copy_rates(self, count=100):
        """Return last N candles"""
        df = self.candles.tail(count)

        rates = []

        for idx, row in df.iterrows():
            rates.append({
                "time": row.get("DATETIME"),
                "open": float(row.get("OPEN", 0)),
                "high": float(row.get("HIGH", 0)),
                "low": float(row.get("LOW", 0)),
                "close": float(row.get("CLOSE", 0)),
                "tick_volume": int(row.get("VOLUME", self.default_volume)),
                "spread": float(row.get("SPREAD", self.default_spread))
            })

        return rates

    def copy_ticks(self, count=100):
        """Return last N ticks"""
        ticks = self._generate_ticks()
        return ticks[-count:]

    def symbol_info(self):
        return self._symbol_info

    def account_info(self):
        return self._account_info

    def terminal_info(self):
        return self._terminal_info

    # =========================================================
    # 🔥 CONTROL FUNCTIONS
    # =========================================================

    def reset(self):
        """Reset tick pointer (restart simulation)"""
        self._current_tick_index = 0

    def is_end(self):
        """Check if tick stream finished"""
        return self._current_tick_index >= len(self._generate_ticks()) - 1

    # =========================================================
    # 🔥 STREAMING (LIKE REAL MARKET)
    # =========================================================

    def stream_ticks(self, sleep_seconds=0.1):
        """Generator for live-like streaming"""

        ticks = self._generate_ticks()

        for t in ticks:
            yield t
            sleep(sleep_seconds)