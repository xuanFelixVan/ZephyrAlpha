# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.capacity_governance.capacity_runbook_generator
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.trading.resource_optimization
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: capacity_runbook_generator.py
# 层: 算法
# - id: A1
#   name_zh: ① CapacityRunbookGenerator
#   name_en: CapacityRunbookGenerator
#   intro: class CapacityRunbookGenerator 源码 L68-L83
#   desc: 公共方法（定义序）: generate；源码 L68-L83
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: CapacityRunbookGenerator
#   downstream: zephyr.trading.resource_optimization
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunbookStep:
    order: int
    action: str
    command: str
    validation: str


@dataclass
class Runbook:
    scenario: str
    steps: list[RunbookStep]
    rollback_steps: list[RunbookStep]


class CapacityRunbookGenerator:
    def generate(self, scenario: str, current_util: float, target_util: float) -> Runbook:
        if current_util > target_util:
            steps = [
                RunbookStep(1, "Assess load", "python scripts/governance/diagnose_depgraph.py", "exit 0"),
                RunbookStep(2, "Scale resources", "Adjust capacity allocation", "utilization < target"),
                RunbookStep(
                    3, "Verify SLO", "python scripts/governance/d11_compliance/audit_registration.py", "exit 0"
                ),
            ]
        else:
            steps = [
                RunbookStep(1, "Verify stability", "Monitor for 5 minutes", "no alerts"),
                RunbookStep(2, "Reduce allocation", "Release excess capacity", "utilization within bounds"),
            ]
        return Runbook(scenario, steps, list(reversed(steps)))
