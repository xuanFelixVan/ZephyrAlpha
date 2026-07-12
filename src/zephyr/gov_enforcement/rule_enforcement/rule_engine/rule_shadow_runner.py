# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_shadow_runner
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 影子模式统计必须准确;假阳性率必须<10%
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_rule_shadow_runner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Rule Shadow Runner — v0.10.0 规则影子模式: 新规则shadow运行3天->diff old vs new->promote。
"""

from __future__ import annotations

import time


class RuleShadowRunner:
    def __init__(self):
        self._shadow_rules: dict[str, dict] = {}

    def deploy_shadow(self, rule_id: str, rule_def: dict, shadow_days: int = 3):
        self._shadow_rules[rule_id] = {
            "rule": rule_def,
            "deployed_at": time.time(),
            "shadow_days": shadow_days,
            "decisions": [],
        }

    def record_shadow_decision(self, rule_id: str, operation: str, old_level: str, new_level: str):
        if rule_id in self._shadow_rules:
            self._shadow_rules[rule_id]["decisions"].append({"op": operation, "old": old_level, "new": new_level})

    def diff(self, rule_id: str) -> dict:
        shadow = self._shadow_rules.get(rule_id)
        if not shadow:
            return {}
        changes = [d for d in shadow["decisions"] if d["old"] != d["new"]]
        return {"rule_id": rule_id, "total": len(shadow["decisions"]), "changes": len(changes)}

    def promote(self, rule_id: str) -> bool:
        return rule_id in self._shadow_rules
