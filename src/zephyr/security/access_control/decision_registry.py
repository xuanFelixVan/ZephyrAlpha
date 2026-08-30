# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md
# [MODULE] zephyr.security.access_control.decision_registry
# [DOMAIN] D_SECURITY
# [MATURITY] production
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
DecisionRegistry - decision log with query and stats.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: decision_registry.py
# 层: 算法
# - id: A1
#   name_zh: ① DecisionRegistry
#   name_en: DecisionRegistry
#   intro: class DecisionRegistry 源码 L58-L78
#   desc: 公共方法（定义序）: log, query, stats；源码 L58-L78
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DecisionRegistry
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Final


@dataclass
class DecisionRecord:
    agent_id: str = ""
    operation: str = ""
    resource: str = ""
    result: str = ""
    rule_id: str = ""
    timestamp: float = field(default_factory=time.time)


class DecisionRegistry:
    def __init__(self) -> None:
        self._records: list[DecisionRecord] = []

    def log(self, agent_id: str, operation: str, resource: str, result: str, rule_id: str = "") -> DecisionRecord:
        record = DecisionRecord(
            agent_id=agent_id, operation=operation, resource=resource, result=result, rule_id=rule_id
        )
        self._records.append(record)
        return record

    def query(self, agent_id: str | None = None) -> list[DecisionRecord]:
        if agent_id is None:
            return list(self._records)
        return [r for r in self._records if r.agent_id == agent_id]

    def stats(self) -> dict[str, Any]:
        total = len(self._records)
        allowed = sum(1 for r in self._records if r.result == "ALLOWED")
        denied = sum(1 for r in self._records if r.result == "DENIED")
        return {"total": total, "allowed": allowed, "denied": denied}


__all__: Final = ["DecisionRecord", "DecisionRegistry"]
