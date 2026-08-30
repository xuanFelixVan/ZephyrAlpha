# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.bus_factor_defense
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/_domain_factor/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/governance/trading/test_bus_factor_defense.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ownership 参数
#   fields: 参数 ownership，类型注解 ModuleOwnership
#   code: bus_factor_defense.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: decision_id 参数
#   fields: 参数 decision_id，类型注解 str
#   code: bus_factor_defense.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: problem 参数
#   fields: 参数 problem，类型注解 str
#   code: bus_factor_defense.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: options 参数
#   fields: 参数 options，类型注解 list[str]
#   code: bus_factor_defense.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① evaluate_bus_factor
#   name_en: evaluate_bus_factor
#   intro: evaluate_bus_factor(ownership) 源码 L137-L145
#   desc: 源码 L137-L145
#   inputs: ownership
#   outputs: ModuleOwnership
# - id: A2
#   name_zh: ② create_decision_log
#   name_en: create_decision_log
#   intro: create_decision_log(decision_id, problem, options, decision…
#   desc: 源码 L152-L170
#   inputs: decision_id problem options decision rationale review_days
#   outputs: DecisionLog
# - id: A3
#   name_zh: ③ generate_runbook
#   name_en: generate_runbook
#   intro: generate_runbook(module_id, content) 源码 L173-L179
#   desc: 源码 L173-L179
#   inputs: module_id content
#   outputs: OpsRunbook
#   （注：A3 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ModuleOwnership
#   name_en: ModuleOwnership
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-020;MOD-INF-018
# - id: O2
#   name_zh: DecisionLog
#   name_en: DecisionLog
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-020;MOD-INF-018
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class BusFactorRisk(str, Enum):
    SAFE = "SAFE"
    AT_RISK = "AT_RISK"
    DANGER = "DANGER"


class ModuleOwnership(BaseModel):
    module_id: str
    owners: list[str] = Field(default_factory=list)
    bus_factor: int = 0
    risk: BusFactorRisk = BusFactorRisk.DANGER
    onboarding_readme: bool = False
    onboarding_diagram: bool = False
    onboarding_key_funcs: bool = False
    last_adr_update: str | None = None

    @property
    def onboarding_complete(self) -> bool:
        return self.onboarding_readme and self.onboarding_diagram and self.onboarding_key_funcs

    @property
    def onboarding_time_estimate(self) -> str:
        if self.onboarding_complete:
            return "<15min"
        return ">15min — INCOMPLETE"


class DecisionLog(BaseModel):
    decision_id: str
    problem: str
    options: list[str] = Field(default_factory=list)
    decision: str = ""
    rationale: str = ""
    review_date: str | None = None


class OpsRunbook(BaseModel):
    module_id: str
    auto_generated: bool = True
    content: str = ""
    generated_at: str = ""
    last_update: str | None = None


def evaluate_bus_factor(ownership: ModuleOwnership) -> ModuleOwnership:
    ownership.bus_factor = len(ownership.owners)
    if ownership.bus_factor >= 2:
        ownership.risk = BusFactorRisk.SAFE
    elif ownership.bus_factor == 1:
        ownership.risk = BusFactorRisk.AT_RISK
    else:
        ownership.risk = BusFactorRisk.DANGER
    return ownership


# 向后兼容别名（原 check_bus_factor 重命名为 evaluate_bus_factor）
check_bus_factor = evaluate_bus_factor


def create_decision_log(
    decision_id: str,
    problem: str,
    options: list[str],
    decision: str,
    rationale: str,
    review_days: int = 90,
) -> DecisionLog:
    from datetime import timedelta

    review_date = (datetime.now(UTC) + timedelta(days=review_days)).isoformat()
    return DecisionLog(
        decision_id=decision_id,
        problem=problem,
        options=options,
        decision=decision,
        rationale=rationale,
        review_date=review_date,
    )


def generate_runbook(module_id: str, content: str = "") -> OpsRunbook:
    return OpsRunbook(
        module_id=module_id,
        auto_generated=True,
        content=content or f"# Runbook: {module_id}\n\n## TBD",
        generated_at=datetime.now(UTC).isoformat(),
    )
