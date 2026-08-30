# [A_module] module_id=MOD-SIG-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-009 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.router
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""
Signal Router sub-package——信号优先级路由（MOD-SIG-009）与冲突消解（MOD-SIG-010）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, Final, ConflictResolution, ConflictResolverConfig, Confl…
#   code: __init__.py import L39
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 annotations, Final, ConflictResolution, ConflictResolverConfig, ConflictSig…
#   desc: __init__ import L39；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（12 符号）
#   name_en: __all__
#   intro: annotations, Final, ConflictResolution, ConflictResolverConfig, ConflictSignal,…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Final

from zephyr.signal_fundamental.router.signal_conflict_resolver import (
    ConflictResolution,
    ConflictResolverConfig,
    ConflictSignal,
    ResolutionAction,
    resolve_conflicts,
)
from zephyr.signal_fundamental.router.signal_priority_router import (
    PriorityRouterConfig,
    RoutableSignal,
    RouteResult,
    SignalKind,
    route_signals,
)

__all__: Final = [
    "ConflictResolution",
    "ConflictResolverConfig",
    "ConflictSignal",
    "PriorityRouterConfig",
    "ResolutionAction",
    "RoutableSignal",
    "RouteResult",
    "SignalKind",
    "resolve_conflicts",
    "route_signals",
]
