# [BLUEPRINT] MOD-INF-014 | 03_modules/_cross_layer/llm-security/blueprint.md | §

# [MODULE] zephyr.llm_security.layers.l5_resource_protection

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

import hashlib
import hmac
import math
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from zephyr.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class _L5CostBudget(BaseModel):
    session_id: str
    max_tokens: int = 100000
    max_cost_cents: float = 500.0
    current_tokens: int = 0
    current_cost_cents: float = 0.0
    limit: str = "session"

    def remaining_tokens(self) -> int:
        return max(0, self.max_tokens - self.current_tokens)

    def remaining_cost_cents(self) -> float:
        return max(0.0, self.max_cost_cents - self.current_cost_cents)

    def exhausted(self) -> bool:
        return self.current_tokens >= self.max_tokens or self.current_cost_cents >= self.max_cost_cents


CostBudget = _L5CostBudget


class _L5TokenBudget(BaseModel):
    session_id: str
    max_tokens: int = 100000
    current_usage: int = 0
    limit: str = "session"

    def remaining(self) -> int:
        return max(0, self.max_tokens - self.current_usage)

    def exhausted(self) -> bool:
        return self.current_usage >= self.max_tokens


TokenBudget = _L5TokenBudget


class SlidingWindowRateLimiter:
    """滑动窗口速率限制器 — N=100, W=60s."""

    def __init__(self, max_requests: int = 100, window_seconds: float = 60.0):
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._lock = threading.Lock()
        self._windows: Dict[str, deque] = defaultdict(deque)

    def allow(self, key: str = "default") -> bool:
        now = time.monotonic()
        with self._lock:
            w = self._windows[key]
            while w and now - w[0] > self._window_seconds:
                w.popleft()
            if len(w) < self._max_requests:
                w.append(now)
                return True
            return False

    def current_count(self, key: str = "default") -> int:
        now = time.monotonic()
        with self._lock:
            w = self._windows[key]
            while w and now - w[0] > self._window_seconds:
                w.popleft()
            return len(w)

    def reset(self, key: str = "default") -> None:
        with self._lock:
            self._windows.pop(key, None)


class LLMCostCircuitBreaker:
    """LLM成本熔断器 — 三级熔断状态."""

    def __init__(
        self,
        budget_threshold_cents: float = 500.0,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
    ):
        self._budget_threshold_cents = budget_threshold_cents
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout_seconds
        self._state = CircuitState.CLOSED
        self._failure_count: int = 0
        self._total_cost_cents: float = 0.0
        self._last_failure_time: float = 0.0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        return self._state

    def record_success(self, cost_cents: float = 0.0) -> None:
        with self._lock:
            self._total_cost_cents += cost_cents
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._failure_count = 0

    def record_failure(self, cost_cents: float = 0.0) -> None:
        with self._lock:
            self._failure_count += 1
            self._total_cost_cents += cost_cents
            self._last_failure_time = time.time()
            if self._failure_count >= self._failure_threshold:
                self._state = CircuitState.OPEN
            elif self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN

    def allow_request(self, estimated_cost_cents: float = 0.0) -> bool:
        with self._lock:
            if self._budget_threshold_cents > 0 and (
                self._total_cost_cents + estimated_cost_cents > self._budget_threshold_cents
            ):
                return False
            if self._state == CircuitState.CLOSED:
                return True
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time >= self._recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    return True
                return False
            return True

    def reset(self) -> None:
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._total_cost_cents = 0.0
            self._last_failure_time = 0.0


