# [BLUEPRINT] MOD-EX_SOR | (pending)
# [MODULE] zephyr.ex_sor.api
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
# [TESTS] tests/ex_sor/test_api_rate_limiter.py; tests/ex_sor/test_broker_api_connector.py
# [A_module] module_id=MOD-EX_SOR | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ex_sor/api — 券商API层 (限速器/连接器)

"""

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包标记文件（无数据输入）
#   fields: 无字段——包内仅此 __init__.py 占位/聚合，无独立业务逻辑
#   code: src/zephyr/ex_sor/api/__init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包命名空间占位/聚合导出
#   name_en: __init__（模块级 __all__）
#   intro: 声明 zephyr.ex_sor.api 包命名空间，按 __all__ 声明导出
#   desc: 包级占位/聚合再导出，无函数无副作用，子模块挂载点
#   inputs: I1
#   outputs: 包级公共命名空间
# 层: 输出
# - id: O1
#   name_zh: 包公共 API 面
#   name_en: __all__
#   intro: 包级导出以 __all__ 声明为准
#   downstream: 见头部 [CONSUMERS] 声明
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""
from typing import Final

from zephyr.ex_sor.api.api_rate_limiter import (
    ApiRateLimiter,
    InvalidRateLimitConfigError,
    RateLimitConfig,
    RateLimitDecision,
    RateLimitLevel,
    RequestPriority,
    SlidingWindowCounter,
    TokenBucket,
    TradingSession,
)
from zephyr.ex_sor.api.broker_api_connector import (
    BrokerApiConnector,
    BrokerConnectionError,
    BrokerProtocol,
    BrokerSubmitError,
    BrokerType,
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitBreakerState,
    ConnectionConfig,
    ConnectionState,
    HeartbeatManager,
    HeartbeatTimeoutError,
    RateLimitedError,
    ReconnectPolicy,
    SimulatedProtocol,
)

__all__: Final = [
    # XS-014 Rate Limiter
    "ApiRateLimiter",
    "RateLimitConfig",
    "RateLimitDecision",
    "RateLimitLevel",
    "RequestPriority",
    "SlidingWindowCounter",
    "TokenBucket",
    "TradingSession",
    "InvalidRateLimitConfigError",
    # XS-013 Broker API Connector
    "BrokerApiConnector",
    "BrokerProtocol",
    "BrokerType",
    "ConnectionConfig",
    "ConnectionState",
    "HeartbeatManager",
    "ReconnectPolicy",
    "CircuitBreaker",
    "CircuitBreakerState",
    "SimulatedProtocol",
    "BrokerConnectionError",
    "BrokerSubmitError",
    "CircuitBreakerOpenError",
    "HeartbeatTimeoutError",
    "RateLimitedError",
]
