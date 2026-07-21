# [BLUEPRINT] MOD-GOV_behavioral_admission | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.gov_enforcement.behavioral_admission
# [DOMAIN] D_GOV_ENFORCEMENT
# [A_module] module_id=MOD-GOV-behavioral_admission | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
# #ARCH-WORKTREE-LIFECYCLE-001 (2026-07-21): session_lifecycle.py 已删除（死代码，生产引用=0）
# 替代状态机：rule_bridge.worktree_lifecycle.WorktreeLifecycle（5态，专门管理 worktree 生命周期）
# 此处 re-export 保持 behavioral_admission 包入口的可见性，便于 callers 发现新状态机
from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import (
    WorktreeLifecycle,
    WorktreeState,
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
    # "SessionLifecycle",  # removed #ARCH-WORKTREE-LIFECYCLE-001
    # "SessionState",      # removed #ARCH-WORKTREE-LIFECYCLE-001
    "VerdictEngine",
    "VerdictLevel",
    "VibeRuleLevel",
    "WorktreeLifecycle",  # added #ARCH-WORKTREE-LIFECYCLE-001
    "WorktreeState",       # added #ARCH-WORKTREE-LIFECYCLE-001
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
    # "session_lifecycle",  # removed #ARCH-WORKTREE-LIFECYCLE-001
    "should",
    "typecheck_hook",
    "verdict_engine",
    "vibe_coding_enforcer",
    "gate_event_adapter",
]
