# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.escalation_metrics
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 指标收集不可遗漏;假阳性率必须跟踪
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Escalation Metrics — D-022-07 指标收集器: 升级率/误升级率/响应延迟。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: escalation_metrics.py
# 层: 算法
# - id: A1
#   name_zh: ① EscalationMetrics
#   name_en: EscalationMetrics
#   intro: class EscalationMetrics 源码 L51-L115
#   desc: 公共方法（定义序）: blocks, total_evals, auto_guards, autonomous, false_positives, latencies, record, escalation_rate,…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: EscalationMetrics
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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

    # --- Public properties (Reverse Hierarchy) ---

    @property
    def blocks(self):
        """Block events list (public API)."""
        return self._blocks

    @property
    def total_evals(self) -> int:
        """Total evaluation count (public API)."""
        return self._total_evals

    @total_evals.setter
    def total_evals(self, value: int) -> None:
        self._total_evals = value

    @property
    def auto_guards(self):
        """Auto guard events list (public API)."""
        return self._auto_guards

    @property
    def autonomous(self):
        """Autonomous events list (public API)."""
        return self._autonomous

    @property
    def false_positives(self):
        """False positive events list (public API)."""
        return self._false_positives

    @property
    def latencies(self):
        """Latency records list (public API)."""
        return self._latencies

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
