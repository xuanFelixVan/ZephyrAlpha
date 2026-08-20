# [BLUEPRINT] MOD-TASK_SYSTEM | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV-architecture_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.governance.architecture_governance
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.governance.architecture_governance.__init__
#   intro: MOD-TASK_SYSTEM 包入口
#   desc: MOD-TASK_SYSTEM 包入口，模块命名空间声明并声明 __all__（41项）
#   inputs: I1
#   outputs: zephyr.governance.architecture_governance 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（41项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.governance.architecture_governance 包公共 API
#   name_en: __all__ 41项
#   intro: MOD-TASK_SYSTEM 包入口——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "ArchPrinciple",
    "BTrackSystem",
    "BlueprintIronLaw",
    "CTrackLayer",
    "CircuitBreaker",
    "CircuitBreakerState",
    "ComputeLocation",
    "ConsistencyDim",
    "Contract",
    "DependencyTier",
    "LayerTopology",
    "LocalFirstPolicy",
    "ManagedDependency",
    "PathResolution",
    "PathResolver",
    "RuntimePlane",
    "architecture_contracts",
    "architecture_principles",
    "btrack_systems_for_layer",
    "cross_env_consistency",
    "dependency_manager",
    "generate_client_order_id",
    "get_by_tier",
    "get_core_deps",
    "get_downstream_chain",
    "get_layer",
    "get_layer_by_index",
    "get_principle_by_kb_ref",
    "get_upstream_chain",
    "layers_by_plane",
    "local_first_arch",
    "princpled_check",
    "reslove_path",
    "validate_against_principles",
    "blueprint_bloat_monitor",
    "blueprint_code_consistency",
    "blueprint_reconciler",
    "construction_verifier",
    "formal_verifier",
    "gap_analyzer",
    "post_sync_validator",
]
