# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.ops_governance.decision_fatigue
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: tasks 参数
#   fields: 参数 tasks，类型注解 list[TaskTriage]
#   code: decision_fatigue.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: level 参数
#   fields: 参数 level，类型注解 EisenhowerPriority
#   code: decision_fatigue.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① triage
#   name_en: triage
#   intro: triage(tasks) 源码 L100-L105
#   desc: 源码 L100-L105
#   inputs: tasks
#   outputs: dict[EisenhowerPriority, list[TaskTriag…
# - id: A2
#   name_zh: ② filter_priority
#   name_en: filter_priority
#   intro: filter_priority(tasks, level) 源码 L108-L109
#   desc: 源码 L108-L109
#   inputs: tasks level
#   outputs: list[TaskTriage]
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: dict[EisenhowerPriority, list[TaskTriag…
#   name_en: dict[EisenhowerPriority, list[TaskTriag…
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: list[TaskTriage]
#   name_en: list[TaskTriage]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class EisenhowerPriority(str, Enum):
    P0_DO_NOW = "P0"
    P1_SCHEDULE = "P1"
    P2_DELEGATE = "P2"
    P3_ELIMINATE = "P3"


class TaskTriage(BaseModel):
    task_id: str
    description: str
    urgent: bool = False
    important: bool = False
    priority: EisenhowerPriority = EisenhowerPriority.P3_ELIMINATE

    def classify(self) -> EisenhowerPriority:
        if self.urgent and self.important:
            self.priority = EisenhowerPriority.P0_DO_NOW
        elif self.important and not self.urgent:
            self.priority = EisenhowerPriority.P1_SCHEDULE
        elif self.urgent and not self.important:
            self.priority = EisenhowerPriority.P2_DELEGATE
        else:
            self.priority = EisenhowerPriority.P3_ELIMINATE
        return self.priority


def triage(tasks: list[TaskTriage]) -> dict[EisenhowerPriority, list[TaskTriage]]:
    result: dict[EisenhowerPriority, list[TaskTriage]] = {p: [] for p in EisenhowerPriority}
    for t in tasks:
        t.classify()
        result[t.priority].append(t)
    return result


def filter_priority(tasks: list[TaskTriage], level: EisenhowerPriority) -> list[TaskTriage]:
    return [t for t in tasks if t.priority == level]
