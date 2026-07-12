# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.evolution.self_upgrade_canary
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
# [A_module] module_id=MOD-UNK_self_upgrade_canary | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Self Upgrade Canary — v0.14.0 R194

Blindspot: FLE upgrades deployed to 100% instantly; bad upgrade breaks everything.
Risk: R194 — FLE self-upgrade introduces regression; no canary deployment strategy.

Mitigation: 5%->100% canary deployment for FLE self-upgrades with auto-rollback.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CanaryPhase(str, Enum):
    INIT = "INIT"
    CANARY_5 = "CANARY_5"
    CANARY_25 = "CANARY_25"
    CANARY_50 = "CANARY_50"
    FULL_100 = "FULL_100"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class CanaryStep:
    pct: int
    health_check_pass: bool
    duration_seconds: float


@dataclass
class SelfUpgradeCanary:
    phases: list[tuple[int, int]] = field(default_factory=lambda: [(5, 300), (25, 600), (50, 900), (100, 1800)])
    current_phase: CanaryPhase = CanaryPhase.INIT
    steps: list[CanaryStep] = field(default_factory=list)

    def advance(self, health_ok: bool) -> CanaryPhase:
        if not health_ok:
            self.current_phase = CanaryPhase.ROLLED_BACK
            return self.current_phase

        phases = [CanaryPhase.CANARY_5, CanaryPhase.CANARY_25, CanaryPhase.CANARY_50, CanaryPhase.FULL_100]
        idx = phases.index(self.current_phase) if self.current_phase in phases else -1
        next_idx = idx + 1
        if next_idx < len(phases):
            self.current_phase = phases[next_idx]
            self.steps.append(
                CanaryStep(
                    pct=self.phases[next_idx][0],
                    health_check_pass=True,
                    duration_seconds=self.phases[next_idx][1],
                )
            )
        return self.current_phase

    def rollback(self) -> None:
        self.current_phase = CanaryPhase.ROLLED_BACK
