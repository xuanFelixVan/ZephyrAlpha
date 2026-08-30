# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.legal_audit_chain
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.agent_rbac.test_forensic_c
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
LegalAuditChain - append-only hash-chained legal audit log.

治本(2026-07-19): 实现 append/verify 以匹配 tests/agent_rbac/test_forensic_c.py 契约.
- append(operation, actor) 追加条目, 每条哈希链接前一条
- verify() -> {intact: bool, length: int} 校验整链哈希完整性

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: legal_audit_chain.py
# 层: 算法
# - id: A1
#   name_zh: ① LegalAuditChain
#   name_en: LegalAuditChain
#   intro: class LegalAuditChain 源码 L68-L101
#   desc: 公共方法（定义序）: append, verify；源码 L68-L101
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: LegalAuditChain
#   downstream: tests.agent_rbac.test_forensic_c
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChainEntry:
    index: int = 0
    operation: str = ""
    actor: str = ""
    prev_hash: str = ""
    hash: str = ""


class LegalAuditChain:
    def __init__(self) -> None:
        self._entries: list[ChainEntry] = []

    def append(self, operation: str, actor: str) -> ChainEntry:
        prev_hash = self._entries[-1].hash if self._entries else ""
        index = len(self._entries)
        entry = ChainEntry(
            index=index,
            operation=operation,
            actor=actor,
            prev_hash=prev_hash,
        )
        entry.hash = self._compute_hash(entry)
        self._entries.append(entry)
        return entry

    def verify(self) -> dict[str, Any]:
        prev_hash = ""
        for i, entry in enumerate(self._entries):
            if entry.prev_hash != prev_hash:
                return {"intact": False, "length": len(self._entries)}
            if entry.index != i:
                return {"intact": False, "length": len(self._entries)}
            computed = self._compute_hash(entry)
            if entry.hash != computed:
                return {"intact": False, "length": len(self._entries)}
            prev_hash = entry.hash
        return {"intact": True, "length": len(self._entries)}

    @staticmethod
    def _compute_hash(entry: ChainEntry) -> str:
        payload = f"{entry.index}|{entry.operation}|{entry.actor}|{entry.prev_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


__all__ = ["ChainEntry", "LegalAuditChain"]
