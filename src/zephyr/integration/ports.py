# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §ports
# [MODULE] zephyr.integration.ports
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.__init__
# [CONSUMERS] zephyr.integration.pipeline_orchestrator;zephyr.infrastructure.pipeline.layer_router
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Ports define structural interfaces only; no concrete implementations; no imports from zephyr.infrastructure.a2a_protocol.governance
# [MODIFY-GUARD] blueprint.md §ports; pipeline/__init__.py __all__
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_pipeline_ports.py
# [A_module] module_id=MOD-ORC_ports | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Protocol-based interface layer for pipeline->mcp dependency abstraction.

Breaks the deep dependency chain: pipeline->mcp->rollback->llm_security->shared.schema
by defining structural interfaces that pipeline depends on instead of importing
mcp concrete implementations directly.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

__all__ = [
    "BlueprintSearchProtocol",
    "DocumentGuardProtocol",
    "MCPServerProtocol",
]


@runtime_checkable
class BlueprintSearchProtocol(Protocol):
    """Structural interface for blueprint search functionality.

    Pipeline depends on this protocol instead of importing
    BlueprintSearchServer directly, breaking the pipeline->mcp link.
    """

    def find_relevant_blueprint(self, query: str, num_results: int = 3) -> dict[str, Any]: ...


@runtime_checkable
class MCPServerProtocol(Protocol):
    """Structural interface for MCP server operations.

    Pipeline depends on this protocol instead of importing
    MCP server implementations directly.
    """

    def serve(self, request: dict[str, Any]) -> dict[str, Any]: ...


@runtime_checkable
class DocumentGuardProtocol(Protocol):
    """Structural interface for document guard operations.

    Pipeline depends on this protocol instead of importing
    DocGuardServer directly.
    """

    def check_document(self, path: str) -> dict[str, Any]: ...
