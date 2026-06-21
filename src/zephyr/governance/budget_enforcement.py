# 代理模块：将 zephyr.governance.budget_enforcement 重定向到实际模块
from zephyr.autonomy_core.skill_executor import BudgetEnforcer


def __getattr__(name):
    """延迟导入 BudgetEngine 避免循环依赖."""
    if name == "BudgetEngine":
        from zephyr.governance.budget_engine import BudgetEngine
        return BudgetEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["BudgetEnforcer", "BudgetEngine"]
