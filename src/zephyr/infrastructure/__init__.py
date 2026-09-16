# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""


# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/infrastructure/infrastructure__init__.yaml
"""

from zephyr.infrastructure.gpu_hot_swap_model import GpuHotSwapModel

# [TTL] permanent
"""


[A_module] module_id=MOD-INFRA_RUNTIME | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

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
