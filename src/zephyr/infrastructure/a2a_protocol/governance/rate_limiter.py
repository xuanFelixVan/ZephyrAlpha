# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infra_ops/a2a_protocol/blueprint.md
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
# [TTL] task_bound
import time


class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = []

    def allow(self, key="default"):
        now = time.time()
        self._requests = [t for t in self._requests if now - t < self.window_seconds]
        if len(self._requests) >= self.max_requests:
            return False
        self._requests.append(now)
        return True

    def reset(self):
        self._requests = []


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