class AIRecursionGuard:
    """AI递归执行保护 — 深度限制 + 循环检测."""

    def __init__(
        self,
        max_recursion_depth: int = 10,
        max_cycle_length: int = 5,
    ):
        self._max_recursion_depth = max_recursion_depth
        self._max_cycle_length = max_cycle_length
        self._call_stack: List[str] = []
        self._seen_hashes: Dict[int, List[int]] = defaultdict(list)

    def enter(self, func_name: str) -> bool:
        self._call_stack.append(func_name)
        if len(self._call_stack) > self._max_recursion_depth:
            self._call_stack.pop()
            return False

        key = hash(func_name)
        positions = self._seen_hashes[key]
        positions.append(len(self._call_stack) - 1)
        if len(positions) >= self._max_cycle_length:
            recent = positions[-self._max_cycle_length:]
            if len(recent) >= 2 and all(
                self._call_stack[recent[i]] == self._call_stack[recent[0]]
                for i in range(len(recent))
            ):
                return False
        return True

    def leave(self, func_name: str) -> None:
        if self._call_stack and self._call_stack[-1] == func_name:
            self._call_stack.pop()

    @property
    def current_depth(self) -> int:
        return len(self._call_stack)

    def reset(self) -> None:
        self._call_stack.clear()
        self._seen_hashes.clear()


class AgentExecutionProtector:
    """Agent执行保护 — max_steps / max_wall_time / max_memory_mb."""

    def __init__(
        self,
        max_steps: int = 100,
        max_wall_time_seconds: float = 600.0,
        max_memory_mb: float = 512.0,
    ):
        self._max_steps = max_steps
        self._max_wall_time = max_wall_time_seconds
        self._max_memory_mb = max_memory_mb
        self._step_count: int = 0
        self._start_time: float = time.time()
        self._lock = threading.Lock()

    def record_step(self) -> Dict[str, Any]:
        with self._lock:
            self._step_count += 1
            elapsed = time.time() - self._start_time
            steps_exceeded = self._step_count > self._max_steps
            time_exceeded = elapsed > self._max_wall_time

            return {
                "allowed": not steps_exceeded and not time_exceeded,
                "steps": self._step_count,
                "max_steps": self._max_steps,
                "elapsed_seconds": round(elapsed, 2),
                "max_wall_time_seconds": self._max_wall_time,
                "steps_exceeded": steps_exceeded,
                "time_exceeded": time_exceeded,
                "max_memory_mb": self._max_memory_mb,
            }

    def reset(self) -> None:
        with self._lock:
            self._step_count = 0
            self._start_time = time.time()


class LSGPerformanceBudget:
    """LSG 自身性能 SLO — P50<10ms/P95<50ms/P99<100ms."""

    def __init__(self):
        self._latencies: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def record(self, layer_name: str, latency_ms: float) -> None:
        with self._lock:
            self._latencies[layer_name].append(latency_ms)
            if len(self._latencies[layer_name]) > 10000:
                self._latencies[layer_name] = self._latencies[layer_name][-5000:]

    def stats(self, layer_name: str) -> Dict[str, Any]:
        with self._lock:
            vals = sorted(self._latencies.get(layer_name, []))
            if not vals:
                return {"count": 0, "p50": 0.0, "p95": 0.0, "p99": 0.0}

            count = len(vals)
            p50 = vals[int(count * 0.50)]
            p95 = vals[min(count - 1, int(count * 0.95))]
            p99 = vals[min(count - 1, int(count * 0.99))]

            meets_slo = p50 < 10.0 and p95 < 50.0 and p99 < 100.0
            return {
                "count": count,
                "p50": round(p50, 3),
                "p95": round(p95, 3),
                "p99": round(p99, 3),
                "meets_slo": meets_slo,
            }

    def meets_slo(self, layer_name: str) -> bool:
        s = self.stats(layer_name)
        if s["count"] == 0:
            return True
        return s["p50"] < 10.0 and s["p95"] < 50.0 and s["p99"] < 100.0


