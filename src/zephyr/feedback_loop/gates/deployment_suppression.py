# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.deployment_suppression
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES] zephyr.feedback_loop.gates.__init__
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
# [A_module] module_id=MOD-UNK_deployment_suppression | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Deployment Suppression — v0.37.0 R464

Blindspot: New deployments proceed while FLE detects active instability;
fresh code injected into already-degrading system compounds damage.

Risk: R464 — Deployment during active incident amplifies blast radius.

Mitigation: FLE-instability gate before deployment pipeline. If FLE
reports DEGRADED or higher state -> block deployment. Auto-release
when system returns to NOMINAL for sustain_window seconds.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum


class DeployGateState(str, Enum):
    OPEN = "OPEN"
    BLOCKED_STABILITY = "BLOCKED_STABILITY"
    BLOCKED_INCIDENT = "BLOCKED_INCIDENT"


@dataclass
class DeploymentSuppression:
    sustain_window: float = 300.0

    state: DeployGateState = DeployGateState.OPEN
    blocked_since: float = 0.0
    stable_since: float | None = None
    blocked_count: int = 0

    def update_from_fle_state(self, fle_state: str) -> DeployGateState:
        now = time.time()

        if fle_state in ("DEGRADED", "INEFFECTIVE", "CRISIS", "SAFE_MODE"):
            if self.state is DeployGateState.OPEN:
                self.blocked_count += 1
                self.blocked_since = now
            self.state = DeployGateState.BLOCKED_STABILITY
            self.stable_since = None
        elif fle_state == "INCIDENT_ACTIVE":
            self.state = DeployGateState.BLOCKED_INCIDENT
            self.stable_since = None
        else:
            if self.stable_since is None:
                self.stable_since = now
            if now - self.stable_since >= self.sustain_window:
                self.state = DeployGateState.OPEN

        return self.state

    def is_deploy_allowed(self) -> bool:
        return self.state is DeployGateState.OPEN

    def remaining_block(self) -> float:
        if self.state is DeployGateState.OPEN:
            return 0.0
        return max(0.0, self.sustain_window - (time.time() - self.stable_since)) if self.stable_since else 999.0
