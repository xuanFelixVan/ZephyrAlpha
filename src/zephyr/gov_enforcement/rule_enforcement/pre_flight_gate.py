# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.pre_flight_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.ops_governance.budget_models; zephyr.governance.ops_governance.budget_engine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_pre_flight_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import time
from dataclasses import dataclass, field
from enum import Enum, auto

from zephyr.governance.ops_governance.budget_engine import BudgetEngine
from zephyr.governance.ops_governance.budget_models import GateDecision


class PreFlightDecision(Enum):
    ALLOW = auto()
    SOFT_WARN = auto()
    HARD_WARN = auto()
    BLOCK = auto()


@dataclass
class PreFlightReport:
    decision: PreFlightDecision
    token_check: GateDecision
    cost_check: GateDecision
    time_check: GateDecision
    recommendations: list[str] = field(default_factory=list)
    checked_at: float = field(default_factory=time.time)

    @property
    def all_green(self) -> bool:
        return self.decision is PreFlightDecision.ALLOW


class PreFlightGate:
    def __init__(self, engine: BudgetEngine | None = None):
        self._engine = engine or BudgetEngine()

    def gate(
        self,
        action: str,
        estimated_tokens: int,
        estimated_cost: float,
        session_id: str = "",
    ) -> PreFlightReport:
        tok = self._engine.pre_flight_check(f"{action}-token", estimated_tokens, estimated_cost + 0.01)
        cst = self._engine.pre_flight_check(f"{action}-cost", estimated_tokens + 100, estimated_cost)
        tim = self._engine.pre_flight_check(f"{action}-time", estimated_tokens, estimated_cost + 0.02)

        recs: list[str] = []
        severity = 0

        for check, name in [(tok, "Token"), (cst, "Cost"), (tim, "Time")]:
            if check.decision is GateDecision.DENY:
                severity = max(severity, 3)
                recs.append(f"{name}: 预算已耗尽，建议降级或拆分任务")
            elif check.decision is GateDecision.DEGRADE:
                severity = max(severity, 2)
                recs.append(f"{name}: 接近上限，建议使用免费模型")
            elif check.decision is GateDecision.NARROW:
                severity = max(severity, 1)
                recs.append(f"{name}: 预算消耗过半，注意控制")

        decision_map = {
            0: PreFlightDecision.ALLOW,
            1: PreFlightDecision.SOFT_WARN,
            2: PreFlightDecision.HARD_WARN,
            3: PreFlightDecision.BLOCK,
        }
        return PreFlightReport(
            decision=decision_map[severity],
            token_check=tok.decision,
            cost_check=cst.decision,
            time_check=tim.decision,
            recommendations=recs,
        )

    def get_engine(self) -> BudgetEngine:
        return self._engine
