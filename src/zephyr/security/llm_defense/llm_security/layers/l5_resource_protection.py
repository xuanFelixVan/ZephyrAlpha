# [BLUEPRINT] MOD-SECURITY-LLM
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l5_resource_protection
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway; tests.llm_security.test_l5_resource_protection
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
import hashlib
import hmac
import math
import time
from collections import Counter, defaultdict
from enum import Enum
from typing import Any


class ResourceProtectionLayer:
    """L5 资源保护层：token/cost/rate 限额 + 成本不对称检测。"""

    def __init__(
        self,
        config=None,
        max_tokens: int = 100000,
        max_cost_cents: float = 500.0,
        rate_max: int = 100,
        rate_window_seconds: int = 60,
    ):
        self.config = config or {}
        self._max_tokens = max_tokens
        self._max_cost_cents = max_cost_cents
        self._token_usage: dict[str, int] = defaultdict(int)
        self._cost_usage: dict[str, float] = defaultdict(float)
        self._rate_limiter = SlidingWindowRateLimiter(
            max_requests=rate_max, window_seconds=rate_window_seconds
        )
        self._cost_asymmetry = CostAsymmetryDefender()

    def check_token_budget(self, session_id: str, tokens: int) -> tuple[bool, str]:
        if self._token_usage[session_id] + tokens > self._max_tokens:
            return False, f"token budget exhausted for {session_id}"
        self._token_usage[session_id] += tokens
        return True, "ok"

    def check_rate_limit(self, key: str) -> tuple[bool, str]:
        if self._rate_limiter.allow(key):
            return True, "ok"
        return False, "rate limit exceeded"

    def check_cost_budget(self, session_id: str, cost_cents: float) -> tuple[bool, str]:
        if self._cost_usage[session_id] + cost_cents > self._max_cost_cents:
            return False, "cost budget exhausted"
        self._cost_usage[session_id] += cost_cents
        return True, "ok"

    async def evaluate(self, ctx: Any) -> Any:
        """评估资源保护：检测成本不对称攻击。"""
        from zephyr.security.llm_defense.llm_security.protocol import SecurityResult
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        raw = getattr(ctx, "raw_input", "") or ""
        result = self._cost_asymmetry.scan(raw)
        if result.get("blocked"):
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason="cost asymmetry attack detected",
                layer_name="l5_resource_protection",
                score=0.0,
                details=result,
            )
        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="resource budget ok",
            layer_name="l5_resource_protection",
            score=1.0,
        )


class ResourceGuard:
    def __init__(self, resource_id="", quota=0, current_usage=0):
        self.resource_id = resource_id
        self.quota = quota
        self.current_usage = current_usage


class AIRecursionGuard:
    """防止 AI 递归攻击的递归深度守卫。"""

    def __init__(self, config: dict[str, Any] | None = None, max_recursion_depth: int = 10):
        self.config = config or {}
        self._max_depth = max_recursion_depth
        self._stack: list[str] = []

    @property
    def current_depth(self) -> int:
        return len(self._stack)

    def enter(self, agent_id: str) -> bool:
        if len(self._stack) >= self._max_depth:
            return False
        self._stack.append(agent_id)
        return True

    def reset(self) -> None:
        self._stack.clear()

    # 兼容旧接口
    def check_recursion(self, call_stack: list[Any]) -> bool:
        return len(call_stack) < self._max_depth


class AgentExecutionProtector:
    """保护 agent 执行免受资源滥用。"""

    def __init__(self, config: dict[str, Any] | None = None, max_steps: int = 100):
        self.config = config or {}
        self._max_steps = max_steps
        self._steps = 0

    def record_step(self) -> dict[str, Any]:
        self._steps += 1
        exceeded = self._steps > self._max_steps
        return {"allowed": not exceeded, "steps_exceeded": exceeded, "steps": self._steps}

    # 兼容旧接口
    def check_execution_limits(self, agent_id: str) -> bool:
        return self._steps <= self._max_steps


