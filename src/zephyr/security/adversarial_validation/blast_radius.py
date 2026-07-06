# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.1 + §16 Phase 1
# [MODULE] zephyr.security.adversarial_validation.blast_radius
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models
# [CONSUMERS] validator.py; injection_engine.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 4-level progressive escalation: FILE(1)→MODULE(2)→CROSS_MODULE(3)→SYSTEM(4); auto-abort when bypass_count reaches threshold for current level
# [MODIFY-GUARD] Threshold values per blueprint §7.2; adding levels MUST update BlastRadiusLevel enum in models.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AbortThresholdError when bypass_count >= threshold at SYSTEM level
# [TESTS] tests/red_blue/test_blast_radius.py
# [A_module] module_id=MOD-SEC_blast_radius | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging

from zephyr.security.adversarial_validation.models import AttackScenario, BlastRadiusLevel

logger = logging.getLogger(__name__)

__all__: list[str] = ["AbortThresholdError", "BlastRadius"]

LEVEL_THRESHOLD: Final[dict[BlastRadiusLevel, int]] = {
    BlastRadiusLevel.FILE: 3,
    BlastRadiusLevel.MODULE: 5,
    BlastRadiusLevel.CROSS_MODULE: 8,
    BlastRadiusLevel.SYSTEM: 15,
}

LEVEL_ORDER: Final[list[BlastRadiusLevel]] = [
    BlastRadiusLevel.FILE,
    BlastRadiusLevel.MODULE,
    BlastRadiusLevel.CROSS_MODULE,
    BlastRadiusLevel.SYSTEM,
]


class AbortThresholdError(RuntimeError):
    pass


class BlastRadius:
    def __init__(self, initial_level: BlastRadiusLevel = BlastRadiusLevel.FILE) -> None:
        self._current_level: BlastRadiusLevel = initial_level
        self._bypass_counts: dict[BlastRadiusLevel, int] = {lvl: 0 for lvl in LEVEL_ORDER}
        self._aborted: bool = False

    @property
    def current_level(self) -> BlastRadiusLevel:
        return self._current_level

    @property
    def aborted(self) -> bool:
        return self._aborted

    def record_bypass(self, scenario: AttackScenario) -> BlastRadiusLevel | None:
        scenario_level = scenario.blast_radius
        self._bypass_counts[scenario_level] = self._bypass_counts.get(scenario_level, 0) + 1

        escalated = self._maybe_escalate(scenario_level)
        if escalated:
            logger.warning("blast_radius_escalated from=%s to=%s", scenario_level.value, self._current_level.value)

        if self._should_abort():
            self._aborted = True
            raise AbortThresholdError(
                f"Blast radius abort: {self._bypass_counts[self._current_level]} bypasses "
                f"at {self._current_level.value} level (threshold: {LEVEL_THRESHOLD[self._current_level]})"
            )

        return self._current_level

    def filter_scenarios(self, scenarios: list[AttackScenario]) -> list[AttackScenario]:
        return [s for s in scenarios if s.blast_radius.risk_rank <= self._current_level.risk_rank]

    def reset(self) -> None:
        self._current_level = BlastRadiusLevel.FILE
        self._bypass_counts = {lvl: 0 for lvl in LEVEL_ORDER}
        self._aborted = False
        logger.info("blast_radius_reset")

    def _maybe_escalate(self, bypass_level: BlastRadiusLevel) -> bool:
        current_rank = self._current_level.risk_rank
        bypass_rank = bypass_level.risk_rank

        if bypass_rank > current_rank:
            self._current_level = bypass_level
            return True

        bypasses_at_current = self._bypass_counts.get(self._current_level, 0)
        threshold = LEVEL_THRESHOLD.get(self._current_level, 3)
        if bypasses_at_current >= threshold:
            next_rank = current_rank + 1
            if next_rank <= 4:
                self._current_level = LEVEL_ORDER[next_rank - 1]
                return True

        return False

    def _should_abort(self) -> bool:
        if self._current_level is BlastRadiusLevel.SYSTEM:
            return self._bypass_counts.get(BlastRadiusLevel.SYSTEM, 0) >= LEVEL_THRESHOLD[BlastRadiusLevel.SYSTEM]
        return False
