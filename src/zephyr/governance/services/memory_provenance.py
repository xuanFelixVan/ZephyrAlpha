# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.services.memory_provenance
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 记忆溯源不可缺失;trust_level必须验证
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Memory Provenance — v0.9.0 记忆溯源追踪: 每条memory record的来源agent+timestamp+hash链。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: memory_provenance.py
# 层: 算法
# - id: A1
#   name_zh: ① MemoryProvenanceLog
#   name_en: MemoryProvenanceLog
#   intro: class MemoryProvenanceLog 源码 L54-L79
#   desc: 公共方法（定义序）: records, record, trace；源码 L54-L79
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: MemoryProvenanceLog
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime


class MemoryProvenanceLog:
    def __init__(self):
        self._records: list[dict] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def records(self) -> list[dict]:
        """只读：records（Stage 4 公共化）。"""
        return self._records

    @records.setter
    def records(self, value):
        """写入：records（Stage 4 公共化）。"""
        self._records = value

    def record(self, agent_id: str, content: str, source_contract: str = "") -> str:
        h = hashlib.sha256(content.encode()).hexdigest()
        ts = datetime.now(UTC).isoformat()
        self._records.append({"agent": agent_id, "hash": h, "timestamp": ts, "contract": source_contract})
        return h

    def trace(self, content_hash: str) -> dict | None:
        for r in self._records:
            if r["hash"] == content_hash:
                return r
        return None
