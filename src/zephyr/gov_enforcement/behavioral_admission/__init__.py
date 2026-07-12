# [BLUEPRINT] MOD-GOV_behavioral_admission | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.gov_enforcement.behavioral_admission
# [DOMAIN] D_GOV_ENFORCEMENT
# [A_module] module_id=MOD-GOV_behavioral_admission | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Existing governance/behavioral-admission imports
from zephyr.gov_enforcement.behavioral_admission.admission_controller import (
    AdmissionController,
    AdmissionDecision,
)
from zephyr.gov_enforcement.behavioral_admission.admission_response import (
    AdmissionResponse,
    AdmissionResponseBuilder,
    AdmissionResponseStatus,
    InvalidDecisionError,
)
from zephyr.gov_enforcement.behavioral_admission.code_review_ai import ReviewLevel
from zephyr.gov_enforcement.behavioral_admission.gpu_consensus_scheduler import (
    ConsensusPriority,
    ConsensusRoute,
    GPUConsensusScheduler,
)
from zephyr.gov_enforcement.behavioral_admission.mcp_result_push import (
    CallbackConnectionError,
    PushError,
    PushStatus,
    ResultPushManager,
)
from zephyr.gov_enforcement.behavioral_admission.post_process import (
    HookResult,
    HookStrategy,
    PipelineResult,
    PostProcessHook,
    PostProcessPipeline,
    format_hook,
    lint_hook,
    typecheck_hook,
)
from zephyr.gov_enforcement.behavioral_admission.protection_index import ProtectionIndex
from zephyr.gov_enforcement.behavioral_admission.session_lifecycle import (
    SessionLifecycle,
    SessionState,
)

# Migrated from compliance/behavioral-admission
from zephyr.gov_enforcement.behavioral_admission.verdict_engine import (
    GraduatedLevel,
    ProtectionLevel,
    VerdictEngine,
    VerdictLevel,
)
from zephyr.gov_enforcement.behavioral_admission.vibe_coding_enforcer import (
    VibeRuleLevel,
    enforce,
    enforce_all,
    list_rules_by_level,
    must,
    should,
)
from zephyr.gov_enforcement.behavioral_admission.gate_event_adapter import GateEventAdapter

__all__ = [
    "AdmissionController",
    "AdmissionDecision",
    "AdmissionResponse",
    "AdmissionResponseBuilder",
    "AdmissionResponseStatus",
    "CallbackConnectionError",
    "ConsensusPriority",
    "ConsensusRoute",
    "GPUConsensusScheduler",
    "GraduatedLevel",
    "HookResult",
    "HookStrategy",
    "InvalidDecisionError",
    "PipelineResult",
    "PostProcessHook",
    "PostProcessPipeline",
    "ProtectionIndex",
    "ProtectionLevel",
    "PushError",
    "PushStatus",
    "ResultPushManager",
    "ReviewLevel",
    "SessionLifecycle",
    "SessionState",
    "VerdictEngine",
    "VerdictLevel",
    "VibeRuleLevel",
    "admission_controller",
    "ai_code_standards",
    "code_review_ai",
    "enforce",
    "enforce_all",
    "format_hook",
    "gpu_consensus_scheduler",
    "lint_hook",
    "list_rules_by_level",
    "mcp_result_push",
    "must",
    "post_process",
    "protection_index",
    "session_lifecycle",
    "should",
    "typecheck_hook",
    "verdict_engine",
    "vibe_coding_enforcer",
    "gate_event_adapter",
]
