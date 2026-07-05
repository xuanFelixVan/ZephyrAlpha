# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.financial_governance.budget_enforcement
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
# 代理模块：将 zephyr.governance.budget_enforcement 重定向到实际模块
from zephyr.autonomy_core.skills.skill_executor import BudgetEnforcer
from zephyr.governance.ops_governance.budget_models import BudgetDimension
from zephyr.governance.ops_governance.budget_tracker import BudgetTracker, TrackerScope
from zephyr.governance.ops_governance.burn_rate_monitor import BurnRateMonitor
from zephyr.governance.ops_governance.degradation_manager import DegradationManager
from zephyr.governance.intelligence_governance.model_router import ModelRouter, TaskComplexity
from zephyr.governance.ops_governance.timeout_guard import TimeoutGuard, TimeoutLevel


def __getattr__(name):
    """延迟导入 BudgetEngine 避免循环依赖."""
    if name == "BudgetEngine":
        from zephyr.governance.ops_governance.budget_engine import BudgetEngine

        return BudgetEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BudgetDimension",
    "BudgetEnforcer",
    "BudgetEngine",
    "BudgetTracker",
    "BurnRateMonitor",
    "DegradationManager",
    "ModelRouter",
    "TaskComplexity",
    "TimeoutGuard",
    "TimeoutLevel",
    "TrackerScope",
]
