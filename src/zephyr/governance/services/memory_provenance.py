# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.services.memory_provenance
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 记忆溯源不可缺失;trust_level必须验证
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_memory_provenance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Memory Provenance — v0.9.0 记忆溯源追踪: 每条memory record的来源agent+timestamp+hash链。
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime


class MemoryProvenanceLog:
    def __init__(self):
        self._records: list[dict] = []

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
