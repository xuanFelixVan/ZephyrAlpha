# [BLUEPRINT] MOD-EX_SOR | (pending)
# [MODULE] zephyr.ex_sor.core
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.ex_sor.core.broker_adapter_manager; zephyr.ex_sor.core.optimal_order_router; zephyr.ex_sor.core.rl_exec_boundary; zephyr.ex_sor.core.rl_exec_contract; zephyr.ex_sor.core.rl_exec_env; zephyr.ex_sor.core.sor_agent
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

"""

# [ALGO_FLOW] external: docs/03_modules/_domain_ex_sor/algo_flow/core__init__.yaml
"""

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
from zephyr.ex_sor.core.rl_exec_boundary import RlExecBoundary
from zephyr.ex_sor.core.rl_exec_contract import RlExecContract
from zephyr.ex_sor.core.rl_exec_env import RlExecEnv

# NOTE(P1W24 并行协调): scaffold 注册器 eager import bug 第十次复发（斜杠变种
# `zephyr.ex_sor/core.sor_agent`），按可逆模式归一为点号合法 import
# （与 #ARCH-228/235/238/242/246/250 同族）。
from zephyr.ex_sor.core.sor_agent import SorAgent

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

__all__.append("RlExecEnv")

__all__.append("RlExecContract")

__all__.append("RlExecBoundary")

__all__.append("SorAgent")

# XS-016 Sell Session Router（gw-tdm-20260909：C12 时段路由接线，包门面再导出）
from zephyr.ex_sor.core.sell_session_router import (
    RouteUrgency,
    SellChannel,
    SellRouteDecision,
    SellSessionRouterError,
    SessionRouterConfig,
    SessionWindow,
    classify_session,
    route_sell,
)

__all__.append("RouteUrgency")
__all__.append("SellChannel")
__all__.append("SellRouteDecision")
__all__.append("SellSessionRouterError")
__all__.append("SessionRouterConfig")
__all__.append("SessionWindow")
__all__.append("classify_session")
__all__.append("route_sell")
