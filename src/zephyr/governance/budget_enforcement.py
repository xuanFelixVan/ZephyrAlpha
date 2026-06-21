# 代理模块：将 zephyr.governance.budget_enforcement 重定向到实际模块
from zephyr.autonomy_core.skill_executor import BudgetEnforcer
from zephyr.governance.burn_rate_monitor import BurnRateMonitor
from zephyr.governance.budget_tracker import BudgetTracker, TrackerScope
from zephyr.governance.degradation_manager import DegradationManager
from zephyr.governance.model_router import ModelRouter, TaskComplexity
from zephyr.governance.timeout_guard import TimeoutGuard, TimeoutLevel
from zephyr.governance.budget_models import BudgetDimension


def __getattr__(name):
    """延迟导入 BudgetEngine 避免循环依赖."""
    if name == "BudgetEngine":
        from zephyr.governance.budget_engine import BudgetEngine
        return BudgetEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BudgetEnforcer",
    "BudgetEngine",
    "BurnRateMonitor",
    "BudgetTracker",
    "TrackerScope",
    "DegradationManager",
    "ModelRouter",
    "TaskComplexity",
    "TimeoutGuard",
    "TimeoutLevel",
    "BudgetDimension",
]