class ModelExtractionDefender:
    """模型提取防御 — 熵检查 + 输出扰动 + MVI 策略."""

    def __init__(self, entropy_threshold: float = 4.5, perturbation_rate: float = 0.05):
        self._entropy_threshold = entropy_threshold
        self._perturbation_rate = perturbation_rate

    def entropy_check(self, text: str) -> Dict[str, Any]:
        if not text:
            return {"entropy": 0.0, "suspicious": False}
        freq: Dict[str, int] = {}
        for ch in text:
            freq[ch] = freq.get(ch, 0) + 1
        total = len(text)
        entropy = 0.0
        for count in freq.values():
            p = count / total
            entropy -= p * math.log2(p)
        suspicious = entropy > self._entropy_threshold
        return {
            "entropy": round(entropy, 3),
            "suspicious": suspicious,
            "threshold": self._entropy_threshold,
        }

    def apply_perturbation(self, text: str) -> str:
        import random

        result: List[str] = []
        for ch in text:
            if random.random() < self._perturbation_rate and ch.isalpha():
                offset = random.choice([-1, 1])
                shifted = chr(ord(ch) + offset)
                if shifted.isalpha():
                    result.append(shifted)
                    continue
            result.append(ch)
        return "".join(result)

    def mvi_strategy(self, text: str) -> Dict[str, Any]:
        """Minimum Viable IP protection — 最低 IP 保护方案."""
        entropy = self.entropy_check(text)
        if entropy["suspicious"]:
            return {
                "action": "perturb",
                "reason": "high entropy suggests model extraction attempt",
                "perturbed": self.apply_perturbation(text),
            }
        return {"action": "pass", "reason": "entropy within normal range"}


