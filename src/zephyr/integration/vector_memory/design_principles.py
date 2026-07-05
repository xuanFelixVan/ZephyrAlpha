# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.design_principles
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.vector_memory.collection_schemas; zephyr.integration.vector_memory.vms_errors; zephyr.integration.vector_memory.provenance_enforcer; zephyr.integration.vector_memory.vms_schemas
# [CONSUMERS] collection_manager; in_process_vector_memory; faiss_collection_manager; tests
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] validate_dimension enforces ALLOWED_DIMENSIONS; validate_provenance enforces provenance metadata; hot/cold separation enforced
# [MODIFY-GUARD] collection_manager.py; in_process_vector_memory.py; faiss_collection_manager.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises DimensionError/ChunkStrategyError/TTLError/HotColdSeparationError/ProvenanceMissingError on validation failure
# [TESTS] tests/memory/test_vector_memory.py
# [A_module] module_id=MOD-INT_design_principles | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from typing import Any, ClassVar

from zephyr.integration.vector_memory.collection_schemas import (
    ALLOWED_DIMENSIONS,
    CHUNK_STRATEGIES_COLD,
    CHUNK_STRATEGIES_HOT,
    COLD_COLLECTIONS,
    COLLECTION_SCHEMAS,
    HOT_COLLECTIONS,
    TTL_MAP,
)
from zephyr.integration.vector_memory.vms_errors import (
    DimensionError,
    HotColdSeparationError,
    ProvenanceMissingError,
    TTLError,
)

__all__: list[str] = ["DesignPrinciplesEnforcer"]

_logger = logging.getLogger(__name__)


class DesignPrinciplesEnforcer:
    ALLOWED_DIMENSIONS: ClassVar[frozenset[int]] = ALLOWED_DIMENSIONS
    HOT_COLLECTIONS: ClassVar[frozenset[str]] = HOT_COLLECTIONS
    COLD_COLLECTIONS: ClassVar[frozenset[str]] = COLD_COLLECTIONS

    @staticmethod
    def validate_dimension(dim: int) -> None:
        if dim not in ALLOWED_DIMENSIONS:
            raise DimensionError(f"嵌入维度 {dim} 不在白名单中。允许: {sorted(ALLOWED_DIMENSIONS)}")

    @staticmethod
    def validate_chunk_strategy(name: str, chunk_strategy: str) -> None:
        if name in HOT_COLLECTIONS and chunk_strategy in CHUNK_STRATEGIES_COLD:
            raise HotColdSeparationError(
                f"热数据 Collection '{name}' 不可使用冷数据分块策略 '{chunk_strategy}'。"
                f"允许: {sorted(CHUNK_STRATEGIES_HOT)}"
            )
        if name in COLD_COLLECTIONS and chunk_strategy in CHUNK_STRATEGIES_HOT:
            _logger.warning(
                "冷数据 Collection '%s' 使用了热数据分块策略 '%s'——可能不适合",
                name,
                chunk_strategy,
            )
        schema = COLLECTION_SCHEMAS.get(name, {})
        expected = schema.get("chunk_strategy", "")
        if expected and chunk_strategy != expected:
            _logger.warning(
                "Collection '%s' 的分块策略 '%s' 与蓝图预期 '%s' 不一致",
                name,
                chunk_strategy,
                expected,
            )

    @staticmethod
    def validate_ttl(name: str, ttl_days: int) -> None:
        expected_ttl = TTL_MAP.get(name)
        if expected_ttl is not None and ttl_days != expected_ttl:
            raise TTLError(f"Collection '{name}' 的 TTL 应为 {expected_ttl}d，实际 {ttl_days}d")

    @staticmethod
    def validate_provenance(metadata: dict[str, Any] | None) -> None:
        if metadata is None:
            raise ProvenanceMissingError("写入操作必须提供 provenance metadata")
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer
        from zephyr.integration.vector_memory.vms_schemas import WriteTrace

        prov = metadata.get("provenance", {})
        origin = prov.get("origin", "") if isinstance(prov, dict) else ""
        if not origin:
            origin = metadata.get("origin", "")
        audit_chain = prov.get("audit_chain", None) if isinstance(prov, dict) else None
        if audit_chain is None:
            audit_chain = metadata.get("audit_chain", [])
        arbitration = prov.get("arbitration", "") if isinstance(prov, dict) else ""
        if not arbitration:
            arbitration = metadata.get("arbitration", "")
        trace = WriteTrace(origin=origin, audit_chain=audit_chain, arbitration=arbitration)
        if not ProvenanceEnforcer.validate(trace):
            raise ProvenanceMissingError("provenance 校验失败: origin/audit_chain/arbitration 不完整")

    @staticmethod
    def validate_all(
        name: str,
        dim: int,
        chunk_strategy: str,
        ttl_days: int,
        strict: bool = True,
    ) -> None:
        DesignPrinciplesEnforcer.validate_dimension(dim)
        if strict:
            DesignPrinciplesEnforcer.validate_chunk_strategy(name, chunk_strategy)
            DesignPrinciplesEnforcer.validate_ttl(name, ttl_days)
        else:
            DesignPrinciplesEnforcer.validate_chunk_strategy(name, chunk_strategy)
