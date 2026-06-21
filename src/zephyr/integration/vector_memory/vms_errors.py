# [A_module] module_id=MOD-INT_vms_errors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain-knowledge/vector-memory/blueprint.md | §

# [MODULE] zephyr.integration.vector_memory.vms_errors

# [INVARIANTS] VMSError is root; all VMS exceptions inherit from VMSError

# [MODIFY-GUARD] collection_manager.py; design_principles.py; in_process_vector_memory.py; faiss_collection_manager.py

# [CONSUMERS] collection_manager; design_principles; in_process_vector_memory; faiss_collection_manager; tests

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] VMSError hierarchy; no side effects

# [TESTS] tests/unit/vector-memory/test_vector_memory.py; tests/adversarial/test_cross_layer_systems_red_team.py

from __future__ import annotations

__all__: list[str] = [
    "VMSError",
    "DesignPrincipleError",
    "ProvenanceMissingError",
    "DimensionError",
    "ChunkStrategyError",
    "TTLError",
    "HotColdSeparationError",
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
