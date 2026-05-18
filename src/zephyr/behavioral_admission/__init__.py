# [BLUEPRINT] MOD-INF-033 | 03_modules/_cross_layer/behavioral-auditor/blueprint.md | §4
# [MODULE] zephyr.behavioral_admission
# [INVARIANTS] behavioral_audit是MOD-INF-033独有目录；54个共享文件属于MOD-INF-023(src/zephyr/behavioral_auditor/)，033通过import消费
# [MODIFY-GUARD] docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md;src/zephyr/behavioral_auditor/__init__.py
# [CONSUMERS] MOD-INF-027(audit_orchestrator);MOD-INF-031(auto_fix_engine)
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VerdictEngine.evaluate: PermissionCheckTimeout→默认BLOCK; AdmissionController.admit: RateLimited→retry_after_ms
# [TESTS] tests/test_behavioral_audit/

from zephyr.behavioral_admission.verdict_engine import (
    VerdictEngine, VerdictLevel, ProtectionLevel, GraduatedLevel,
)
from zephyr.behavioral_admission.admission_controller import (
    AdmissionController, AdmissionDecision,
)
from zephyr.behavioral_admission.protection_index import ProtectionIndex
from zephyr.behavioral_admission.gpu_consensus_scheduler import (
    GPUConsensusScheduler, ConsensusPriority, ConsensusRoute,
)
from zephyr.behavioral_admission.session_lifecycle import (
    SessionLifecycle, SessionState,
)

__all__ = [
    "VerdictEngine", "VerdictLevel", "ProtectionLevel", "GraduatedLevel",
    "AdmissionController", "AdmissionDecision",
    "ProtectionIndex",
    "gpu_consensus_scheduler",
    "GPUConsensusScheduler", "ConsensusPriority", "ConsensusRoute",
    "SessionLifecycle", "SessionState",
]
