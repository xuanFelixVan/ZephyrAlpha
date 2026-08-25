# [BLUEPRINT] MOD-INF-016 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""


[A_module] module_id=MOD-TRADING | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.trading
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.trading.__init__
#   intro: [A_module] module_id=MOD-TRADING | layer=infrastructure | st
#   desc: MOD-INF-016 包入口，模块命名空间声明并声明 __all__（40项）
#   inputs: I1
#   outputs: zephyr.trading 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（40项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.trading 包公共 API
#   name_en: __all__ 40项
#   intro: [A_module] module_id=MOD-TRADING | layer=infrastructure | st——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "action_dispatcher",
    "admission_controller",
    "ai_audit_logger",
    "auto_dispatcher",
    "auto_integrator",
    "auto_runtime_core",
    "auto_task_generator",
    "autopilot",
    "boot_hooks",
    "capability_card",
    "capability_registry",
    "capability_sync",
    "conductor",
    "dream_cycle",
    "finalizer",
    "gpu_consensus_scheduler",
    "gpu_monitor",
    "health_monitor",
    "ide_health_daemon",
    "integration_registry",
    "lifecycle_manager",
    "module_onboarding_scanner",
    "night_shift_queue",
    "orphan_detector",
    "ports",
    "protection_index",
    "resource_optimization",
    "runtime_config",
    "speed_baseline_checker",
    "staging_area",
    "status_dashboard",
    "stop_gate",
    "task_gate",
    "verdict_engine",
    "windows_service",
    "work_dag",
    "work_orchestrator",
    "zombie_scanner",
    "trigger_registry",
    "__main__",
]

from zephyr.trading import (
    trigger_registry,  # noqa: F401  # ORPHAN-MODULE: 新模块引用登记（41_buy_flow §3.9 MOD-TRIG-001）
)
from zephyr.trading.strategy_abnormal_exit_orchestrator import StrategyAbnormalExitOrchestrator
from zephyr.trading.trading_core_process_spec import TradingCoreProcessSpec

__all__.append("StrategyAbnormalExitOrchestrator")

__all__.append("TradingCoreProcessSpec")
