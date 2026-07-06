# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.infra.limiter
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
# [A_module] module_id=MOD-SHR_limiter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Self

"""
limiter.py —— 速率限制器（Phase 8 新增 | 盲点 B14 修复）

痛点修复：LLM API 有 rate limit（如 DeepSeek 500 RPM），AI agent 不知道就会频繁 HTTP 429——
  1. HTTP 429 → 自动重试 → 更频繁 429 → 雪崩
  2. 没有 token bucket / sliding window——只能随机 sleep 碰运气
  3. 速率限制配置散落在各个 agent 代码中——不可审计

设计对标：
  - Google Guava RateLimiter（token bucket + 平滑突发）
  - Stripe API rate-limit headers（X-RateLimit-Remaining / Retry-After）
  - AWS API Gateway throttling（token bucket + 请求配额）

设计原则：
  - Token Bucket 算法——简单、精确、防止突发
  - async-first——asyncio.sleep 不阻塞事件循环
  - 零依赖第三方库——仅 Python 标准库 + asyncio + time

AI 施工约定：
  - 所有 LLM API 调用 MUST 经过 RateLimiter——禁止裸调
  - RateLimiter 配置 SHOULD 从 YAML 或环境变量加载——动态可调

SSoT: MOD-INF-016 §2.13 shared-limiter
Version: 0.1.0
"""


import asyncio
import functools
import logging
import time
from dataclasses import dataclass

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "RateLimitError",
    "RateLimiterStats",
    "TokenBucketLimiter",
    "async_limited",
]

logger = logging.getLogger(__name__)


class RateLimitError(ZephyrBaseError):
    """速率限制耗尽——等待时间过长或无法获取 token。"""
    error_code = "ZA-SH-0043"


@dataclass
class RateLimiterStats:
    permits_per_second: float
    available_tokens: float
    total_acquired: int
    total_rejected: int
    total_waited: int


class TokenBucketLimiter:
    """Token Bucket 速率限制器——平滑突发 + 精确控速。

    Usage::

        limiter = TokenBucketLimiter(permits_per_second=500.0, burst_size=50.0)
        async with limiter.acquire():
            await call_llm_api(...)

        print(limiter.stats())
    """

    def __init__(
        self,
        permits_per_second: float,
        *,
        burst_size: float | None = None,
        max_wait_seconds: float = 30.0,
    ) -> None:
        self._rate = permits_per_second
        self._burst = burst_size or permits_per_second
        self._max_wait = max_wait_seconds
        self._tokens = self._burst
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()
        self._total_acquired = 0
        self._total_rejected = 0
        self._total_waited = 0

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    async def acquire(self) -> None:
        async with self._lock:
            self._refill()

            if self._tokens >= 1.0:
                self._tokens -= 1.0
                self._total_acquired += 1
                return

            wait_time = (1.0 - self._tokens) / self._rate
            self._tokens = 0.0

            if wait_time > self._max_wait:
                self._total_rejected += 1
                raise RateLimitError(
                    f"rate limit exceeded: need {wait_time:.1f}s wait, max {self._max_wait}s",
                    details={
                        "rate": self._rate,
                        "wait_needed_seconds": round(wait_time, 2),
                        "max_wait_seconds": self._max_wait,
                    },
                )

            # 5.100.1 修复: 原代码在持锁期间 release→sleep→acquire, 释放锁期间其他协程
            # 可修改 _tokens/_last_refill, 重新获取后覆盖其修改 (数据丢失).
            # 改为持锁期间 sleep, 简单正确. 并发优化 (条件变量) 属专项工程.
            logger.info("rate limit: waiting %.2fs for token", wait_time)
            await asyncio.sleep(wait_time)

            self._last_refill = time.monotonic()
            self._tokens = 0.0
            self._total_acquired += 1
            self._total_waited += 1

    async def __aenter__(self) -> Self:
        await self.acquire()
        return self

    async def __aexit__(self, *args: object) -> None:
        pass

    def stats(self) -> RateLimiterStats:
        self._refill()
        return RateLimiterStats(
            permits_per_second=self._rate,
            available_tokens=round(self._tokens, 2),
            total_acquired=self._total_acquired,
            total_rejected=self._total_rejected,
            total_waited=self._total_waited,
        )


def async_limited(
    permits_per_second: float,
    *,
    burst_size: float | None = None,
    max_wait_seconds: float = 30.0,
):
    """装饰器：为异步函数自动加上速率限制。

    Usage::

        @async_limited(perms_per_second=500.0)
        async def call_llm(prompt: str) -> str: ...
    """
    limiter = TokenBucketLimiter(
        permits_per_second=permits_per_second,
        burst_size=burst_size,
        max_wait_seconds=max_wait_seconds,
    )

    def decorator(func):
        # 5.78.1 修复：原手动设置 __name__/__qualname__/__doc__，但未设置 __wrapped__、__module__、__annotations__、__dict__。
        # 改为 @functools.wraps(func) 自动设置所有属性。
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with limiter:
                return await func(*args, **kwargs)

        wrapper._limiter = limiter
        return wrapper

    return decorator
