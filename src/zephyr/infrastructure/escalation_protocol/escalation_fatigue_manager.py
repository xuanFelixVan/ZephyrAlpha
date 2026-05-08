"""Escalation Fatigue Manager — v0.11.0 升级疲劳管理器。"""
from __future__ import annotations
import time

class EscalationFatigueManager:
    def __init__(self):
        self._owner_escalations:dict[str,list[float]]={}
        self._cooldown_h=4
        self._max_daily=6

    def record_escalation(self, owner_id:str)->bool:
        now=time.time()
        recent=[t for t in self._owner_escalations.get(owner_id,[]) if now-t<86400]
        if len(recent)>=self._max_daily:
            return False
        last=[t for t in self._owner_escalations.get(owner_id,[]) if now-t<self._cooldown_h*3600]
        if last:
            return False
        self._owner_escalations.setdefault(owner_id,[]).append(now)
        return True
