"""Clock Guard — v0.8.0 时钟完整性防御: NTP漂移检测+wall clock monotonic验证。"""
from __future__ import annotations
import time

class ClockGuard:
    def __init__(self):
        self._monotonic_start=time.monotonic()
        self._wall_start=time.time()

    def detect_drift(self)->float:
        mono_elapsed=time.monotonic()-self._monotonic_start
        wall_elapsed=time.time()-self._wall_start
        return abs(wall_elapsed-mono_elapsed)

    def is_suspicious(self)->bool:
        return self.detect_drift()>5.0

    def validate_timestamp(self, ts:float, tolerance_s:float=60)->bool:
        return abs(time.time()-ts)<tolerance_s
