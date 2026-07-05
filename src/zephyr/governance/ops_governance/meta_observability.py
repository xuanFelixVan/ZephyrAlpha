# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.meta_observability
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 自健康检查不可跳过;dead-man-switch必须触发
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_meta_observability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Meta Observability — v0.10.0 协议自身可观测性: self loop latency+p99+edge case rate。
"""

from __future__ import annotations


class MetaObservability:
    def __init__(self):
        self._self_latencies: list[float] = []
        self._edge_cases = 0

    def record_self_latency(self, seconds: float):
        self._self_latencies.append(seconds)

    def p99_self_latency(self) -> float:
        if not self._self_latencies:
            return 0.0
        sorted_l = sorted(self._self_latencies)
        idx = int(len(sorted_l) * 0.99)
        return sorted_l[max(0, idx)]

    def register_edge_case(self):
        self._edge_cases += 1

    def edge_case_rate(self, total: int) -> float:
        return self._edge_cases / max(1, total)
