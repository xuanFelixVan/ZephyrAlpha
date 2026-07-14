# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.provenance_enforcer
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.vector_memory.vms_schemas; zephyr.integration.vector_memory.collection_manager
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_provenance_enforcer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ProvenanceEnforcer — MOD-INF-011 写入溯源强制执行
===================================================
蓝图 §1 · §6 · WriteTrace 强制 + CBAC 集成

职责
----
- validate(WriteTrace) -> bool: 校验 origin/audit_chain/arbitration 三字段完整性
- attach(metadata, WriteTrace): 给已写入向量绑定 provenance 元数据
"""

from __future__ import annotations

import logging
from typing import Any

_logger = logging.getLogger(__name__)


from zephyr.integration.vector_memory.vms_schemas import WriteTrace


class ProvenanceEnforcer:
    @staticmethod
    def validate(trace: WriteTrace) -> bool:
        if trace is None:
            _logger.warning("ProvenanceEnforcer: WriteTrace 为 None")
            return False
        if not trace.origin:
            _logger.warning("ProvenanceEnforcer: origin 为空")
            return False
        if not trace.audit_chain or len(trace.audit_chain) < 1:
            _logger.warning("ProvenanceEnforcer: audit_chain 不完整")
            return False
        if not trace.arbitration:
            _logger.warning("ProvenanceEnforcer: arbitration 为空")
            return False
        return True

    @staticmethod
    def attach(metadata: dict[str, Any], provenance: dict[str, Any]) -> dict[str, Any]:
        meta = dict(metadata or {})
        meta["provenance"] = {
            "origin": provenance.get("origin"),
            "audit_chain": provenance.get("audit_chain"),
            "arbitration": provenance.get("arbitration"),
            "validated": True,
        }
        return meta

    @staticmethod
    def cbau_check(collection: str, operation: str, ai_session: object | None = None) -> bool:
        from zephyr.integration.vector_memory.collection_manager import COLLECTION_SCHEMAS

        schema = COLLECTION_SCHEMAS.get(collection, {})
        autonomy = schema.get("ai_autonomy_level", "")

        if autonomy == "human-gated":
            _logger.warning("CBAC: %s 是 human-gated，拒绝 AI 操作 '%s' (mitigates R10)", collection, operation)
            return False
        return True

    @staticmethod
    def ai_autonomy_gate(collection: str, session_type: str = "ai") -> bool:
        from zephyr.integration.vector_memory.collection_manager import COLLECTION_SCHEMAS

        schema = COLLECTION_SCHEMAS.get(collection, {})
        autonomy = schema.get("ai_autonomy_level", "")

        if session_type == "ai" and autonomy == "human-gated":
            _logger.warning("AI 自治门: %s 拒绝 AI session 写入 (mitigates R10/R12)", collection)
            return False
        return True
