# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.rule_canary_manager

# [INVARIANTS] 金丝雀范围必须限制;自动回滚必须可用

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Rule Canary Manager — v0.10.0 规则金丝雀: 1%用户先上新规则→A/B对比→rollback。
"""
from __future__ import annotations

class RuleCanaryManager:
    def __init__(self):
        self._canary_weight=0.01
        self._baseline_metrics:dict={}
        self._canary_metrics:dict={}

    def set_baseline(self, metrics:dict):
        self._baseline_metrics=metrics

    def set_canary_metrics(self, metrics:dict):
        self._canary_metrics=metrics

    def should_rollback(self)->bool:
        baseline_err=self._baseline_metrics.get("false_positive_rate",0)
        canary_err=self._canary_metrics.get("false_positive_rate",0)
        return canary_err>baseline_err*2.0

    def promote(self)->None:
        self._canary_weight=1.0
