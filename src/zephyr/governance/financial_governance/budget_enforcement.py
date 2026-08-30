# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.financial_governance.budget_enforcement
# [DOMAIN] D_GOV_REPAIR
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
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# 代理模块：将 zephyr.governance.budget_enforcement 重定向到实际模块
"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: budget_enforcement.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 BudgetDimension, BudgetEnforcer, BudgetEngine, BudgetTracker, BurnRateMonit…
#   desc: __init__ import L0；__all__ 11 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（11 符号）
#   name_en: __all__
#   intro: BudgetDimension, BudgetEnforcer, BudgetEngine, BudgetTracker, BurnRateMonitor,…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.autonomy_core.skills.skill_executor import BudgetEnforcer
from zephyr.governance.intelligence_governance.model_router import ModelRouter, TaskComplexity
from zephyr.governance.ops_governance.budget_models import BudgetDimension
from zephyr.governance.ops_governance.budget_tracker import BudgetTracker, TrackerScope
from zephyr.governance.ops_governance.burn_rate_monitor import BurnRateMonitor
from zephyr.governance.ops_governance.degradation_manager import DegradationManager
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

__version__ = "0.8.0"
