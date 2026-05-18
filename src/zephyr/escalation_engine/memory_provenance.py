# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.memory_provenance

# [INVARIANTS] 记忆溯源不可缺失;trust_level必须验证

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Memory Provenance — v0.9.0 记忆溯源追踪: 每条memory record的来源agent+timestamp+hash链。
"""
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone

class MemoryProvenanceLog:
    def __init__(self):
        self._records:list[dict]=[]

    def record(self, agent_id:str, content:str, source_contract:str="")->str:
        h=hashlib.sha256(content.encode()).hexdigest()
        ts=datetime.now(timezone.utc).isoformat()
        self._records.append({"agent":agent_id,"hash":h,"timestamp":ts,"contract":source_contract})
        return h

    def trace(self, content_hash:str)->dict|None:
        for r in self._records:
            if r["hash"]==content_hash:
                return r
        return None
