"""Error Budget Burst Limiter — v0.11.0 错误预算Burst限流器。"""
from __future__ import annotations
import time

class BurstLimiter:
    def __init__(self):
        self._burst_window_s=60
        self._max_burst=10
        self._requests:list[float]=[]

    def allow(self)->bool:
        now=time.time()
        self._requests=[t for t in self._requests if now-t<self._burst_window_s]
        if len(self._requests)>=self._max_burst:
            return False
        self._requests.append(now)
        return True
