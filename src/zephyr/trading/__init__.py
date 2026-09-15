# [BLUEPRINT] MOD-INF-016 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""


[A_module] module_id=MOD-TRADING | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [ALGO_FLOW] external: docs/03_modules/_domain_trading/algo_flow/trading__init__.yaml
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
    "trigger_registry",
    "__main__",
]

from zephyr.trading import (
    trigger_registry,  # noqa: F401  # ORPHAN-MODULE: 新模块引用登记（41_buy_flow §3.9 MOD-TRIG-001）
)
from zephyr.trading.strategy_abnormal_exit_orchestrator import StrategyAbnormalExitOrchestrator
from zephyr.trading.trading_core_process_spec import TradingCoreProcessSpec
from zephyr.trading.trading_order_aggregate import TradingOrderAggregate
from zephyr.trading.eod_processor import EodProcessor
from zephyr.trading.manual_instruction_channel import ManualInstructionChannel
from zephyr.trading.settlement_record_aggregate import SettlementRecordAggregate

__all__.append("StrategyAbnormalExitOrchestrator")

__all__.append("TradingCoreProcessSpec")

__all__.append("TradingOrderAggregate")

__all__.append("EodProcessor")

__all__.append("ManualInstructionChannel")

__all__.append("SettlementRecordAggregate")

from zephyr.trading.decision_map import (
    DecisionMap,
    DecisionMapSchemaError,
    load_decision_map,
    validate_decision_map,
)

__all__.append("DecisionMap")
__all__.append("DecisionMapSchemaError")
__all__.append("load_decision_map")
__all__.append("validate_decision_map")
