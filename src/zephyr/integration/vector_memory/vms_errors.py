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
# [A_module] module_id=MOD-INF-011 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
    error_code = "ZA-IG-0001"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class DesignPrincipleError(VMSError):
    error_code = "ZA-IG-0002"


class ProvenanceMissingError(VMSError):
    error_code = "ZA-IG-0003"


class DimensionError(DesignPrincipleError):
    error_code = "ZA-IG-0004"


class ChunkStrategyError(DesignPrincipleError):
    error_code = "ZA-IG-0005"


class TTLError(DesignPrincipleError):
    error_code = "ZA-IG-0006"


class HotColdSeparationError(DesignPrincipleError):
    error_code = "ZA-IG-0007"
