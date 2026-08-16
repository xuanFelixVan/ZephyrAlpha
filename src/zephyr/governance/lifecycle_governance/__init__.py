# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV-lifecycle_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.governance.lifecycle_governance
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.governance.lifecycle_governance.__init__
#   intro: __unmanaged__src/zephyr/governance/lifecycle_governance/__init__.py 包入口
#   desc: MOD-GOV-lifecycle_governance 包入口，模块命名空间声明并声明 __all__（33项）
#   inputs: I1
#   outputs: zephyr.governance.lifecycle_governance 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（33项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.governance.lifecycle_governance 包公共 API
#   name_en: __all__ 33项
#   intro: __unmanaged__src/zephyr/governance/lifecycle_governance/__init__.py 包入口——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "APIEndpoint",
    "APIState",
    "DeprecationNotice",
    "MigrationPhase",
    "PLVCheck",
    "PLVSpec",
    "PhaseDef",
    "PhaseSpec",
    "RollbackState",
    "STATE_NAMESPACE",
    "TransitionPhase",
    "TransitionState",
    "api_lifecycle",
    "check_promotion_allowed",
    "create_transition_state",
    "deprecate_api",
    "evaluate_rollback",
    "get_next_phase",
    "get_next_phase",
    "get_phase_def",
    "get_phase_spec",
    "get_plv_spec",
    "load_persisted_state",
    "migration_strategy",
    "paper_live_transition",
    "persist_state",
    "post_live_verification",
    "recover",
    "remove_api",
    "rollback_state_machine",
    "safe_read_state",
    "valid_transition",
'transition']
