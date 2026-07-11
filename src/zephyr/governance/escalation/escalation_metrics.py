# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.escalation_metrics
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 指标收集不可遗漏;假阳性率必须跟踪
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_escalation_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Escalation Metrics — D-022-07 指标收集器: 升级率/误升级率/响应延迟。
"""

from __future__ import annotations


class EscalationMetrics:
    def __init__(self):
        self._total_evals = 0
        self._blocks = 0
        self._auto_guards = 0
        self._autonomous = 0
        self._false_positives = 0
        self._latencies: list[float] = []

    def record(self, level: str, latency_s: float, was_false_positive: bool = False):
        self._total_evals += 1
        if level == "blocked":
            self._blocks += 1
        elif level == "auto_guard":
            self._auto_guards += 1
        else:
            self._autonomous += 1
        self._latencies.append(latency_s)
        if was_false_positive:
            self._false_positives += 1

    def escalation_rate(self) -> float:
        return self._blocks / max(1, self._total_evals)

    def avg_latency(self) -> float:
        return sum(self._latencies) / max(1, len(self._latencies))

    def false_positive_rate(self) -> float:
        return self._false_positives / max(1, self._blocks)
