# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination._core_coordination
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer3_coordination.supervisor; zephyr.infrastructure.a2a_protocol.layer3_coordination.construction_verifier; zephyr.infrastructure.a2a_protocol.layer3_coordination.deadlock_guard; zephyr.infrastructure.a2a_protocol.layer3_coordination.livelock_detector; zephyr.infrastructure.a2a_protocol.layer3_coordination.cascade_guard; zephyr.infrastructure.a2a_protocol.layer3_coordination.conflict_detector; zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator; zephyr.infrastructure.a2a_protocol.layer3_coordination.semantic_diff
# [CONSUMERS] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] backward_compat: all exports must remain available from layer3_coordination
# [MODIFY-GUARD] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.infrastructure.a2a_protocol.layer3_coordination"
# [A_module] module_id=MOD-INF__core_coordination | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export bridge for layer3_coordination core coordination symbols.

Aggregates 23 symbols from 8 source modules to preserve backward compatibility
for ``from layer3_coordination._core_coordination import ...`` consumers.
"""

from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import (
    AgentMeta,
    AgentRole,
    ArbitrationResult,
    Arbitrator,
    FileOwnership,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.cascade_guard import (
    CascadeGuard,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.conflict_detector import (
    ChangeRange,
    ChangeSet,
    Conflict,
    ConflictDetector,
    ConflictSeverity,
    ConflictType,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.construction_verifier import (
    ConstructionVerifier,
    StubAnalysis,
    VerifierResult,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.deadlock_guard import (
    DeadlockGuard,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.livelock_detector import (
    LivelockDetector,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.semantic_diff import (
    SemanticDiffEngine,
    SemanticDiffEntry,
    SemanticDiffReport,
    SemanticDiffType,
    SemanticRegion,
)
from zephyr.infrastructure.a2a_protocol.layer3_coordination.supervisor import (
    Supervisor,
)

__all__ = [
    "AgentMeta",
    "AgentRole",
    "ArbitrationResult",
    "Arbitrator",
    "CascadeGuard",
    "ChangeRange",
    "ChangeSet",
    "Conflict",
    "ConflictDetector",
    "ConflictSeverity",
    "ConflictType",
    "ConstructionVerifier",
    "DeadlockGuard",
    "FileOwnership",
    "LivelockDetector",
    "SemanticDiffEngine",
    "SemanticDiffEntry",
    "SemanticDiffReport",
    "SemanticDiffType",
    "SemanticRegion",
    "StubAnalysis",
    "Supervisor",
    "VerifierResult",
]
