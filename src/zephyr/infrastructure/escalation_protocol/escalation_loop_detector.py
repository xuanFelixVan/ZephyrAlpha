"""Escalation Loop Detector — v0.10.0 跨模块升级循环: escalate→block→auto_guard→escalate循环检测。"""
from __future__ import annotations
import time

class EscalationLoopDetector:
    def __init__(self):
        self._history:list[tuple[str,str,float]]=[]

    def record_transition(self, task_id:str, from_level:str, to_level:str):
        self._history.append((task_id,from_level,time.time()))
        self._history.append((task_id,to_level,time.time()))

    def detect_loop(self, window_s:float=300)->bool:
        recent=[(tid,lvl) for tid,lvl,t in self._history if time.time()-t<window_s]
        for tid in set(t[0] for t in recent):
            count=sum(1 for t in recent if t[0]==tid)
            if count>=6:return True
        return False
