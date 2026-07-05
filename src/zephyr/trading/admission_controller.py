# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §17
# [MODULE] zephyr.trading.admission_controller
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] zephyr.trading.verdict_engine;MOD-INF-027(audit-orchestrator)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] TokenBucket全局桶50/s burst=100不可绕过；熔断器failure_threshold触发后所有请求CIRCUIT_OPEN
# [MODIFY-GUARD] docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md;src/zephyr/behavioral-admission/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] admit: RateLimited→retry_after_ms; admit: CircuitOpen→retry_after_cb_recovery
# [TESTS] tests/test_behavioral_audit/test_admission_controller.py
# [A_module] module_id=MOD-ORC_admission_controller | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import threading
import time
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class AdmissionDecision(str, Enum):
    ADMIT = "ADMIT"
    RATE_LIMITED = "RATE_LIMITED"
    CIRCUIT_OPEN = "CIRCUIT_OPEN"
    REJECTED = "REJECTED"


class EventTypeBudget(str, Enum):
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    GATE_OPERATION = "gate_operation"
    RBAC_DECISION = "rbac_decision"
    API_CALL = "api_call"
    SESSION = "session"
    DEFAULT = "default"


class TokenBucketConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rate: float = 50.0
    burst: float = 100.0


class PerTypeBucketConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_write: TokenBucketConfig = Field(default_factory=lambda: TokenBucketConfig(rate=20.0, burst=40.0))
    file_delete: TokenBucketConfig = Field(default_factory=lambda: TokenBucketConfig(rate=5.0, burst=10.0))
    gate_operation: TokenBucketConfig = Field(default_factory=lambda: TokenBucketConfig(rate=30.0, burst=60.0))
    rbac_decision: TokenBucketConfig = Field(default_factory=lambda: TokenBucketConfig(rate=50.0, burst=100.0))
    api_call: TokenBucketConfig = Field(default_factory=lambda: TokenBucketConfig(rate=10.0, burst=20.0))
    session: TokenBucketConfig = Field(default_factory=lambda: TokenBucketConfig(rate=15.0, burst=30.0))
    default: TokenBucketConfig = Field(default_factory=lambda: TokenBucketConfig(rate=25.0, burst=50.0))


class AdmissionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: AdmissionDecision = AdmissionDecision.ADMIT
    event_type: str = ""
    retry_after_ms: int = 0
    remaining_tokens: float = 0.0
    circuit_open: bool = False


class AdmissionMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_requests: int = 0
    admitted: int = 0
    rate_limited: int = 0
    circuit_open: int = 0
    rejected: int = 0
    global_tokens_remaining: float = 0.0
    circuit_breaker_state: str = "closed"
    last_admit_time: float = 0.0


class _TokenBucket:
    __slots__ = ("_burst", "_last_refill", "_lock", "_rate", "_tokens")

    def __init__(self, rate: float, burst: float) -> None:
        self._rate = rate
        self._burst = burst
        self._tokens = burst
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def consume(self, tokens: float = 1.0) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    @property
    def tokens(self) -> float:
        # 5.91.1 修复: getter不调用_refill()修改状态,返回近似值(不推进_last_refill)
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            return min(self._burst, self._tokens + elapsed * self._rate)

    def update_rate(self, new_rate: float, new_burst: float | None = None) -> None:
        with self._lock:
            self._rate = new_rate
            if new_burst is not None:
                self._burst = new_burst
                self._tokens = min(self._tokens, self._burst)


class _CircuitBreaker:
    _STATE_CLOSED = "closed"
    _STATE_OPEN = "open"
    _STATE_HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int = 50,
        recovery_timeout_s: float = 30.0,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout_s = recovery_timeout_s
        self._failure_count: int = 0
        self._state = self._STATE_CLOSED
        self._last_failure_time: float = 0.0
        self._lock = threading.Lock()

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._failure_count >= self._failure_threshold:
                self._state = self._STATE_OPEN

    def record_success(self) -> None:
        with self._lock:
            if self._state == self._STATE_HALF_OPEN:
                self._state = self._STATE_CLOSED
                self._failure_count = 0

    def is_open(self) -> bool:
        with self._lock:
            if self._state == self._STATE_OPEN:
                elapsed = time.monotonic() - self._last_failure_time
                if elapsed >= self._recovery_timeout_s:
                    self._state = self._STATE_HALF_OPEN
                    return False
                return True
            return False

    @property
    def state(self) -> str:
        # 5.91.2 修复: getter仅返回当前状态,不触发OPEN→HALF_OPEN转换
        # 转换逻辑已由_should_block()在行为方法中执行
        with self._lock:
            return self._state

    def reset(self) -> None:
        with self._lock:
            self._state = self._STATE_CLOSED
            self._failure_count = 0

    @property
    def retry_after_ms(self) -> int:
        with self._lock:
            if self._state != self._STATE_OPEN:
                return 0
            remaining = self._recovery_timeout_s - (time.monotonic() - self._last_failure_time)
            return max(0, int(remaining * 1000))


_DEFAULT_GLOBAL_CONFIG = TokenBucketConfig(rate=50.0, burst=100.0)
_DEFAULT_PER_TYPE_CONFIG = PerTypeBucketConfig()


