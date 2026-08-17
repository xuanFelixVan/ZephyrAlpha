# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.context_governance.multi_turn_intent_analyzer
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 多轮语义分析不可跳过;10轮链+per_tool budget不可修改
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Multi-Turn Intent Analyzer — v0.13.0 多轮分布式意图分析器。
"""

from __future__ import annotations


class MultiTurnIntentAnalyzer:
    def __init__(self):
        self._turn_history: list[dict] = []

    # ── Stage 4 公共化（2026-07-28）：只读 property ──
    @property
    def turn_history(self) -> list[dict]:
        """只读：turn_history（Stage 4 公共化）。"""
        return self._turn_history

    @turn_history.setter
    def turn_history(self, value):
        """写入：turn_history（Stage 4 公共化）。"""
        self._turn_history = value

    def record_turn(self, turn: dict):
        self._turn_history.append(turn)

    def accumulated_intent(self, window_turns: int = 5) -> str:
        recent = self._turn_history[-window_turns:]
        intents = [t.get("intent", "") for t in recent]
        if any(p in " ".join(intents).lower() for p in ["override", "bypass", "sudo", "force"]):
            return "suspicious"
        return "normal"

    def should_escalate(self) -> bool:
        return self.accumulated_intent() == "suspicious"
