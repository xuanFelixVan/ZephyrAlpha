"""Vigil Runtime — v0.6.0 VIGIL维护运行时: 运维token预算+手动override窗口。"""
from __future__ import annotations
import time

class VigilRuntime:
    def __init__(self):
        self._token_budget=2000
        self._tokens_used=0
        self._override_window_open=False
        self._override_expiry=0.0

    def consume(self, tokens:int)->bool:
        if self._tokens_used+tokens>self._token_budget:
            return False
        self._tokens_used+=tokens
        return True

    def open_override_window(self, duration_s:float=600):
        self._override_window_open=True
        self._override_expiry=time.time()+duration_s

    @property
    def override_active(self)->bool:
        return self._override_window_open and time.time()<self._override_expiry

    def remaining_tokens(self)->int:
        return max(0,self._token_budget-self._tokens_used)
