"""Protocol Self Context — v0.10.0 协议自维护上下文管理器。"""
from __future__ import annotations

class ProtocolSelfContext:
    def __init__(self):
        self._context:dict={"version":"v0.10.0","active_rules":0,"last_reconcile":None}

    def update_metrics(self, active_rules:int):
        self._context["active_rules"]=active_rules

    def snapshot(self)->dict:
        return dict(self._context)
