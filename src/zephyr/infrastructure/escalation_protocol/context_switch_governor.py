"""Context Switch Governor — v0.11.0 Owner上下文切换预算管理器。"""
from __future__ import annotations

class ContextSwitchGovernor:
    def __init__(self):
        self._daily_switches:dict[str,int]={}
        self._max_switches_per_owner=12

    def can_switch(self, owner_id:str)->bool:
        current=self._daily_switches.get(owner_id,0)
        return current<self._max_switches_per_owner

    def record_switch(self, owner_id:str):
        self._daily_switches[owner_id]=self._daily_switches.get(owner_id,0)+1
