# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.bandwidth_optimizer
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-020;MOD-INF-018;MOD-INF-027
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Token/Cost/Time三维预算;超预算拒绝
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md;src/zephyr/budget-enforcer/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BudgetExceededError;CostLimitError
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-RES_bandwidth_optimizer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BandwidthDimension(str, Enum):
    INTERRUPT_OVERHEAD = "interrupt_overhead"
    CONTEXT_SWITCHING = "context_switching"
    DECISION_FATIGUE = "decision_fatigue"
    COMMUNICATION_LATENCY = "communication_latency"
    ATTENTION_SPAN = "attention_span"
    COGNITIVE_LOAD = "cognitive_load"


@dataclass
class BandwidthScore:
    interrupt_overhead: float = 0.0
    context_switching: float = 0.0
    decision_fatigue: float = 0.0
    communication_latency: float = 0.0
    attention_span: float = 0.0
    cognitive_load: float = 0.0

    @property
    def composite(self) -> float:
        weights = {
            "interrupt_overhead": 0.20,
            "context_switching": 0.20,
            "decision_fatigue": 0.20,
            "communication_latency": 0.15,
            "attention_span": 0.10,
            "cognitive_load": 0.15,
        }
        total = (
            self.interrupt_overhead * weights["interrupt_overhead"]
            + self.context_switching * weights["context_switching"]
            + self.decision_fatigue * weights["decision_fatigue"]
            + self.communication_latency * weights["communication_latency"]
            + self.attention_span * weights["attention_span"]
            + self.cognitive_load * weights["cognitive_load"]
        )
        return round(total, 3)

    def normalize(self) -> None:
        """每维度 self-normalize 到 [0,1] 范围。"""
        caps = {
            "interrupt_overhead": 10.0,
            "context_switching": 10.0,
            "decision_fatigue": 10.0,
            "communication_latency": 10.0,
            "attention_span": 10.0,
            "cognitive_load": 10.0,
        }
        self.interrupt_overhead = min(1.0, self.interrupt_overhead / caps["interrupt_overhead"])
        self.context_switching = min(1.0, self.context_switching / caps["context_switching"])
        self.decision_fatigue = min(1.0, self.decision_fatigue / caps["decision_fatigue"])
        self.communication_latency = min(1.0, self.communication_latency / caps["communication_latency"])
        self.attention_span = min(1.0, max(0.0, self.attention_span / caps["attention_span"]))
        self.cognitive_load = min(1.0, self.cognitive_load / caps["cognitive_load"])


@dataclass
class OptimizationRecommendation:
    task_granularity: str = "medium"
    focus_shift_interval_seconds: int = 1800
    max_tasks_per_session: int = 30
    suggested_break_seconds: int = 300


def recommend(score: BandwidthScore) -> OptimizationRecommendation:
    score.normalize()
    c = score.composite

    if c > 0.7:
        return OptimizationRecommendation(
            task_granularity="small",
            focus_shift_interval_seconds=600,
            max_tasks_per_session=10,
            suggested_break_seconds=600,
        )
    if c > 0.4:
        return OptimizationRecommendation(
            task_granularity="medium",
            focus_shift_interval_seconds=1800,
            max_tasks_per_session=30,
            suggested_break_seconds=300,
        )
    return OptimizationRecommendation(
        task_granularity="large",
        focus_shift_interval_seconds=3600,
        max_tasks_per_session=65,
        suggested_break_seconds=120,
    )
