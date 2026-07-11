# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.evolution.self_modification_rate_limiter
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-UNK_self_modification_rate_limiter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R522: SelfModificationRateLimiter
TokenBucket自修改速率限制 — 每小时最多N次，防止失控螺旋
"""

import time
from dataclasses import dataclass


@dataclass
class SelfModificationRateLimiter:
    max_burst: int = 5
    refill_rate_per_hour: int = 10
    tokens: float = 0.0
    last_refill: float = 0.0
    blocked_count: int = 0
    total_requests: int = 0

    def __post_init__(self) -> None:
        self.tokens = float(self.max_burst)
        self.last_refill = time.time()

    def request_modification(self, change_type: str, severity: str) -> dict:
        self.total_requests += 1
        self._refill()

        allowed = self.tokens >= 1.0
        if allowed:
            self.tokens -= 1.0

            if severity == "critical":
                pass
        else:
            self.blocked_count += 1

        return {
            "allowed": allowed,
            "tokens_remaining": round(self.tokens, 1),
            "max_burst": self.max_burst,
            "refill_rate_per_hour": self.refill_rate_per_hour,
            "change_type": change_type,
            "blocked_count": self.blocked_count,
            "total_requests": self.total_requests,
        }

    def _refill(self) -> None:
        now = time.time()
        elapsed_hours = (now - self.last_refill) / 3600.0
        self.tokens = min(
            self.tokens + elapsed_hours * self.refill_rate_per_hour,
            float(self.max_burst),
        )
        self.last_refill = now

    def get_status(self) -> dict:
        self._refill()
        return {
            "tokens_available": round(self.tokens, 1),
            "max_burst": self.max_burst,
            "total_modifications_allowed": self.total_requests - self.blocked_count,
            "total_blocked": self.blocked_count,
            "block_rate": round(self.blocked_count / max(self.total_requests, 1), 3),
        }

    def emergency_override(self) -> dict:
        self.tokens = float(self.max_burst)
        self.last_refill = time.time()
        self.blocked_count = 0
        return {"override": "activated", "tokens_reset": self.max_burst}
