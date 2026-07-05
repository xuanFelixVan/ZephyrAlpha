# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.stream_abort_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_stream_abort_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""StreamAbortGuard — 流式中断守卫
=====================================
蓝图 §2.13 · 流式输出中途预算二次确认

检查点（每 500 output token）
-----------------------------
  budget_exhausted → IMMEDIATE_ABORT
  quality_low      → ABORT_AND_RETRY（切更便宜模型）
  too_verbose      → ABORT_WITH_WARNING
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class AbortDecision(Enum):
    CONTINUE = auto()
    IMMEDIATE_ABORT = auto()
    ABORT_AND_RETRY = auto()
    ABORT_WITH_WARNING = auto()


AbortReason = AbortDecision


class StreamState(Enum):
    ACTIVE = auto()
    PAUSED = auto()
    ABORTED = auto()
    COMPLETED = auto()


class ProviderProtocol(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"


@dataclass
class StreamCheckpoint:
    tokens_emitted: int = 0
    estimated_completion_tokens: int = 0
    quality_score: float = 1.0
    remaining_budget: float = 0.0
    session_budget: float = 0.0
    expected_max_tokens: int = 0
    provider: ProviderProtocol = ProviderProtocol.ANTHROPIC


@dataclass
class AbortResult:
    decision: AbortDecision
    reason: str = ""
    partial_output: str = ""
    tokens_emitted: int = 0
    retry_model_tier: str = ""
    timestamp: float = field(default_factory=time.time)


_CHECKPOINT_INTERVAL = 500
_QUALITY_THRESHOLD = 0.3
_QUALITY_MIN_TOKENS = 200
_VERBOSITY_MULTIPLIER = 3.0
_SLIDING_WINDOW_SECONDS = 60.0
_MICRO_TRANSACTION_THRESHOLD = 0.01
_MICRO_TRANSACTION_ACCUMULATION_LIMIT = 1.0


class StreamAbortGuard:
    def __init__(
        self,
        checkpoint_interval: int = _CHECKPOINT_INTERVAL,
        quality_threshold: float = _QUALITY_THRESHOLD,
        verbosity_multiplier: float = _VERBOSITY_MULTIPLIER,
        sliding_window_seconds: float = _SLIDING_WINDOW_SECONDS,
        micro_transaction_threshold: float = _MICRO_TRANSACTION_THRESHOLD,
        micro_transaction_accumulation_limit: float = _MICRO_TRANSACTION_ACCUMULATION_LIMIT,
    ) -> None:
        self._checkpoint_interval = checkpoint_interval
        self._quality_threshold = quality_threshold
        self._verbosity_multiplier = verbosity_multiplier
        self._sliding_window_seconds = sliding_window_seconds
        self._micro_transaction_threshold = micro_transaction_threshold
        self._micro_transaction_accumulation_limit = micro_transaction_accumulation_limit
        self._cost_events: list[tuple[float, float]] = []
        self._partial_output: str = ""
        self._tokens_emitted: int = 0
        self._aborted: bool = False
        self._abort_history: list[AbortResult] = []
        self._lock = threading.Lock()

    def check(self, checkpoint: StreamCheckpoint) -> AbortResult:
        if checkpoint.tokens_emitted % self._checkpoint_interval != 0 and checkpoint.tokens_emitted > 0:
            return AbortResult(decision=AbortDecision.CONTINUE, tokens_emitted=checkpoint.tokens_emitted)

        micro_abort = self._check_micro_transaction_accumulation()
        if micro_abort is not None:
            return micro_abort

        if checkpoint.remaining_budget - checkpoint.estimated_completion_tokens < 0:
            result = AbortResult(
                decision=AbortDecision.IMMEDIATE_ABORT,
                reason=f"预算耗尽 — remaining={checkpoint.remaining_budget:.0f}, completion_est={checkpoint.estimated_completion_tokens}",
                tokens_emitted=checkpoint.tokens_emitted,
            )
            self._record_abort(result)
            return result

        if checkpoint.quality_score < self._quality_threshold and checkpoint.tokens_emitted > _QUALITY_MIN_TOKENS:
            result = AbortResult(
                decision=AbortDecision.ABORT_AND_RETRY,
                reason=f"质量过低 — score={checkpoint.quality_score:.2f} < {self._quality_threshold}",
                tokens_emitted=checkpoint.tokens_emitted,
                retry_model_tier="economy",
            )
            self._record_abort(result)
            return result

        if (
            checkpoint.expected_max_tokens > 0
            and checkpoint.tokens_emitted > checkpoint.expected_max_tokens * self._verbosity_multiplier
        ):
            result = AbortResult(
                decision=AbortDecision.ABORT_WITH_WARNING,
                reason=f"响应过于冗长 — {checkpoint.tokens_emitted} > {checkpoint.expected_max_tokens}×{self._verbosity_multiplier}",
                tokens_emitted=checkpoint.tokens_emitted,
            )
            self._record_abort(result)
            return result

        return AbortResult(decision=AbortDecision.CONTINUE, tokens_emitted=checkpoint.tokens_emitted)

    def record_chunk_cost(self, cost: float) -> AbortResult | None:
        with self._lock:
            now = time.time()
            self._cost_events.append((now, cost))
            self._prune_cost_events(now)
            total = sum(c for _, c in self._cost_events)
            if cost <= self._micro_transaction_threshold and total > self._micro_transaction_accumulation_limit:
                result = AbortResult(
                    decision=AbortDecision.IMMEDIATE_ABORT,
                    reason=f"微交易累积超限 — {len(self._cost_events)} chunks totaling ${total:.2f} > ${self._micro_transaction_accumulation_limit:.2f} limit",
                    tokens_emitted=0,
                )
                self._aborted = True
                self._abort_history.append(result)
                return result
        return None

    def _check_micro_transaction_accumulation(self) -> AbortResult | None:
        with self._lock:
            now = time.time()
            self._prune_cost_events(now)
            total = sum(c for _, c in self._cost_events)
            if len(self._cost_events) >= 5 and total > self._micro_transaction_accumulation_limit:
                result = AbortResult(
                    decision=AbortDecision.IMMEDIATE_ABORT,
                    reason=f"滑动窗口累积超限 — {len(self._cost_events)} chunks in {self._sliding_window_seconds:.0f}s totaling ${total:.2f} > ${self._micro_transaction_accumulation_limit:.2f}",
                    tokens_emitted=0,
                )
                self._aborted = True
                self._abort_history.append(result)
                return result
        return None

    def _prune_cost_events(self, now: float) -> None:
        cutoff = now - self._sliding_window_seconds
        self._cost_events = [(t, c) for t, c in self._cost_events if t > cutoff]

    def _record_abort(self, result: AbortResult) -> None:
        with self._lock:
            self._aborted = True
            self._abort_history.append(result)

    def save_partial(self, output: str) -> None:
        with self._lock:
            self._partial_output = output

    def get_partial(self) -> str:
        with self._lock:
            return self._partial_output

    def get_resume_prompt(self) -> str:
        with self._lock:
            if not self._partial_output:
                return ""
            return f"[Previous partial output — continue from here]\n{self._partial_output[-500:]}"

    @property
    def is_aborted(self) -> bool:
        with self._lock:
            return self._aborted

    def get_abort_history(self) -> list[AbortResult]:
        with self._lock:
            return list(self._abort_history)

    def reset(self) -> None:
        with self._lock:
            self._partial_output = ""
            self._tokens_emitted = 0
            self._aborted = False
            self._cost_events.clear()

    def get_provider_stop_reason(self, provider: ProviderProtocol) -> str:
        mapping = {
            ProviderProtocol.ANTHROPIC: "max_tokens",
            ProviderProtocol.OPENAI: "length",
            ProviderProtocol.GOOGLE: "MAX_TOKENS",
            ProviderProtocol.DEEPSEEK: "length",
        }
        return mapping.get(provider, "length")

    def summary(self) -> dict[str, Any]:
        with self._lock:
            now = time.time()
            self._prune_cost_events(now)
            return {
                "checkpoint_interval": self._checkpoint_interval,
                "quality_threshold": self._quality_threshold,
                "verbosity_multiplier": self._verbosity_multiplier,
                "is_aborted": self._aborted,
                "abort_count": len(self._abort_history),
                "partial_output_length": len(self._partial_output),
                "sliding_window_seconds": self._sliding_window_seconds,
                "micro_transaction_threshold": self._micro_transaction_threshold,
                "micro_transaction_accumulation_limit": self._micro_transaction_accumulation_limit,
                "cost_events_in_window": len(self._cost_events),
                "total_cost_in_window": sum(c for _, c in self._cost_events),
            }


__all__ = [
    "AbortDecision",
    "AbortResult",
    "ProviderProtocol",
    "StreamAbortGuard",
    "StreamCheckpoint",
]
