# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.3 + §16 Phase 1
# [MODULE] zephyr.security.adversarial_validation.validator
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models; zephyr.security.adversarial_validation.scenario_loader; zephyr.security.adversarial_validation.defense_runner; zephyr.security.adversarial_validation.bypass_recorder; zephyr.security.adversarial_validation.steady_state; zephyr.security.adversarial_validation.cleanup; zephyr.security.adversarial_validation.blast_radius
# [CONSUMERS] cli.py; game_day_runner.py; mcp_endpoints.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] run_adversarial_session() MUST follow: load->filter->defend->record->steady_state->cleanup; RedBlueReport.session_id MUST be unique per run
# [MODIFY-GUARD] Adding new phases to adversarial session MUST update run_adversarial_session() flow; report fields per blueprint §4.4
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SessionError on cleanup failure; AbortThresholdError propagates from BlastRadius
# [TESTS] tests/red_blue/test_validator.py
# [A_module] module_id=MOD-SEC_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from zephyr.security.adversarial_validation.blast_radius import AbortThresholdError, BlastRadius
from zephyr.security.adversarial_validation.bypass_recorder import BypassRecorder
from zephyr.security.adversarial_validation.cleanup import Cleanup, CleanupVerificationError
from zephyr.security.adversarial_validation.defense_runner import DefenseRunner
from zephyr.security.adversarial_validation.models import (
    AttackScenario,
    AttackTier,
    BlastRadiusLevel,
    RedBlueReport,
    ResultClass,
    ScenarioResult,
    SteadyStateSummary,
)
from zephyr.security.adversarial_validation.scenario_loader import ScenarioLoader
from zephyr.security.adversarial_validation.steady_state import SteadyState, SteadyStateDriftError

logger = logging.getLogger(__name__)

__all__: list[str] = ["RedBlueValidator", "SessionError"]


class SessionError(RuntimeError):
    error_code = "ZA-SC-0001"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class RedBlueValidator:
    def __init__(self) -> None:
        self._loader = ScenarioLoader()
        self._defense = DefenseRunner()
        self._recorder = BypassRecorder()
        self._steady = SteadyState()
        self._cleanup = Cleanup()
        self._blast = BlastRadius(BlastRadiusLevel.FILE)

    def run_adversarial_session(
        self,
        session_name: str,
        tier: AttackTier | None = None,
        blast_radius: BlastRadiusLevel = BlastRadiusLevel.FILE,
    ) -> RedBlueReport:
        session_id = f"RB-{uuid.uuid4().hex[:12]}"
        self._blast.reset()
        self._blast = BlastRadius(blast_radius)

        start = datetime.now(UTC)

        scenarios = self._load_and_filter(tier)
        if not scenarios:
            return RedBlueReport(session_id=session_id)

        self._steady.verify_before_attack()

        scene_results: list[ScenarioResult] = []
        blocked = 0
        bypassed = 0

        for scenario in scenarios:
            result = self._process_scenario(scenario)
            scene_results.append(result)
            if result.result is ResultClass.BLOCKED:
                blocked += 1
            elif result.result is ResultClass.BYPASSED:
                bypassed += 1
                try:
                    self._blast.record_bypass(scenario)
                except AbortThresholdError as e:
                    logger.critical("blast_radius_aborted error=%s", str(e))
                    report = self._build_report(session_id, scene_results, blocked, bypassed, start)
                    report.circuit_breaker_open = True
                    return report

        steady_summary: SteadyStateSummary
        try:
            steady_summary = self._steady.verify_after_attack()
        except SteadyStateDriftError:
            steady_summary = SteadyStateSummary(drifted=35, total_metrics=35, drift_rate=100.0)

        cleanup_ok = False
        try:
            self._cleanup.ensure_clean()
            cleanup_ok = True
        except CleanupVerificationError:
            logger.error("cleanup_failed")

        report = self._build_report(session_id, scene_results, blocked, bypassed, start)
        report.steady_state_summary = steady_summary
        report.cleanup_verified = cleanup_ok

        logger.info("session_complete session_id=%s blocked=%d bypassed=%d", session_id, blocked, bypassed)

        # F30 RedBlueValidator 验证完成时发布 validation_result 事件 (F30->F15)
        try:
            from zephyr.shared.event_bus import EventBusBackpressure

            EventBusBackpressure().emit(
                "validation_result",
                payload={
                    "timestamp": datetime.now(UTC).isoformat(),
                    "source_function": "RedBlueValidator.run_adversarial_session",
                    "severity": "info" if bypassed == 0 else "high",
                    "detail": f"session_id={session_id} blocked={blocked} bypassed={bypassed} total={len(scene_results)}",
                },
            )
        except Exception as e:
            logger.warning("suppressed error in validator", exc_info=True)

        return report

    def _load_and_filter(self, tier: AttackTier | None = None) -> list[AttackScenario]:
        all_scenarios = self._loader.load()
        active = [s for s in all_scenarios if s.status == "active"]
        if tier:
            active = [s for s in active if s.tier == tier]
        return self._blast.filter_scenarios(active)

    def _process_scenario(self, scenario: AttackScenario) -> ScenarioResult:
        defense_result = self._defense.run_defense(scenario)
        now = datetime.now(UTC)

        if defense_result.passed:
            return ScenarioResult(
                scenario_id=scenario.scenario_id,
                name=scenario.name,
                tier=scenario.tier,
                result=ResultClass.BLOCKED,
                gate_id=defense_result.gate_id,
                detail=defense_result.detail,
            )
        else:
            bypass = self._recorder.record_bypass(
                scenario_id=scenario.scenario_id,
                gate_id=defense_result.gate_id,
                detail=defense_result.detail,
                attack_payload=scenario.injection.payload,
                defense_response=defense_result.detail,
                tier=scenario.tier,
            )
            return ScenarioResult(
                scenario_id=scenario.scenario_id,
                name=scenario.name,
                tier=scenario.tier,
                result=ResultClass.BYPASSED,
                gate_id=defense_result.gate_id,
                detail=defense_result.detail,
                bypass_entry=bypass.entry_id,
            )

    def _build_report(
        self,
        session_id: str,
        results: list[ScenarioResult],
        blocked: int,
        bypassed: int,
        start: datetime,
    ) -> RedBlueReport:
        total = len(results)
        duration = (datetime.now(UTC) - start).total_seconds() * 1000
        report = RedBlueReport(
            session_id=session_id,
            total=total,
            blocked=blocked,
            bypassed=bypassed,
            scenarios=results,
            new_bypass_entries=bypassed,
            blast_radius_used=self._blast.current_level,
            duration_ms=round(duration, 1),
        )
        report.compute_blocked_rate()
        return report
