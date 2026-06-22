# [A_module] module_id=MOD-INF__core_coordination | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination._core_coordination
# [INVARIANTS] backward_compat: all exports must remain available from layer3_coordination
# [MODIFY-GUARD] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [CONSUMERS] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.infrastructure.a2a_protocol.layer3_coordination"
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
