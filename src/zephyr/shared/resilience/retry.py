# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.resilience.retry
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
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
# [A_module] module_id=MOD-RES_retry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
retry.py —— 统一重试策略（Phase 2 新增 | 零依赖）

对标：tenacity 库的 API 设计，但仅依赖 Python 标准库 + logging。

设计原则：
  - 指数退避 + 全 jitter（AWS 推荐方案，避免惊群效应）
  - 白名单/黑名单异常——只重试 transient 错误，永久失败立即抛出
  - async 优先——项目主体是异步架构

AI 施工约定：
  - LLM API 调用 / 文件 I/O / 网络操作 MUST 使用本模块重试
  - 禁止裸 while True + time.sleep——那是反模式
  - 每个 retry 调用点 MUST 在参数中注明 retryable_exceptions

SSoT: MOD-INF-016 §2.6 shared-resilience
Version: 0.1.0
"""

from __future__ import annotations

import asyncio
import functools
import logging
import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Concatenate, ParamSpec, TypeVar

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "RetryConfig",
    "RetryExhaustedError",
    "async_retry",
]

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


class RetryExhaustedError(ZephyrBaseError):
    """所有重试均已耗尽——最后一次异常通过 __cause__ 链保留。"""
    error_code = "ZA-SH-0018"


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    backoff_multiplier: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,)
    non_retryable_exceptions: tuple[type[Exception], ...] = ()

    def delay_for_attempt(self, attempt: int) -> float:
        raw = min(
            self.base_delay_seconds * (self.backoff_multiplier**attempt),
            self.max_delay_seconds,
        )
        if self.jitter:
            raw = random.uniform(0, raw)
        return raw

    def should_retry(self, exc: Exception) -> bool:
        if isinstance(exc, self.non_retryable_exceptions):
            return False
        if self.retryable_exceptions == (Exception,):
            return True
        return isinstance(exc, self.retryable_exceptions)


def async_retry(
    config: RetryConfig | None = None,
    *,
    max_attempts: int | None = None,
    base_delay_seconds: float | None = None,
    max_delay_seconds: float | None = None,
    retryable_exceptions: tuple[type[Exception], ...] | None = None,
    non_retryable_exceptions: tuple[type[Exception], ...] | None = None,
) -> Callable[[Callable[Concatenate[Any, P], R]], Callable[P, R]]:
    """异步重试装饰器——指数退避 + jitter。

    Example::

        @async_retry(max_attempts=3, retryable_exceptions=(aiohttp.ClientError,))
        async def fetch_url(url: str) -> dict: ...

    Args:
        config: 预置 RetryConfig（优先级高于 kwargs）。
        max_attempts: 最大重试次数（含首次调用）。
        base_delay_seconds: 首次退避延迟秒数。
        max_delay_seconds: 最大延迟上限。
        retryable_exceptions: 可重试的异常白名单。
        non_retryable_exceptions: 不可重试的异常黑名单（优先级高于白名单）。
    """

    _cfg = config or RetryConfig(
        max_attempts=max_attempts or 3,
        base_delay_seconds=base_delay_seconds or 1.0,
        max_delay_seconds=max_delay_seconds or 60.0,
        retryable_exceptions=retryable_exceptions or (Exception,),
        non_retryable_exceptions=non_retryable_exceptions or (),
    )

    def decorator(func: Callable[Concatenate[Any, P], R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: Exception | None = None
            for attempt in range(_cfg.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if not _cfg.should_retry(exc):
                        raise
                    if attempt == _cfg.max_attempts - 1:
                        break
                    delay = _cfg.delay_for_attempt(attempt)
                    logger.warning(
                        "retry attempt %d/%d for %s after %.1fs: %s",
                        attempt + 1,
                        _cfg.max_attempts,
                        func.__qualname__,
                        delay,
                        exc,
                    )
                    await asyncio.sleep(delay)

            raise RetryExhaustedError(
                f"{func.__qualname__} failed after {_cfg.max_attempts} attempts",
                details={
                    "max_attempts": _cfg.max_attempts,
                    "last_error": str(last_exc),
                },
            ) from last_exc

        return wrapper

    return decorator
