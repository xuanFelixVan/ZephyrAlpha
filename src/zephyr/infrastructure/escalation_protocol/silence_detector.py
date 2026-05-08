"""Silence Detector — v0.8.0 静默窗口检测器: agent无响应超时+heartbeat缺失检测。"""
from __future__ import annotations
import time

class SilenceDetector:
    def __init__(self):
        self._last_activity:dict[str,float]={}
        self._timeout_s=1800

    def record_activity(self, agent_id:str):
        self._last_activity[agent_id]=time.time()

    def detect_silence(self)->list[str]:
        now=time.time()
        return [aid for aid,last in self._last_activity.items() if now-last>self._timeout_s]

    def is_silent(self, agent_id:str)->bool:
        last=self._last_activity.get(agent_id,0)
        return time.time()-last>self._timeout_s
