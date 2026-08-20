# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.witness_isolation
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Witness隔离不可突破;独立namespace必须强制
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Witness Isolation — v0.8.0 Witness隔离: N版本decision验证+投票机制+majority判定。
"""

from __future__ import annotations


class WitnessIsolator:
    def __init__(self):
        self._witnesses: dict[str, str] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def witnesses(self) -> dict[str, str]:
        """只读：witnesses（Stage 4 公共化）。"""
        return self._witnesses

    @witnesses.setter
    def witnesses(self, value):
        """写入：witnesses（Stage 4 公共化）。"""
        self._witnesses = value

    def register_witness(self, witness_id: str, decision: str):
        self._witnesses[witness_id] = decision

    def majority_decision(self) -> str:
        if not self._witnesses:
            return "no_decision"
        from collections import Counter

        counts = Counter(self._witnesses.values())
        total = len(self._witnesses)
        for decision, count in counts.most_common(1):
            if count > total / 2:
                return decision
        return "no_consensus"

    def disagree_count(self) -> int:
        from collections import Counter

        if not self._witnesses:
            raise ValueError("no witnesses registered")
        counts = Counter(self._witnesses.values())
        return len(self._witnesses) - max(counts.values())
