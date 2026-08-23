# [A_module] module_id=MOD-SIG-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-009 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.router
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""Signal Router sub-package——信号优先级路由（MOD-SIG-009）与冲突消解（MOD-SIG-010）。"""

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
