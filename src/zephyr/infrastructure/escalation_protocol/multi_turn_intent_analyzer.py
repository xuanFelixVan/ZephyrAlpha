"""Multi-Turn Intent Analyzer — v0.13.0 多轮分布式意图分析器。"""
from __future__ import annotations

class MultiTurnIntentAnalyzer:
    def __init__(self):
        self._turn_history:list[dict] = []

    def record_turn(self, turn:dict):
        self._turn_history.append(turn)

    def accumulated_intent(self, window_turns:int=5)->str:
        recent=self._turn_history[-window_turns:]
        intents=[t.get("intent","") for t in recent]
        if any(p in " ".join(intents).lower() for p in ["override","bypass","sudo","force"]):
            return "suspicious"
        return "normal"

    def should_escalate(self)->bool:
        return self.accumulated_intent()=="suspicious"