class CostAsymmetryDefender:
    """成本不对称攻击防御."""

    _FREE_INTELLIGENCE_PATTERNS: List[str] = [
        "analyze this codebase",
        "review all files",
        "audit the entire project",
        "find all bugs",
        "scan everything",
        "summarize every file",
        "catalog all functions",
    ]

    _EVALUATION_PATTERNS: List[str] = [
        "evaluate my model",
        "rate this response",
        "compare these outputs",
        "benchmark this",
        "score this",
    ]

    _REFLECTIVE_PATTERNS: List[str] = [
        "what are your limitations",
        "how were you trained",
        "what is your architecture",
        "describe your training data",
        "what is your prompt",
        "how do you work internally",
    ]

    def scan(self, prompt: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        free_intel_hits = [
            p for p in self._FREE_INTELLIGENCE_PATTERNS if p in prompt_lower
        ]
        eval_hits = [p for p in self._EVALUATION_PATTERNS if p in prompt_lower]
        reflective_hits = [
            p for p in self._REFLECTIVE_PATTERNS if p in prompt_lower
        ]

        blocked = bool(free_intel_hits) or bool(eval_hits) or len(reflective_hits) >= 2
        return {
            "blocked": blocked,
            "free_intelligence_flagged": bool(free_intel_hits),
            "evaluation_flagged": bool(eval_hits),
            "reflective_flagged": len(reflective_hits) >= 2,
            "hits": {
                "free_intelligence": free_intel_hits,
                "evaluation": eval_hits,
                "reflective": reflective_hits,
            },
        }


class SemanticCacheCollisionDefender:
    """语义缓存键冲突防御 — Key Salting + HMAC."""

    def __init__(self, salt: Optional[bytes] = None, hmac_key: Optional[bytes] = None):
        self._salt = salt or hashlib.sha256(
            f"cache-salt-{time.time()}-{id(self)}".encode()
        ).digest()
        self._hmac_key = hmac_key or hashlib.sha256(
            f"cache-hmac-{time.time()}-{id(self)}".encode()
        ).digest()

    def salt_key(self, original_key: str) -> str:
        salted = f"{original_key}:{self._salt.hex()[:16]}"
        return hashlib.sha256(salted.encode()).hexdigest()

    def sign_value(self, salted_key: str, value: str) -> str:
        sig = hmac.new(
            self._hmac_key,
            f"{salted_key}:{value}".encode(),
            hashlib.sha256,
        ).hexdigest()[:16]
        return f"{value}|sig={sig}"

    def verify_integrity(self, salted_key: str, signed_value: str) -> Tuple[bool, str]:
        if "|sig=" not in signed_value:
            return False, ""
        value_part, sig_part = signed_value.rsplit("|sig=", 1)
        expected_sig = hmac.new(
            self._hmac_key,
            f"{salted_key}:{value_part}".encode(),
            hashlib.sha256,
        ).hexdigest()[:16]
        if not hmac.compare_digest(expected_sig, sig_part):
            return False, value_part
        return True, value_part


class ResourceProtectionLayer(LLMSecurityProtocol):
    """L5 资源保护层 —— Token+速率+成本+递归+Agent保护+性能+模型提取+成本不对称+缓存.

    SSoT: MOD-INF-024 (budget_enforcer) 为预算执行真源。
    本层保留本地简化追踪作为 fail-closed 安全网。
    当 budget_engine 可用时，委托其 pre_flight_check 做预算决策。
    """

    def __init__(
        self,
        max_tokens: int = 100000,
        max_cost_cents: float = 500.0,
        rate_max: int = 100,
        rate_window: float = 60.0,
        max_recursion_depth: int = 10,
        agent_max_steps: int = 100,
        agent_max_wall_time: float = 600.0,
        agent_max_memory_mb: float = 512.0,
        budget_engine: Any = None,
    ):
        self._token_budgets: Dict[str, _L5TokenBudget] = {}
        self._cost_budgets: Dict[str, _L5CostBudget] = {}
        self._rate_limiter = SlidingWindowRateLimiter(
            max_requests=rate_max, window_seconds=rate_window
        )
        self._circuit_breaker = LLMCostCircuitBreaker(
            budget_threshold_cents=max_cost_cents
        )
        self._recursion_guard = AIRecursionGuard(
            max_recursion_depth=max_recursion_depth
        )
        self._agent_protector = AgentExecutionProtector(
            max_steps=agent_max_steps,
            max_wall_time_seconds=agent_max_wall_time,
            max_memory_mb=agent_max_memory_mb,
        )
        self._perf_budget = LSGPerformanceBudget()
        self._extraction_defender = ModelExtractionDefender()
        self._cost_asymmetry_defender = CostAsymmetryDefender()
        self._cache_defender = SemanticCacheCollisionDefender()
        self._default_max_tokens = max_tokens
        self._default_max_cost = max_cost_cents
        self._budget_engine = budget_engine

    def layer_name(self) -> str:
        return "l5_resource_protection"

    def layer_index(self) -> int:
        return 5

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        session_id = ctx.metadata.get("session_id", "default")
        task = ctx.metadata.get("task", ctx.raw_input[:200])
        estimated_cost = ctx.metadata.get("estimated_cost_cents", 0.0)

        t0 = time.perf_counter()

        token_ok, token_msg = self.check_token_budget(
            session_id, ctx.metadata.get("token_estimate", 100)
        )
        if not token_ok:
            return self._deny(token_msg)

        rate_ok, rate_msg = self.check_rate_limit(session_id)
        if not rate_ok:
            return self._deny(rate_msg)

        cost_ok, cost_msg = self.check_cost_budget(
            session_id, estimated_cost
        )
        if not cost_ok:
            return self._deny(cost_msg)

        agent_ok, agent_msg = self.enforce_agent_limits()
        if not agent_ok:
            return self._deny(agent_msg)

        cost_asym = self._cost_asymmetry_defender.scan(ctx.raw_input)
        if cost_asym["blocked"]:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason="Cost asymmetry attack detected",
                layer_name=self.layer_name(),
                score=0.0,
                details={"cost_asymmetry": cost_asym},
            )

        extraction = self._extraction_defender.entropy_check(ctx.raw_input)
        if extraction["suspicious"]:
            return SecurityResult(
                decision=SecurityDecision.FLAG,
                reason="Model extraction attempt suspected — high entropy",
                layer_name=self.layer_name(),
                score=0.3,
                details={"extraction": extraction},
            )

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self.record_usage(session_id, {"elapsed_ms": elapsed_ms, "task": task})

        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="Resource budget OK",
            layer_name=self.layer_name(),
            score=0.9,
            details={
                "session_id": session_id,
                "elapsed_ms": round(elapsed_ms, 3),
            },
        )

    def _deny(self, reason: str) -> SecurityResult:
        return SecurityResult(
            decision=SecurityDecision.DENY,
            reason=reason,
            layer_name=self.layer_name(),
            score=0.0,
        )

    def check_token_budget(
        self, session_id: str, estimated_tokens: int
    ) -> Tuple[bool, str]:
        if session_id not in self._token_budgets:
            self._token_budgets[session_id] = _L5TokenBudget(
                session_id=session_id,
                max_tokens=self._default_max_tokens,
            )
        budget = self._token_budgets[session_id]
        if budget.current_usage + estimated_tokens > budget.max_tokens:
            return False, f"Token budget exhausted for session {session_id}"
        budget.current_usage += estimated_tokens
        return True, "ok"

    def check_rate_limit(self, key: str) -> Tuple[bool, str]:
        allowed = self._rate_limiter.allow(key)
        if allowed:
            return True, "ok"
        return False, f"Rate limit exceeded for {key}"

    def check_cost_budget(
        self, session_id: str, estimated_cost_cents: float
    ) -> Tuple[bool, str]:
        if self._budget_engine is not None:
            try:
                estimated_cost_usd = estimated_cost_cents / 100.0
                gate_result = self._budget_engine.pre_flight_check(
                    f"l5:{session_id}", 0, estimated_cost_usd
                )
                if gate_result.decision.name not in ("ALLOW", "NARROW"):
                    return False, f"BudgetEngine denied: {gate_result.reason}"
            except Exception:
                pass

        if session_id not in self._cost_budgets:
            self._cost_budgets[session_id] = _L5CostBudget(
                session_id=session_id,
                max_cost_cents=self._default_max_cost,
            )
        budget = self._cost_budgets[session_id]

        if not self._circuit_breaker.allow_request(estimated_cost_cents):
            return False, f"Circuit breaker blocked. State={self._circuit_breaker.state.value}"

        if budget.current_cost_cents + estimated_cost_cents > budget.max_cost_cents:
            self._circuit_breaker.record_failure(estimated_cost_cents)
            return False, f"Cost budget exhausted for {session_id}"

        budget.current_cost_cents += estimated_cost_cents
        self._circuit_breaker.record_success(estimated_cost_cents)
        return True, "ok"

    def enforce_agent_limits(self) -> Tuple[bool, str]:
        status = self._agent_protector.record_step()
        if status["steps_exceeded"]:
            return False, f"Agent step limit exceeded: {status['steps']}/{status['max_steps']}"
        if status["time_exceeded"]:
            return False, f"Agent wall time exceeded: {status['elapsed_seconds']:.1f}s/{status['max_wall_time_seconds']}s"
        return True, "ok"

    def record_usage(
        self, session_id: str, details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        d = details or {}
        self._perf_budget.record(
            self.layer_name(), d.get("elapsed_ms", 0.0)
        )
        return {"session_id": session_id, "recorded": True}

    @property
    def rate_limiter(self) -> SlidingWindowRateLimiter:
        return self._rate_limiter

    @property
    def circuit_breaker(self) -> LLMCostCircuitBreaker:
        return self._circuit_breaker

    @property
    def recursion_guard(self) -> AIRecursionGuard:
        return self._recursion_guard

    @property
    def agent_protector(self) -> AgentExecutionProtector:
        return self._agent_protector

    @property
    def perf_budget(self) -> LSGPerformanceBudget:
        return self._perf_budget

    @property
    def extraction_defender(self) -> ModelExtractionDefender:
        return self._extraction_defender

    @property
    def cache_defender(self) -> SemanticCacheCollisionDefender:
        return self._cache_defender

    def get_token_budget(self, session_id: str) -> _L5TokenBudget:
        if session_id not in self._token_budgets:
            self._token_budgets[session_id] = _L5TokenBudget(
                session_id=session_id, max_tokens=self._default_max_tokens
            )
        return self._token_budgets[session_id]

    def get_cost_budget(self, session_id: str) -> _L5CostBudget:
        if session_id not in self._cost_budgets:
            self._cost_budgets[session_id] = _L5CostBudget(
                session_id=session_id, max_cost_cents=self._default_max_cost
            )
        return self._cost_budgets[session_id]

    def reset_all(self) -> None:
        self._token_budgets.clear()
        self._cost_budgets.clear()
        self._circuit_breaker.reset()
        self._recursion_guard.reset()
        self._agent_protector.reset()
