# [BLUEPRINT] SRC-136 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.reliability.retry_handler
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_retry_handler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Retry Handler — 指数退避重试 + 可恢复/不可恢复错误分类。

依据：
    蓝图 MOD-TASK_SYSTEM §6.2.2 + v0.6.0
    任务卡 TASK-INF-0108 (Part 2/4)

功能：
    - 指数退避：base_delay=1s, max_delay=64s, max_retries=5
    - 可恢复错误（network/timeout）-> 重试
    - 不可恢复错误（ValueError/AssertionError）-> 立即失败
"""

from __future__ import annotations

from typing import Final
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

UNRECOVERABLE_EXCEPTIONS: Final[tuple] = (
    ValueError,
    TypeError,
    AssertionError,
    SyntaxError,
    ImportError,
    AttributeError,
)


@dataclass
class RetryConfig:
    base_delay_s: float = 1.0
    max_delay_s: float = 64.0
    max_retries: int = 5
    backoff_multiplier: float = 2.0
    jitter: bool = True


@dataclass
class RetryAttempt:
    attempt: int
    success: bool
    delay_s: float
    exception: Exception | None = None
    total_time_s: float = 0.0


@dataclass
class RetryResult:
    success: bool
    attempts: list[RetryAttempt]
    total_time_s: float
    final_error: Exception | None = None


class RetryHandler:
    def __init__(self, config: RetryConfig | None = None) -> None:
        self._config = config or RetryConfig()

    def execute(self, func: Callable, *args: Any, **kwargs: Any) -> RetryResult:
        attempts: list[RetryAttempt] = []
        t0 = time.time()

        for i in range(self._config.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                attempts.append(
                    RetryAttempt(
                        attempt=i + 1,
                        success=True,
                        delay_s=time.time() - t0,
                    )
                )
                return RetryResult(
                    success=True,
                    attempts=attempts,
                    total_time_s=time.time() - t0,
                )
            except Exception as e:
                attempts.append(
                    RetryAttempt(
                        attempt=i + 1,
                        success=False,
                        delay_s=time.time() - t0,
                        exception=e,
                    )
                )

                if self._is_unrecoverable(e) or i == self._config.max_retries:
                    return RetryResult(
                        success=False,
                        attempts=attempts,
                        total_time_s=time.time() - t0,
                        final_error=e,
                    )

                delay = min(
                    self._config.base_delay_s * (self._config.backoff_multiplier**i),
                    self._config.max_delay_s,
                )

                if self._config.jitter:
                    import random

                    delay *= 0.5 + random.random()

                time.sleep(delay)

        return RetryResult(success=False, attempts=attempts, total_time_s=time.time() - t0)

    @staticmethod
    def _is_unrecoverable(exc: Exception) -> bool:
        return isinstance(exc, UNRECOVERABLE_EXCEPTIONS)
