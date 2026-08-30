# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.ai_guards.ai_audit_guard
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
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
#   name: require_approval_for 参数
#   fields: 参数 require_approval_for（无注解）
#   code: ai_audit_guard.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AiAuditGuard
#   name_en: AiAuditGuard
#   intro: class AiAuditGuard 源码 L64-L95
#   desc: 公共方法（定义序）: check, approve, get_pending；源码 L64-L95
#   inputs: require_approval_for
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AiAuditGuard
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditRecord:
    operation: str
    agent_id: str
    timestamp: float
    details: dict[str, Any] = field(default_factory=dict)
    approved: bool = True


class AiAuditGuard:
    def __init__(self, require_approval_for: tuple[str, ...] = ("delete", "modify_core")):
        self._require_approval = set(require_approval_for)
        self._records: list[AuditRecord] = []
        self._pending: list[AuditRecord] = []

    def check(self, operation: str, agent_id: str, **details: Any) -> AuditRecord:
        needs_approval = any(op in operation for op in self._require_approval)
        record = AuditRecord(
            operation=operation,
            agent_id=agent_id,
            timestamp=time.time(),
            details=details,
            approved=not needs_approval,
        )
        if needs_approval:
            self._pending.append(record)
        else:
            self._records.append(record)
        return record

    def approve(self, operation: str, agent_id: str) -> bool:
        for i, r in enumerate(self._pending):
            if r.operation == operation and r.agent_id == agent_id:
                r.approved = True
                self._records.append(r)
                self._pending.pop(i)
                return True
        return False

    def get_pending(self) -> list[AuditRecord]:
        return list(self._pending)