class CircuitState(Enum):
    """断路器状态。"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class LLMCostCircuitBreaker:
    """LLM 成本断路器。"""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 60,
    ):
        self.config = config or {}
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout_seconds
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at: float = 0.0

    @property
    def state(self) -> CircuitState:
        if self._state is CircuitState.OPEN:
            if time.time() - self._opened_at > self._recovery_timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.time()

    def allow_request(self) -> bool:
        return self.state != CircuitState.OPEN

    def reset(self) -> None:
        self._failures = 0
        self._state = CircuitState.CLOSED

    def trip(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = time.time()

    def check(self) -> CircuitState:
        return self.state


class CostAsymmetryDefender:
    """检测成本不对称攻击（少量输入榨取大量情报）。"""

    _FREE_INTELLIGENCE_PATTERNS = [
        "analyze this codebase",
        "review all files",
        "audit the entire",
        "review all",
        "analyze the entire",
        "enumerate all",
        "list every",
    ]

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def scan(self, text: str) -> dict[str, Any]:
        lowered = (text or "").lower()
        flagged = any(p in lowered for p in self._FREE_INTELLIGENCE_PATTERNS)
        return {
            "blocked": flagged,
            "free_intelligence_flagged": flagged,
            "reason": "free intelligence extraction" if flagged else "ok",
        }

    # 兼容旧接口
    def detect_asymmetry(self, request: Any, response: Any) -> bool:
        return self.scan(str(request))["blocked"]

    def calculate_cost_ratio(self, input_tokens: int, output_tokens: int) -> float:
        if input_tokens == 0:
            return float(output_tokens)
        return output_tokens / input_tokens


class _L5CostBudget:
    """内部成本预算追踪器。"""

    def __init__(
        self,
        max_cost: float = 100.0,
        current_cost: float = 0.0,
        *,
        session_id: str = "",
        max_cost_cents: float | None = None,
        current_cost_cents: float | None = None,
    ):
        self.session_id = session_id
        self.max_cost_cents = max_cost_cents if max_cost_cents is not None else max_cost
        self.current_cost_cents = current_cost_cents if current_cost_cents is not None else current_cost

    def exhausted(self) -> bool:
        return self.current_cost_cents >= self.max_cost_cents

    def remaining_cost_cents(self) -> float:
        return max(0.0, self.max_cost_cents - self.current_cost_cents)

    def can_spend(self, amount: float) -> bool:
        return self.current_cost_cents + amount <= self.max_cost_cents

    def spend(self, amount: float) -> None:
        self.current_cost_cents += amount


class _L5TokenBudget:
    """内部 token 预算追踪器。"""

    def __init__(
        self,
        max_tokens: int = 100000,
        current_tokens: int = 0,
        *,
        session_id: str = "",
        current_usage: int | None = None,
    ):
        self.session_id = session_id
        self.max_tokens = max_tokens
        self.current_usage = current_usage if current_usage is not None else current_tokens

    def exhausted(self) -> bool:
        return self.current_usage >= self.max_tokens

    def remaining(self) -> int:
        return max(0, self.max_tokens - self.current_usage)

    def can_consume(self, tokens: int) -> bool:
        return self.current_usage + tokens <= self.max_tokens

    def consume(self, tokens: int) -> None:
        self.current_usage += tokens


class LSGPerformanceBudget:
    """LSG 性能预算追踪器（分位数统计 + SLO 判定）。"""

    def __init__(self, max_tokens: int = 4096, max_time_ms: int = 30000):
        self.max_tokens = max_tokens
        self.max_time_ms = max_time_ms
        self._records: dict[str, list[float]] = defaultdict(list)

    def record(self, layer: str, latency_ms: float) -> None:
        self._records[layer].append(latency_ms)

    def stats(self, layer: str) -> dict[str, Any]:
        recs = self._records.get(layer, [])
        if not recs:
            return {"count": 0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "meets_slo": True}
        srt = sorted(recs)

        def _pct(p: float) -> float:
            idx = min(len(srt) - 1, max(0, int(len(srt) * p)))
            return srt[idx]

        p50, p95, p99 = _pct(0.50), _pct(0.95), _pct(0.99)
        return {
            "count": len(recs),
            "p50": p50,
            "p95": p95,
            "p99": p99,
            "meets_slo": p95 < 50.0 and p99 < 100.0,
        }

    def check_budget(self, tokens_used: int, elapsed_ms: int) -> bool:
        return tokens_used <= self.max_tokens and elapsed_ms <= self.max_time_ms


class ModelExtractionDefender:
    """检测模型提取攻击（高熵查询模式）。"""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        entropy_threshold: float = 4.5,
    ):
        self.config = config or {}
        self._threshold = entropy_threshold

    def entropy_check(self, text: str) -> dict[str, Any]:
        if not text:
            return {"suspicious": False, "entropy": 0.0}
        counts = Counter(text)
        length = len(text)
        entropy = -sum((c / length) * math.log2(c / length) for c in counts.values())
        return {"suspicious": entropy > self._threshold, "entropy": round(entropy, 4)}

    # 兼容旧接口
    def detect_extraction(self, query_pattern: list[Any]) -> bool:
        joined = "".join(str(q) for q in query_pattern)
        return self.entropy_check(joined)["suspicious"]

    def check_query_similarity(self, queries: list[str]) -> float:
        if len(queries) < 2:
            return 0.0
        return 1.0 - _jaccard(set(queries[0].split()), set(queries[-1].split()))


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / max(len(a | b), 1)


class SemanticCacheCollisionDefender:
    """检测语义缓存碰撞攻击（HMAC 签名验证）。"""

    def __init__(self, config: dict[str, Any] | None = None, salt: str = "l5-cache-salt"):
        self.config = config or {}
        self._salt = salt

    def salt_key(self, key: str) -> str:
        return hmac.new(self._salt.encode(), key.encode(), hashlib.sha256).hexdigest()

    def sign_value(self, salted_key: str, value: str) -> str:
        return f"{value}::sig={hmac.new(salted_key.encode(), value.encode(), hashlib.sha256).hexdigest()}"

    def verify_integrity(self, salted_key: str, signed_value: str) -> tuple[bool, str]:
        if "::sig=" not in signed_value:
            return False, ""
        value, _, sig = signed_value.partition("::sig=")
        expected = hmac.new(salted_key.encode(), value.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected), value

    # 兼容旧接口
    def detect_collision(self, cache_key: str, cached_value: Any, new_value: Any) -> bool:
        return cached_value != new_value

    def validate_cache_entry(self, key: str, value: Any) -> bool:
        return True


class SlidingWindowRateLimiter:
    """滑动窗口限流器（per-key 计数）。"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str = "default") -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        bucket = [t for t in self._buckets[key] if t >= cutoff]
        self._buckets[key] = bucket
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True

    def current_count(self, key: str = "default") -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        return sum(1 for t in self._buckets[key] if t >= cutoff)

    # 兼容旧接口
    def allow_request(self) -> bool:
        return self.allow("default")

    def record_request(self, timestamp: float) -> None:
        self._buckets["default"].append(timestamp)
