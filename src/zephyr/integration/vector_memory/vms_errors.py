# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.vms_errors
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] collection_manager; design_principles; in_process_vector_memory; faiss_collection_manager; tests
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] VMSError is root; all VMS exceptions inherit from VMSError
# [MODIFY-GUARD] collection_manager.py; design_principles.py; in_process_vector_memory.py; faiss_collection_manager.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] VMSError hierarchy; no side effects
# [TESTS] tests/memory/test_vector_memory.py; tests/kb/test_cross_layer_systems_red_team.py
# [A_module] module_id=MOD-INT_vms_errors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

__all__: list[str] = [
    "ChunkStrategyError",
    "DesignPrincipleError",
    "DimensionError",
    "HotColdSeparationError",
    "ProvenanceMissingError",
    "TTLError",
    "VMSError",
]


class VMSError(Exception):
    pass


class DesignPrincipleError(VMSError):
    pass


class ProvenanceMissingError(VMSError):
    pass


class DimensionError(DesignPrincipleError):
    pass


class ChunkStrategyError(DesignPrincipleError):
    pass


class TTLError(DesignPrincipleError):
    pass


class HotColdSeparationError(DesignPrincipleError):
    pass
