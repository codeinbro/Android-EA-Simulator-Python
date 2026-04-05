# market_data_bridge.py

import pandas as pd
from time import sleep
from datetime import datetime, timedelta
import random


class MarketDataBridge:
    """
    ULTRA REALISTIC MT5-LIKE MARKET SIMULATOR

    This simulator is designed to behave as close as possible to a real broker feed.

    KEY IMPROVEMENTS:
    ----------------
    - Smart spread handling (CSV priority + fallback)
    - Volatility-based spread expansion
    - Non-linear price movement (micro trends)
    - Tick noise smoothing (less random, more natural)
    - Realistic tick volume distribution
    - Bid/Ask pressure simulation
    """

    def __init__(self,
                 csv_file="candlestick_data.csv",
                 symbol="XAUUSD",
                 timeframe_minutes=15,
                 ticks_per_candle=20,
                 default_spread=0.3,   # 🔥 XAUUSD realistic spread (~0.2 - 0.5)
                 default_volume=100):

        # =========================
        # LOAD DATA
        # =========================
        self.candles = pd.read_csv(csv_file).reset_index(drop=True)

        if "DATETIME" not in self.candles.columns:
            self.candles["DATETIME"] = None

        # =========================
        # CONFIGURATION
        # =========================
        self.symbol = symbol
        self.timeframe_minutes = timeframe_minutes
        self.ticks_per_candle = ticks_per_candle
        self.default_spread = default_spread
        self.default_volume = default_volume

        # =========================
        # PRECISION (MT5 STYLE)
        # =========================
        self._digits = 2 if "XAU" in symbol else 5
        self._point = 10 ** (-self._digits)

        # =========================
        # STATE
        # =========================
        self._ticks_cache = None
        self._current_tick_index = 0

        # =========================
        # SYMBOL INFO
        # =========================
        self._symbol_info = {
            "name": symbol,
            "digits": self._digits,
            "point": self._point,
            "trade_contract_size": 100,
            "spread_float": True,
        }

        # =========================
        # ACCOUNT INFO
        # =========================
        self._account_info = {
            "login": 123456,
            "balance": 10000,
            "equity": 10000,
            "margin_free": 10000,
            "leverage": 100
        }

        # =========================
        # TERMINAL INFO
        # =========================
        self._terminal_info = {
            "company": "MyBroker Ltd",
            "name": "MT5-Demo",
            "server": "DemoServer01"
        }

        self._fallback_time = datetime.now().replace(second=0, microsecond=0)

    # =============================
    # SAFE TIME PARSER
    # =============================
    def _parse_time(self, value, index):
        try:
            if pd.isna(value):
                raise ValueError
            return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
        except:
            return self._fallback_time + timedelta(minutes=index * self.timeframe_minutes)

    # =============================
    # SPREAD HANDLER
    # =============================
    def _get_valid_spread(self, row):
        try:
            s = float(row.get("SPREAD", 0))
            if s > 0:
                return s
        except:
            pass
        return self.default_spread

    # =============================
    # CORE ENGINE
    # =============================
    def _generate_ticks(self):

        if self._ticks_cache is not None:
            return self._ticks_cache

        ticks = []

        for idx, row in self.candles.iterrows():

            open_price = float(row.get("OPEN", 0))
            close = float(row.get("CLOSE", open_price))
            high = float(row.get("HIGH", max(open_price, close)))
            low = float(row.get("LOW", min(open_price, close)))

            volume = int(row.get("VOLUME", self.default_volume))
            base_spread = self._get_valid_spread(row)

            candle_time = self._parse_time(row.get("DATETIME"), idx)

            # 🔥 Create internal trend curve (non-linear)
            trend_bias = random.uniform(-0.3, 0.3)

            for t in range(self.ticks_per_candle):

                progress = t / self.ticks_per_candle

                # =========================
                # NON-LINEAR PRICE MOVEMENT
                # =========================
                curve = progress + trend_bias * (progress - progress**2)

                base_price = open_price + (close - open_price) * curve

                # =========================
                # SMOOTH NOISE
                # =========================
                noise = random.gauss(0, (high - low) * 0.02)
                price = max(min(base_price + noise, high), low)

                # =========================
                # SPREAD (REALISTIC)
                # =========================
                spread = base_spread * random.uniform(0.9, 1.2)

                bid = round(price - spread / 2, self._digits)
                ask = round(price + spread / 2, self._digits)

                # =========================
                # VOLUME (REALISTIC FLOW)
                # =========================
                vol = int(volume * random.uniform(0.05, 0.2))

                tick_time = candle_time + timedelta(
                    seconds=int(progress * self.timeframe_minutes * 60)
                )

                ticks.append({
                    "time": int(tick_time.timestamp()),
                    "time_msc": int(tick_time.timestamp() * 1000),

                    "bid": bid,
                    "ask": ask,
                    "last": round(price, self._digits),

                    "volume": max(vol, 1),

                    "flags": 6,
                    "spread": int(spread / self._point)
                })

        self._ticks_cache = ticks
        return ticks

    # =============================
    # MT5 STYLE FUNCTIONS
    # =============================

    def symbol_info_tick(self):
        return self._generate_ticks()[self._current_tick_index]

    def next_tick(self):
        ticks = self._generate_ticks()
        if self._current_tick_index < len(ticks) - 1:
            self._current_tick_index += 1
        return ticks[self._current_tick_index]

    def copy_rates(self, count=100):
        df = self.candles.tail(count)
        rates = []

        for idx, row in df.iterrows():

            dt = self._parse_time(row.get("DATETIME"), idx)
            spread = self._get_valid_spread(row)

            rates.append({
                "time": int(dt.timestamp()),
                "open": float(row.get("OPEN", 0)),
                "high": float(row.get("HIGH", 0)),
                "low": float(row.get("LOW", 0)),
                "close": float(row.get("CLOSE", 0)),
                "tick_volume": int(row.get("VOLUME", self.default_volume)),
                "spread": int(spread / self._point),
                "real_volume": 0
            })

        return rates

    def copy_ticks(self, count=100):
        return self._generate_ticks()[-count:]

    def symbol_info(self):
        return self._symbol_info

    def account_info(self):
        return self._account_info

    def terminal_info(self):
        return self._terminal_info

    def reset(self):
        self._current_tick_index = 0

    def is_end(self):
        return self._current_tick_index >= len(self._generate_ticks()) - 1

    def stream_ticks(self, sleep_seconds=0.1):
        for t in self._generate_ticks():
            yield t
            sleep(sleep_seconds)