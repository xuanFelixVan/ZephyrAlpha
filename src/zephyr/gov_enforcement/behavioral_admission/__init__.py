# [BLUEPRINT] MOD-GOV_BEHAVIORAL_ADMISSION | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.gov_enforcement.behavioral_admission
# [DOMAIN] D_GOV_ENFORCEMENT
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-GOV_BEHAVIORAL_ADMISSION | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Existing governance/behavioral-admission imports
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: admission_controller 子模块符号 2个
#   fields: AdmissionController / AdmissionDecision
#   code: zephyr.gov_enforcement.behavioral_admission.admission_controller
# - id: I2
#   name: admission_response 子模块符号 4个
#   fields: AdmissionResponse / AdmissionResponseBuilder / AdmissionResponseStatus / InvalidDecisionError
#   code: zephyr.gov_enforcement.behavioral_admission.admission_response
# - id: I3
#   name: code_review_ai 子模块符号 1个
#   fields: ReviewLevel
#   code: zephyr.gov_enforcement.behavioral_admission.code_review_ai
# - id: I4
#   name: gate_event_adapter 子模块符号 1个
#   fields: GateEventAdapter
#   code: zephyr.gov_enforcement.behavioral_admission.gate_event_adapter
# - id: I5
#   name: gpu_consensus_scheduler 子模块符号 3个
#   fields: ConsensusPriority / ConsensusRoute / GPUConsensusScheduler
#   code: zephyr.gov_enforcement.behavioral_admission.gpu_consensus_scheduler
# - id: I6
#   name: mcp_result_push 子模块符号 4个
#   fields: CallbackConnectionError / PushError / PushStatus / ResultPushManager
#   code: zephyr.gov_enforcement.behavioral_admission.mcp_result_push
# - id: I7
#   name: post_process 子模块符号 8个
#   fields: HookResult / HookStrategy / PipelineResult / PostProcessHook / PostProcessPipeline / format_hook 等8个
#   code: zephyr.gov_enforcement.behavioral_admission.post_process
# - id: I8
#   name: protection_index 子模块符号 1个
#   fields: ProtectionIndex
#   code: zephyr.gov_enforcement.behavioral_admission.protection_index
# - id: I9
#   name: verdict_engine 子模块符号 4个
#   fields: GraduatedLevel / ProtectionLevel / VerdictEngine / VerdictLevel
#   code: zephyr.gov_enforcement.behavioral_admission.verdict_engine
# - id: I10
#   name: vibe_coding_enforcer 子模块符号 6个
#   fields: VibeRuleLevel / enforce / enforce_all / list_rules_by_level / must / should
#   code: zephyr.gov_enforcement.behavioral_admission.vibe_coding_enforcer
# - id: I11
#   name: worktree_lifecycle 子模块符号 2个
#   fields: WorktreeLifecycle / WorktreeState
#   code: zephyr.gov_enforcement.rule_bridge.worktree_lifecycle
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.gov_enforcement.behavioral_admission.__init__
#   intro: Existing governance/behavioral-admission imports
#   desc: MOD-GOV_BEHAVIORAL_ADMISSION 包入口，包级聚合再导出并声明 __all__（45项）
#   inputs: I1 I2 I3 I4 I5 I6 I7 I8 I9 I10 I11
#   outputs: zephyr.gov_enforcement.behavioral_admission 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（45项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.gov_enforcement.behavioral_admission 包公共 API
#   name_en: __all__ 45项
#   intro: Existing governance/behavioral-admission imports——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# I5 --> A1
# I6 --> A1
# I7 --> A1
# I8 --> A1
# I9 --> A1
# I10 --> A1
# I11 --> A1
# A1 --> O1
"""

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
from zephyr.gov_enforcement.behavioral_admission.gate_event_adapter import GateEventAdapter
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

# #ARCH-WORKTREE-LIFECYCLE-001 (2026-07-21): session_lifecycle.py 已删除（死代码，生产引用=0）
# 替代状态机：rule_bridge.worktree_lifecycle.WorktreeLifecycle（5态，专门管理 worktree 生命周期）
# 此处 re-export 保持 behavioral_admission 包入口的可见性，便于 callers 发现新状态机
from zephyr.gov_enforcement.rule_bridge.worktree_lifecycle import (
    WorktreeLifecycle,
    WorktreeState,
)

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
