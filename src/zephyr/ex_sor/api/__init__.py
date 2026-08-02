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
# [A_module] module_id=MOD-EX_SOR_api | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ex_sor/api — 券商API层 (限速器/连接器)

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
