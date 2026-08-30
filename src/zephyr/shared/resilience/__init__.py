# [A_module] module_id=MOD-RES-resilience_shared_resilience | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [TTL] permanent
"""
resilience/__init__.py — 韧性工具包入口（Phase 2 新增）

零依赖共享基类——gates/circuit_breaker.py 可选在此基础上叠加 SQLite 持久化 + 门禁集成。

子模块：
  - retry.py            — 重试策略（指数退避 + jitter）
  - circuit_breaker.py  — 熔断器状态机（CLOSED/OPEN/HALF_OPEN，零依赖）
  - fallback.py         — 降级策略模式

SSoT: MOD-INF-016 §2.6 shared-resilience
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: CircuitBreaker, CircuitOpenError, CircuitState, FallbackChain, fallba…
#   code: __init__.py import L44
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 CircuitBreaker, CircuitOpenError, CircuitState, FallbackChain, RetryConfig,…
#   desc: __init__ import L44；__all__ 10 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（10 符号）
#   name_en: __all__
#   intro: CircuitBreaker, CircuitOpenError, CircuitState, FallbackChain, RetryConfig, Ret…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
)
from zephyr.shared.resilience.fallback import FallbackChain, fallback
from zephyr.shared.resilience.retry import (
    RetryConfig,
    RetryExhaustedError,
    async_retry,
)

__all__ = [
    "CircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "FallbackChain",
    "RetryConfig",
    "RetryExhaustedError",
    "async_retry",
    "circuit_breaker",
    "fallback",
    "retry",
]
