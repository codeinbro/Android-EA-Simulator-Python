# market_data_bridge.py

import pandas as pd
from time import sleep
from datetime import datetime, timedelta
import random


class MarketDataBridge:

    def __init__(self,
                 csv_file="candlestick_data.csv",
                 symbol="EURUSD",
                 timeframe_minutes=15,
                 ticks_per_candle=20,
                 default_spread=0.0001,
                 default_volume=100):

        # =========================
        # LOAD CSV (ONLY HERE)
        # =========================
        self.candles = pd.read_csv(csv_file).reset_index(drop=True)

        # =========================
        # CONFIG
        # =========================
        self.symbol = symbol
        self.timeframe_minutes = timeframe_minutes
        self.ticks_per_candle = ticks_per_candle
        self.default_spread = default_spread
        self.default_volume = default_volume

        # =========================
        # CACHE
        # =========================
        self._ticks_cache = None
        self._current_tick_index = 0

        # =========================
        # SYMBOL INFO
        # =========================
        self._symbol_info = {
            "name": symbol,
            "point": 0.01,
            "digits": 2,
            "trade_contract_size": 100000
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

    # =========================================================
    # 🔥 CORE ENGINE
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

            # --- TIME SAFE ---
            try:
                candle_time = datetime.strptime(
                    str(row.get("DATETIME")),
                    "%Y-%m-%d %H:%M:%S"
                )
            except:
                candle_time = datetime.now()

            # --- GENERATE TICKS ---
            for t in range(self.ticks_per_candle):

                progress = t / self.ticks_per_candle
                base_price = open_price + (close - open_price) * progress

                noise = random.uniform(-0.3, 0.3)
                price = max(min(base_price + noise, high), low)

                spread = base_spread * random.uniform(0.8, 1.5)

                bid = price - spread / 2
                ask = price + spread / 2

                tick_time = candle_time + timedelta(
                    seconds=int(progress * self.timeframe_minutes * 60)
                )

                # 🔥 MT5 FORMAT
                ticks.append({
                    "time": int(tick_time.timestamp()),
                    "time_msc": int(tick_time.timestamp() * 1000),

                    "bid": round(bid, 5),
                    "ask": round(ask, 5),
                    "last": round(price, 5),

                    "volume": random.randint(1, volume),
                    "flags": 2  # simple simulation

                })

        self._ticks_cache = ticks
        return ticks

    # =========================================================
    # 🔥 MT5 API STYLE
    # =========================================================

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

        for _, row in df.iterrows():

            try:
                t = int(datetime.strptime(
                    str(row.get("DATETIME")),
                    "%Y-%m-%d %H:%M:%S"
                ).timestamp())
            except:
                t = int(datetime.now().timestamp())

            rates.append({
                "time": t,
                "open": float(row.get("OPEN", 0)),
                "high": float(row.get("HIGH", 0)),
                "low": float(row.get("LOW", 0)),
                "close": float(row.get("CLOSE", 0)),
                "tick_volume": int(row.get("VOLUME", self.default_volume)),
                "spread": int(float(row.get("SPREAD", self.default_spread)) * 10000),
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

    # =========================================================
    # CONTROL
    # =========================================================

    def reset(self):
        self._current_tick_index = 0

    def is_end(self):
        return self._current_tick_index >= len(self._generate_ticks()) - 1

    # =========================================================
    # STREAM
    # =========================================================

    def stream_ticks(self, sleep_seconds=0.1):
        for t in self._generate_ticks():
            yield t
            sleep(sleep_seconds)