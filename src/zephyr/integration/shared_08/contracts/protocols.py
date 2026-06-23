# [BLUEPRINT] SRC-183 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.protocols
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.gate.gate_result
# [CONSUMERS] zephyr.governance.rule_enforcement;zephyr.governance.behavioral_auditor;zephyr.governance.audit_trail;zephyr.infrastructure.rollback;zephyr.autonomy_core;zephyr.integration;zephyr.governance
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Protocols define structural interfaces only; no concrete implementations
# [MODIFY-GUARD] contracts_blueprint.md §Protocols; __init__.py __all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_protocols | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""Structural Protocol interfaces for cross-module contracts.

These @runtime_checkable Protocols break bidirectional dependencies by
defining shared structural interfaces that modules depend on instead of
depending on each other's concrete implementations.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from zephyr.integration.shared_08.contracts.gate.gate_result import GateResult

# ── 7 Protocol interfaces ────────────────────────────────────────────


@runtime_checkable
class GateActionProtocol(Protocol):
    """Structural interface for rollback/gate action execution."""

    def execute(self) -> GateResult: ...

    name: str


@runtime_checkable
class DriftBudgetCheckerProtocol(Protocol):
    """Structural interface for drift budget checking."""

    def check_budget_for_gate(self, module: str) -> dict: ...


@runtime_checkable
class RecoveryTriggerProtocol(Protocol):
    """Structural interface for drift recovery triggering."""

    def trigger_recovery(self, payload: dict) -> dict: ...


@runtime_checkable
class AuditWriterProtocol(Protocol):
    """Structural interface for immutable audit writing."""

    def write_audit(self, entry: dict) -> str: ...


@runtime_checkable
class DriftScannerProtocol(Protocol):
    """Structural interface for drift event scanning."""

    def scan_drift_events(self) -> list[dict]: ...


@runtime_checkable
class SelfTestableProtocol(Protocol):
    """Structural interface for self-test / health check components."""

    def run_self_test(self) -> bool: ...


@runtime_checkable
class ModuleStatusProtocol(Protocol):
    """Structural interface for module/pipeline status reporting."""

    def get_status(self) -> dict: ...


# ── Shared contract types ────────────────────────────────────────────


class AgentCapability(BaseModel):
    """Agent capability contract — shared across agent-spec / governance / audit."""

    agent_id: str
    capabilities: list[str] = []
    version: str = "1.0.0"
    spec_hash: str = ""


class IntegrityVerifier(BaseModel):
    """Integrity verification contract — shared across audit-trail / governance."""

    spec_hash: str = ""

    def verify_chain(self) -> dict: ...


_STABILITY_FROZEN = True
_FROZEN_PUBLIC_API = frozenset(
    {
        "GateActionProtocol",
        "DriftBudgetCheckerProtocol",
        "RecoveryTriggerProtocol",
        "AuditWriterProtocol",
        "DriftScannerProtocol",
        "SelfTestableProtocol",
        "ModuleStatusProtocol",
        "AgentCapability",
        "IntegrityVerifier",
    }
)


def __getattr__(name: str):
    if name in _FROZEN_PUBLIC_API:
        import logging

        logging.getLogger("zephyr.stability_guard").warning(
            "STABILITY VIOLATION: Public API attribute '%s' removed from frozen module zephyr.integration.shared_08.contracts.protocols",
            name,
        )
    raise AttributeError(f"module 'zephyr.integration.shared_08.contracts.protocols' has no attribute {name!r}")
