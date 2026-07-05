# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.rule_engine.rule_canary_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 金丝雀范围必须限制;自动回滚必须可用
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_rule_canary_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Rule Canary Manager — v0.10.0 规则金丝雀: 1%用户先上新规则→A/B对比→rollback。
"""

from __future__ import annotations


class RuleCanaryManager:
    def __init__(self):
        self._canary_weight = 0.01
        self._baseline_metrics: dict = {}
        self._canary_metrics: dict = {}

    def set_baseline(self, metrics: dict):
        self._baseline_metrics = metrics

    def set_canary_metrics(self, metrics: dict):
        self._canary_metrics = metrics

    def should_rollback(self) -> bool:
        baseline_err = self._baseline_metrics.get("false_positive_rate", 0)
        canary_err = self._canary_metrics.get("false_positive_rate", 0)
        return canary_err > baseline_err * 2.0

    def promote(self) -> None:
        self._canary_weight = 1.0