class AdmissionController:
    def __init__(
        self,
        global_config: TokenBucketConfig | None = None,
        per_type_config: PerTypeBucketConfig | None = None,
        enable_circuit_breaker: bool = True,
        cb_failure_threshold: int = 50,
        cb_recovery_timeout_s: float = 30.0,
    ) -> None:
        self._global_bucket = _TokenBucket(
            rate=(global_config or _DEFAULT_GLOBAL_CONFIG).rate,
            burst=(global_config or _DEFAULT_GLOBAL_CONFIG).burst,
        )
        ptc = per_type_config or _DEFAULT_PER_TYPE_CONFIG
        self._type_buckets: dict[str, _TokenBucket] = {
            EventTypeBudget.FILE_WRITE.value: _TokenBucket(ptc.file_write.rate, ptc.file_write.burst),
            EventTypeBudget.FILE_DELETE.value: _TokenBucket(ptc.file_delete.rate, ptc.file_delete.burst),
            EventTypeBudget.GATE_OPERATION.value: _TokenBucket(ptc.gate_operation.rate, ptc.gate_operation.burst),
            EventTypeBudget.RBAC_DECISION.value: _TokenBucket(ptc.rbac_decision.rate, ptc.rbac_decision.burst),
            EventTypeBudget.API_CALL.value: _TokenBucket(ptc.api_call.rate, ptc.api_call.burst),
            EventTypeBudget.SESSION.value: _TokenBucket(ptc.session.rate, ptc.session.burst),
            EventTypeBudget.DEFAULT.value: _TokenBucket(ptc.default.rate, ptc.default.burst),
        }
        self._enable_cb = enable_circuit_breaker
        self._circuit_breaker = _CircuitBreaker(
            failure_threshold=cb_failure_threshold,
            recovery_timeout_s=cb_recovery_timeout_s,
        )
        self._metrics_lock = threading.Lock()
        self._total_requests: int = 0
        self._admitted: int = 0
        self._rate_limited: int = 0
        self._circuit_open: int = 0
        self._rejected: int = 0
        self._last_admit_time: float = 0.0

    def admit(self, event: Any) -> AdmissionResult:
        with self._metrics_lock:
            self._total_requests += 1

        if self._enable_cb and self._circuit_breaker.is_open():
            with self._metrics_lock:
                self._circuit_open += 1
            return AdmissionResult(
                decision=AdmissionDecision.CIRCUIT_OPEN,
                event_type=self._extract_event_type(event),
                retry_after_ms=self._circuit_breaker.retry_after_ms,
                circuit_open=True,
            )

        event_type = self._extract_event_type(event)

        if not self._global_bucket.consume():
            self._circuit_breaker.record_failure()
            with self._metrics_lock:
                self._rate_limited += 1
            return AdmissionResult(
                decision=AdmissionDecision.RATE_LIMITED,
                event_type=event_type,
                retry_after_ms=self._compute_retry_after(event_type),
                remaining_tokens=0.0,
            )

        type_bucket = self._type_buckets.get(event_type, self._type_buckets[EventTypeBudget.DEFAULT.value])
        if not type_bucket.consume():
            self._circuit_breaker.record_failure()
            with self._metrics_lock:
                self._rate_limited += 1
            return AdmissionResult(
                decision=AdmissionDecision.RATE_LIMITED,
                event_type=event_type,
                retry_after_ms=self._compute_retry_after(event_type),
                remaining_tokens=0.0,
            )

        self._circuit_breaker.record_success()
        with self._metrics_lock:
            self._admitted += 1
            self._last_admit_time = time.monotonic()

        return AdmissionResult(
            decision=AdmissionDecision.ADMIT,
            event_type=event_type,
            remaining_tokens=self._global_bucket.tokens,
        )

    def admit_batch(self, events: list[Any]) -> list[AdmissionResult]:
        return [self.admit(evt) for evt in events]

    def get_metrics(self) -> AdmissionMetrics:
        # 5.111.1 修复：原在 _metrics_lock 内访问 _global_bucket.tokens 和 _circuit_breaker.state，
        # 两个 @property 各自获取独立 threading.Lock，构成"持A锁时获取B锁、C锁"嵌套。
        # 改为持锁前先快照子对象状态，然后在 _metrics_lock 块内仅组装返回值。
        global_tokens = self._global_bucket.tokens
        cb_state = self._circuit_breaker.state
        with self._metrics_lock:
            return AdmissionMetrics(
                total_requests=self._total_requests,
                admitted=self._admitted,
                rate_limited=self._rate_limited,
                circuit_open=self._circuit_open,
                rejected=self._rejected,
                global_tokens_remaining=global_tokens,
                circuit_breaker_state=cb_state,
                last_admit_time=self._last_admit_time,
            )

    def get_retry_after(self, event_type: str) -> int:
        if self._enable_cb and self._circuit_breaker.is_open():
            return self._circuit_breaker.retry_after_ms
        return self._compute_retry_after(event_type)

    def reset_circuit_breaker(self) -> None:
        self._circuit_breaker.reset()

    def update_rate(self, new_rate: float, new_burst: float | None = None) -> None:
        self._global_bucket.update_rate(new_rate, new_burst)

    def health_check(self) -> dict[str, Any]:
        metrics = self.get_metrics()
        return {
            "status": "healthy" if metrics.circuit_breaker_state != "open" else "degraded",
            "metrics": metrics.model_dump(),
            "type_bucket_tokens": {k: round(v.tokens, 2) for k, v in self._type_buckets.items()},
        }

    def _extract_event_type(self, event: Any) -> str:
        if isinstance(event, dict):
            raw = event.get("event_type", "")
        elif hasattr(event, "event_type"):
            raw = event.event_type
        else:
            raw = ""
        if isinstance(raw, str):
            return raw if raw in self._type_buckets else EventTypeBudget.DEFAULT.value
        return EventTypeBudget.DEFAULT.value

    def _compute_retry_after(self, event_type: str) -> int:
        type_bucket = self._type_buckets.get(event_type, self._type_buckets[EventTypeBudget.DEFAULT.value])
        if type_bucket._rate > 0:
            return max(1, int(1000.0 / type_bucket._rate))
        return 1000
