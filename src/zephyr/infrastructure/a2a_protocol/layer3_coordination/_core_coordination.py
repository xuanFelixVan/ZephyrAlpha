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

from .supervisor import Supervisor
from .construction_verifier import ConstructionVerifier, StubAnalysis, VerifierResult
from .deadlock_guard import DeadlockGuard
from .livelock_detector import LivelockDetector
from .cascade_guard import CascadeGuard
from .conflict_detector import ConflictDetector, Conflict, ConflictType, ConflictSeverity, ChangeRange, ChangeSet
from .arbitrator import Arbitrator, AgentRole, FileOwnership, AgentMeta, ArbitrationResult
from .semantic_diff import SemanticDiffEngine, SemanticDiffType, SemanticDiffEntry, SemanticDiffReport, SemanticRegion
