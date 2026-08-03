# [BLUEPRINT] MOD-EX_SOR | (pending)
# [MODULE] zephyr.ex_sor.core
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_sor/test_broker_adapter_manager.py; tests/ex_sor/test_optimal_order_router.py
# [A_module] module_id=MOD-EX_SOR | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ex_sor/core — 路由核心 (适配器/路由/调度/算法)

from typing import Final

from zephyr.ex_sor.core.broker_adapter_manager import (
    BrokerAdapter,
    BrokerAdapterError,
    BrokerAdapterManager,
    BrokerSelection,
    FailoverExhaustedError,
    NoAvailableBrokerError,
)
from zephyr.ex_sor.core.optimal_order_router import (
    DefaultMetricsProvider,
    InvalidRouteWeightsError,
    NoRouteAvailableError,
    OptimalOrderRouter,
    RouteDecision,
    RouteResult,
    RouteScore,
    RouteWeights,
    RoutingError,
)

__all__: Final = [
    # XS-002 Broker Adapter Manager
    "BrokerAdapter",
    "BrokerAdapterManager",
    "BrokerSelection",
    "BrokerAdapterError",
    "NoAvailableBrokerError",
    "FailoverExhaustedError",
    # XS-001 Optimal Order Router
    "OptimalOrderRouter",
    "RouteScore",
    "RouteWeights",
    "RouteDecision",
    "RouteResult",
    "DefaultMetricsProvider",
    "RoutingError",
    "NoRouteAvailableError",
    "InvalidRouteWeightsError",
]
