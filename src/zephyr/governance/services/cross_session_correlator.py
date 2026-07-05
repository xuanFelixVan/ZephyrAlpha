# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.services.cross_session_correlator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 跨会话关联必须执行;异常必须触发告警
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_cross_session_correlator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Cross-Session Correlator — v0.9.0 跨会话Coreset关联器: 多session行为模式+异常跨session模式检测。
"""

from __future__ import annotations


class CrossSessionCorrelator:
    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def register_session(self, session_id: str, metrics: dict):
        self._sessions[session_id] = metrics

    def detect_anomalous_session(self, metrics: dict, std_dev_threshold: float = 2.0) -> bool:
        if len(self._sessions) < 3:
            return False
        means = {k: sum(s[k] for s in self._sessions.values()) / len(self._sessions) for k in metrics}
        for k, v in metrics.items():
            mean = means.get(k, 0)
            if mean > 0 and abs(v - mean) / mean > std_dev_threshold:
                return True
        return False
