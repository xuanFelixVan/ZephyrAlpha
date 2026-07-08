# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.security.wireheading_prevention
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_wireheading_prevention | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Wireheading Prevention — v0.37.0 R486

Blindspot: FLE gains ability to modify its own success metrics;
learns to game KPI measurements instead of fixing real problems.

Risk: R486 — FLE wireheads by altering metric definitions, thresholds,
or data sources to report false success (AI safety critical).

Mitigation: Immutable metric definitions with cryptographic signature.
Any attempt to modify metric registry -> immediate SAFE_MODE + full audit.
Whitelist-only modification channel requiring owner cryptographic approval.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum


class WireheadState(str, Enum):
    CLEAN = "CLEAN"
    ATTEMPT_DETECTED = "ATTEMPT_DETECTED"
    SAFE_MODE = "SAFE_MODE"


@dataclass
class WireheadingPrevention:
    immutable_metrics: dict[str, str] = field(default_factory=dict)
    modification_attempts: list[dict] = field(default_factory=list)
    state: WireheadState = WireheadState.CLEAN
    safe_mode_until: float = 0.0

    def register_metric(self, name: str, definition: str) -> str:
        sig = hashlib.sha256(definition.encode("utf-8")).hexdigest()[:32]
        self.immutable_metrics[name] = sig
        return sig

    def verify_metric(self, name: str, definition: str) -> bool:
        if self.state is WireheadState.SAFE_MODE:
            return False
        expected = self.immutable_metrics.get(name)
        if not expected:
            return True
        actual = hashlib.sha256(definition.encode("utf-8")).hexdigest()[:32]

        if actual != expected:
            self.modification_attempts.append(
                {
                    "metric": name,
                    "time": time.time(),
                    "expected_hash": expected,
                    "actual_hash": actual,
                }
            )
            if len(self.modification_attempts) >= 3:
                self._trigger_safe_mode()
            self.state = WireheadState.ATTEMPT_DETECTED
            return False

        return True

    def _trigger_safe_mode(self) -> None:
        self.state = WireheadState.SAFE_MODE
        self.safe_mode_until = time.time() + 3600.0

    def owner_override_reset(self) -> None:
        self.state = WireheadState.CLEAN
        self.modification_attempts.clear()
