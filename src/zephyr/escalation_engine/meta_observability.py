# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.meta_observability

# [INVARIANTS] 自健康检查不可跳过;dead-man-switch必须触发

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Meta Observability — v0.10.0 协议自身可观测性: self loop latency+p99+edge case rate。
"""
from __future__ import annotations
import time

class MetaObservability:
    def __init__(self):
        self._self_latencies:list[float]=[]
        self._edge_cases=0

    def record_self_latency(self, seconds:float):
        self._self_latencies.append(seconds)

    def p99_self_latency(self)->float:
        if not self._self_latencies:return 0.0
        sorted_l=sorted(self._self_latencies)
        idx=int(len(sorted_l)*0.99)
        return sorted_l[max(0,idx)]

    def register_edge_case(self):
        self._edge_cases+=1

    def edge_case_rate(self,total:int)->float:
        return self._edge_cases/max(1,total)
