# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.resilience.self_api_throttle_defense
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_self_api_throttle_defense | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Self API Throttle Defense — v0.39.0 R491

Blindspot: FLE's own diagnosis/repair actions can overwhelm the very systems
they monitor. A burst of automated actions generates a burst of metrics, which
triggers more detection, which dispatches more actions — runaway amplification.

Risk: R491 — FLE becomes a self-DoS engine. Flood of automated API calls
saturates system resources, creating more anomalies, triggering more actions.
Positive feedback loop destroys system availability.

Mitigation: Token bucket rate limiter for FLE's own outbound actions. Per-target
concurrency cap. Global action budget with burst allowance. When budget exhausted
-> queue or drop non-critical actions. Alert when throttling activates.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ThrottleState(str, Enum):
    NORMAL = "NORMAL"
    THROTTLING = "THROTTLING"
    SATURATED = "SATURATED"


@dataclass
class SelfAPIThrottleDefense:
    global_rate_per_second: float = 10.0
    global_burst: int = 50
    per_target_rate_per_second: float = 2.0
    per_target_burst: int = 10
    max_queue_size: int = 200

    global_tokens: float = 0.0
    target_tokens: dict[str, float] = field(default_factory=dict)
    action_queue: list[dict] = field(default_factory=list)
    throttle_state: ThrottleState = ThrottleState.NORMAL
    last_refill: float = field(default_factory=time.time)
    throttled_count: int = 0

    def _refill_tokens(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        self.last_refill = now

        self.global_tokens = min(
            float(self.global_burst),
            self.global_tokens + elapsed * self.global_rate_per_second,
        )

        for target in list(self.target_tokens):
            self.target_tokens[target] = min(
                float(self.per_target_burst),
                self.target_tokens[target] + elapsed * self.per_target_rate_per_second,
            )

            if self.target_tokens[target] < 0.01:
                del self.target_tokens[target]

    def request_action(self, action_id: str, target: str, priority: int = 3) -> dict:
        self._refill_tokens()

        if target not in self.target_tokens:
            self.target_tokens[target] = float(self.per_target_burst)

        global_ok = self.global_tokens >= 1.0
        target_ok = self.target_tokens.get(target, 0.0) >= 1.0
        queue_not_full = len(self.action_queue) < self.max_queue_size

        if global_ok and target_ok:
            self.global_tokens -= 1.0
            self.target_tokens[target] -= 1.0
            return {"action_id": action_id, "allowed": True, "target": target}

        if queue_not_full and priority <= 2:
            self.action_queue.append(
                {
                    "action_id": action_id,
                    "target": target,
                    "priority": priority,
                    "queued_at": time.time(),
                }
            )
            return {"action_id": action_id, "allowed": False, "queued": True, "target": target}

        self.throttled_count += 1

        if self.global_tokens < 0.0:
            self.throttle_state = ThrottleState.SATURATED
        else:
            self.throttle_state = ThrottleState.THROTTLING

        return {
            "action_id": action_id,
            "allowed": False,
            "queued": False,
            "target": target,
            "throttle_state": self.throttle_state.value,
            "recommendation": "reduce_action_frequency_or_increase_budget",
        }

    def drain_queue(self, max_drain: int = 10) -> list[str]:
        self._refill_tokens()
        dispatched = []
        remaining = []

        for item in self.action_queue[:max_drain]:
            target = item["target"]
            if target not in self.target_tokens:
                self.target_tokens[target] = float(self.per_target_burst)

            if self.global_tokens >= 1.0 and self.target_tokens[target] >= 1.0:
                self.global_tokens -= 1.0
                self.target_tokens[target] -= 1.0
                dispatched.append(item["action_id"])
            else:
                remaining.append(item)

        self.action_queue = remaining + self.action_queue[max_drain:]
        return dispatched

    def get_throttle_status(self) -> dict:
        self._refill_tokens()
        return {
            "state": self.throttle_state.value,
            "global_tokens_available": round(self.global_tokens, 1),
            "global_burst": self.global_burst,
            "queue_depth": len(self.action_queue),
            "throttled_total": self.throttled_count,
            "active_targets": len(self.target_tokens),
            "recommendation": (
                "emergency_throttle_all_non_critical"
                if self.throttle_state is ThrottleState.SATURATED
                else "reduce_non_critical_actions"
                if self.throttle_state is ThrottleState.THROTTLING
                else "continue"
            ),
        }

    def reset_counters(self) -> None:
        self.throttled_count = 0
        self.throttle_state = ThrottleState.NORMAL
