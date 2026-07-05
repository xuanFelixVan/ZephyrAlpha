# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance.rate_limiter
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
import threading
import time


class RateLimiter:
    """Sliding window 速率限制器，支持 per-key 分桶。

    5.36.4 修复：原 allow(key="default") 接收 key 参数但操作单一 self._requests 列表，
    key 从未用于分桶，API 签名暗示 per-key 隔离但实际所有 key 共享一个 bucket。
    改为 dict[str, list[float]] 按 key 分桶，每个 key 独立计数。

    5.36.5 修复：原列表操作无 threading.Lock 保护，多线程并发调用 allow() 时列表
    读写竞态。增加 threading.Lock 保护所有 _requests 操作。
    """

    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # 5.36.4 修复：按 key 分桶，替代单一 _requests 列表
        self._requests_by_key: dict[str, list[float]] = {}
        # 5.36.5 修复：线程安全锁，保护 _requests_by_key 的读写
        self._lock = threading.Lock()

    def allow(self, key="default"):
        now = time.time()
        with self._lock:
            bucket = self._requests_by_key.get(key)
            if bucket is None:
                bucket = []
                self._requests_by_key[key] = bucket
            # 清理过期时间戳
            bucket[:] = [t for t in bucket if now - t < self.window_seconds]
            if len(bucket) >= self.max_requests:
                return False
            bucket.append(now)
            return True

    def reset(self, key: str | None = None):
        """重置限流器。

        参数：
            key: 指定 key 则仅重置该 key 的桶；None 则清空所有 key。
        """
        with self._lock:
            if key is None:
                self._requests_by_key.clear()
            else:
                self._requests_by_key.pop(key, None)


def create_rate_limiter(config=None):
    config = config or {}
    return RateLimiter(
        max_requests=config.get("max_requests", 100),
        window_seconds=config.get("window_seconds", 60),
    )


RATE_LIMITED_KEY = "rate_limited"


class PerToolRateLimiter:
    def __init__(self, config=None):
        self.config = config or {}
        self._limiters = {}

    def allow(self, tool_name, key="default"):
        if tool_name not in self._limiters:
            self._limiters[tool_name] = RateLimiter(
                max_requests=self.config.get(tool_name, {}).get("max_requests", 100),
                window_seconds=self.config.get(tool_name, {}).get("window_seconds", 60),
            )
        return self._limiters[tool_name].allow(key)

    def reset(self, tool_name=None):
        if tool_name and tool_name in self._limiters:
            self._limiters[tool_name].reset()
        else:
            self._limiters.clear()


class RateLimiterStats:
    def __init__(self, total_requests=0, allowed=0, rejected=0, current_rate=0.0):
        self.total_requests = total_requests
        self.allowed = allowed
        self.rejected = rejected
        self.current_rate = current_rate
