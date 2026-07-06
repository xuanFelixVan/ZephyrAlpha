# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] zephyr.integration.mcp.rate_limiter
# [DOMAIN] D_INTEGRATION
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
# [A_module] module_id=MOD-INT_rate_limiter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MCP Gateway 同步速率限制器（MOD-INF-013 §12 Step 3）。

设计基线：
- 自包含 sync TokenBucket——不依赖 shared/limiter.py 的 asyncio 实现
- Token Bucket 算法 + 线程安全（threading.Lock）
- 按 tool_name 粒度独立 bucket（对标 R98）
- 可配置：10 req/s default, 30 burst（从 config/mcp.json 加载）

盲点关闭：B10（缺限流 → 无 DoS 防护）。
"""

from __future__ import annotations

from typing import Final
import threading
import time
from dataclasses import dataclass

__all__ = [
    "DEFAULT_BURST",
    "DEFAULT_MAX_WAIT",
    "DEFAULT_QPS",
    "RATE_LIMITED_KEY",
    "RateLimiter",
    "RateLimiterStats",
]

RATE_LIMITED_KEY: Final[str] = "RATE_LIMITED"
DEFAULT_QPS: Final[float] = 10.0
DEFAULT_BURST: Final[float] = 30.0
DEFAULT_MAX_WAIT: Final[float] = 30.0


@dataclass
class RateLimiterStats:
    permits_per_second: float
    available_tokens: float
    total_acquired: int = 0
    total_rejected: int = 0
    total_waited: int = 0


class RateLimiter:
    """同步 Token Bucket 速率限制器。

    Usage::

        rl = RateLimiter(permits_per_second=10.0, burst_size=30.0)
        if not rl.try_acquire():
            raise RateLimitExceeded("rate limited")
    """

    def __init__(
        self,
        permits_per_second: float = DEFAULT_QPS,
        *,
        burst_size: float | None = None,
        max_wait_seconds: float = DEFAULT_MAX_WAIT,
    ) -> None:
        self._rate = permits_per_second
        self._burst = burst_size or permits_per_second
        self._max_wait = max_wait_seconds
        self._tokens = self._burst
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()
        self._acquired = 0
        self._rejected = 0
        self._waited = 0

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    def try_acquire(self) -> bool:
        """尝试获取 1 token。True=获取成功，False=被限流。"""
        with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                self._acquired += 1
                return True
            self._rejected += 1
            return False

    def acquire(self, timeout: float | None = None) -> bool:
        """获取 1 token，可选等待。True=获取成功；False=超时/被拒。"""
        deadline = time.monotonic() + (timeout or self._max_wait)
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    self._acquired += 1
                    return True

                wait_time = (1.0 - self._tokens) / self._rate
                # 5.16.13 修复：_waited 自增移入锁内，避免并发 lost update
                self._waited += 1

            if time.monotonic() + wait_time > min(deadline, time.monotonic() + self._max_wait):
                with self._lock:
                    self._rejected += 1
                return False

            time.sleep(min(wait_time, 0.1))

    def stats(self) -> RateLimiterStats:
        with self._lock:
            self._refill()
            return RateLimiterStats(
                permits_per_second=self._rate,
                available_tokens=round(self._tokens, 2),
                total_acquired=self._acquired,
                total_rejected=self._rejected,
                total_waited=self._waited,
            )


class RateLimitExceeded(Exception):
    """速率限制超出。"""


class PerToolRateLimiter:
    """按 tool_name 粒度管理多个 TokenBucket。

    5.36.9 修复：原 docstring 误写为 "默认 10QPS per client"，但 try_acquire(tool_name)
    实际按 tool_name 分桶（key = tool_name），无 client 维度。修正为 per-tool 描述，
    避免安全审计/容量规划基于错误假设。若需 per-client 限流需引入 client_id 维度
    （参见 5.36.2，待后续重构）。

    默认 10QPS per tool；可在 config/mcp.json 覆盖。
    """

    def __init__(self, default_qps: float = DEFAULT_QPS, default_burst: float = DEFAULT_BURST) -> None:
        self._default_qps = default_qps
        self._default_burst = default_burst
        self._buckets: dict[str, RateLimiter] = {}
        self._lock = threading.Lock()

    def get_or_create(self, tool_name: str, qps: float | None = None, burst: float | None = None) -> RateLimiter:
        key = tool_name
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = RateLimiter(
                    qps or self._default_qps,
                    burst_size=burst or self._default_burst,
                )
            return self._buckets[key]

    def try_acquire(self, tool_name: str) -> bool:
        return self.get_or_create(tool_name).try_acquire()

    def stats(self) -> dict[str, RateLimiterStats]:
        with self._lock:
            return {k: v.stats() for k, v in self._buckets.items()}
