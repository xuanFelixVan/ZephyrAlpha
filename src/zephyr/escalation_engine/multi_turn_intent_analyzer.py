# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.multi_turn_intent_analyzer

# [INVARIANTS] 多轮语义分析不可跳过;10轮链+per_tool budget不可修改

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Multi-Turn Intent Analyzer — v0.13.0 多轮分布式意图分析器。
"""
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
