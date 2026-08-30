# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.pre_flight_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.ops_governance.budget_models; zephyr.governance.ops_governance.budget_engine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: engine 参数
#   fields: 参数 engine（无注解）
#   code: pre_flight_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PreFlightReport
#   name_en: PreFlightReport
#   intro: class PreFlightReport 源码 L72-L82
#   desc: 公共方法（定义序）: all_green；源码 L72-L82
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② PreFlightGate
#   name_en: PreFlightGate
#   intro: class PreFlightGate 源码 L85-L140
#   desc: 公共方法（定义序）: engine, gate, get_engine；源码 L85-L140
#   inputs: engine
#   outputs: 返回值
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: PreFlightReport, PreFlightGate
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def engine(self):
        """只读：engine（Stage 4 公共化）。"""
        return self._engine

    @engine.setter
    def engine(self, value):
        """写入：engine（Stage 4 公共化）。"""
        self._engine = value

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
