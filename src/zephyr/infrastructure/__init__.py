# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: GpuHotSwapModel
#   code: __init__.py import L31
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 auto_diagnostics, blueprint_code_sync, config_validator, contract_tester, c…
#   desc: __init__ import L31；__all__ 23 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（23 符号）
#   name_en: __all__
#   intro: auto_diagnostics, blueprint_code_sync, config_validator, contract_tester, cost_…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.infrastructure.gpu_hot_swap_model import GpuHotSwapModel

# [TTL] permanent
"""


[A_module] module_id=MOD-INFRA_RUNTIME | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.infrastructure
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.infrastructure.__init__
#   intro: [A_module] module_id=MOD-INFRA_RUNTIME | layer=infrastructur
#   desc: MOD-INFRA_RUNTIME 包入口，模块命名空间声明并声明 __all__（17项）
#   inputs: I1
#   outputs: zephyr.infrastructure 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（17项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.infrastructure 包公共 API
#   name_en: __all__ 17项
#   intro: [A_module] module_id=MOD-INFRA_RUNTIME | layer=infrastructur——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

# D_INFRA_RUNTIME Domain Package
# This package unifies runtime orchestration, lifecycle management,
# event routing, and infrastructure services.

__all__ = [
    "auto_diagnostics",
    "blueprint_code_sync",
    "config_validator",
    "contract_tester",
    "cost_tracker",
    "database_service",
    "dry_run_simulator",
    "event_bus_upgrade",
    "event_store",
    "file_watcher",
    "finding_task_bridge",
    "hot_plane_budget",
    "infrastructure_base",
    "kill_switch_sim",
    "process_supervisor",
    "pydantic_v2_migrator",
    "redis_state_layer_ssot",
    "registry_governance",
    "signal_engine_process_spec",
    "strategy_canary_release",
    "system_snapshot",
    "warm_hot_gate",
    "warm_plane_budget",
]

__all__.append("GpuHotSwapModel")
# NOTE(P1W17): scaffold 注册器行首 eager import + 类名 append 已归一为模块名条目
# （signal_engine_process_spec/warm_plane_budget 按字母序入列），恢复本包"纯模块名导出"
# 约定；GpuHotSwapModel 行首 eager import 为前波残留，本波未动。
# NOTE(P1W24): MOD-INF-072 strategy_canary_release 按同约定模块名入列（字母序），
# scaffold 产生的行首 eager import+类名 append 已归一。
