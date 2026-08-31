# [BLUEPRINT] MOD-BT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
"""
[A_module] module_id=MOD-BT-001_implementations | layer=domain | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: EventDrivenEngine, BacktestConfig, DefaultBacktestEngine
#   code: __init__.py import L31
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 BacktestConfig, DefaultBacktestEngine, EventDrivenEngine, vectorized_engine…
#   desc: __init__ import L31；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: BacktestConfig, DefaultBacktestEngine, EventDrivenEngine, vectorized_engine, ev…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.backtest.implementations.event_driven_engine import EventDrivenEngine
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)

__all__ = [
    "BacktestConfig",
    "DefaultBacktestEngine",
    "EventDrivenEngine",
    "vectorized_engine",
    "event_driven_engine",
]
