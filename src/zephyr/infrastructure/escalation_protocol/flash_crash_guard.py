"""Flash Crash Guard — v0.12.0 闪崩双轨熔断器。"""
from __future__ import annotations
import time

class FlashCrashGuard:
    LIQUIDITY_THRESHOLD=50.0
    VELOCITY_THRESHOLD=60.0

    def __init__(self):
        self._tripped=False
        self._trip_time=0.0

    def evaluate(self, price_drop_pct:float, velocity_pct_per_s:float, bid_ask_spread_pct:float)->bool:
        if price_drop_pct>self.LIQUIDITY_THRESHOLD or velocity_pct_per_s>self.VELOCITY_THRESHOLD:
            self._tripped=True
            self._trip_time=time.time()
            return True
        return False

    @property
    def tripped(self)->bool:
        return self._tripped

    def reset(self):
        self._tripped=False
