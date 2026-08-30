# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.worm_write_integrity
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
WORM Write Integrity — v0.15.0 R216

Blindspot: FLE audit log writable; attacker can erase evidence after the fact.
Risk: R216 — Audit trail modified post-incident; forensic investigation impossible.

Mitigation: Write-Once-Read-Many (WORM) storage for all FLE decision and action logs.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: worm_write_integrity.py
# 层: 算法
# - id: A1
#   name_zh: ① WORMWriteIntegrity
#   name_en: WORMWriteIntegrity
#   intro: class WORMWriteIntegrity 源码 L70-L90
#   desc: 公共方法（定义序）: write, verify, seal；源码 L70-L90
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: WORMWriteIntegrity
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


@dataclass
class WORMEntry:
    entry_id: str
    content_hash: str
    timestamp: str
    data: str


@dataclass
class WORMWriteIntegrity:
    entries: list[WORMEntry] = field(default_factory=list)
    sealed: bool = False

    def write(self, entry_id: str, data: dict) -> WORMEntry:
        if self.sealed:
            raise PermissionError("WORM storage is sealed; cannot write")
        content_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        entry = WORMEntry(entry_id=entry_id, content_hash=content_hash, timestamp="", data=json.dumps(data))
        self.entries.append(entry)
        return entry

    def verify(self, entry_id: str, expected_data: dict) -> bool:
        for e in self.entries:
            if e.entry_id == entry_id:
                current_hash = hashlib.sha256(json.dumps(expected_data, sort_keys=True).encode()).hexdigest()
                return e.content_hash == current_hash
        return False

    def seal(self) -> None:
        self.sealed = True
