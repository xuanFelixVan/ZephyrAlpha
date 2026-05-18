# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.scheduler_act

# [INVARIANTS] ActPhaseHandler.run_act returns ActResult; run_verify returns verification

# [MODIFY-GUARD] none

# [CONSUMERS] zephyr.feedback_loop.scheduler

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from zephyr.feedback_loop.actors.action_selector import ActionSelector
from zephyr.feedback_loop.detectors.action_efficacy_decay_detector import ActionEfficacyDecayDetector
from zephyr.feedback_loop.detectors.action_interaction_detector import ActionInteractionDetector
from zephyr.feedback_loop.detectors.diminishing_returns_detector import DiminishingReturnsDetector
from zephyr.feedback_loop.detectors.guard_oscillation_detector import GuardOscillationDetector
from zephyr.feedback_loop.detectors.placebo_action_detector import PlaceboActionDetector
from zephyr.feedback_loop.diagnosers.action_composition_health_monitor import ActionCompositionHealthMonitor
from zephyr.feedback_loop.diagnosers.context_window_pressure_manager import ContextWindowPressureManager
from zephyr.feedback_loop.diagnosers.self_bottleneck_detector import PipelineStage, SelfBottleneckDetector
from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter
from zephyr.feedback_loop.resilience.graceful_degradation_planner import GracefulDegradationPlanner
from zephyr.feedback_loop.resilience.oscillation_damping import OscillationDamping
from zephyr.feedback_loop.resilience.self_api_throttle_defense import SelfAPIThrottleDefense
from zephyr.feedback_loop.diagnosers.toil_quantification import ToilQuantification
from zephyr.feedback_loop.verifiers.cascading_rollback_analyzer import CascadingRollbackAnalyzer
from zephyr.feedback_loop.verifiers.stochastic_diagnosis_verifier import StochasticDiagnosisVerifier
from zephyr.feedback_loop.verifiers.verification_engine import VerificationEngine


@dataclass
class ActResult:
    action_record: Any = None
    action_type: Any = None
    skipped: bool = False


@dataclass
class ActPhaseHandler:
    throttle_defense: SelfAPIThrottleDefense
    degradation_planner: GracefulDegradationPlanner
    mod_rate_limiter: SelfModificationRateLimiter
    guard_oscillation: GuardOscillationDetector
    context_pressure: ContextWindowPressureManager
    bottleneck_detector: SelfBottleneckDetector

    action_selector: ActionSelector | None = field(init=False, default=None)
    verification_engine: VerificationEngine = field(default_factory=VerificationEngine)
    oscillation_damping: OscillationDamping = field(default_factory=OscillationDamping)
    action_interaction_detector: ActionInteractionDetector = field(default_factory=ActionInteractionDetector)
    toil_tracker: ToilQuantification = field(default_factory=ToilQuantification)
    action_decay: ActionEfficacyDecayDetector = field(default_factory=ActionEfficacyDecayDetector)
    placebo_detector: PlaceboActionDetector = field(default_factory=PlaceboActionDetector)
    composition_health: ActionCompositionHealthMonitor = field(default_factory=ActionCompositionHealthMonitor)
    cascading_rollback: CascadingRollbackAnalyzer = field(default_factory=CascadingRollbackAnalyzer)
    stochastic_verifier: StochasticDiagnosisVerifier = field(default_factory=StochasticDiagnosisVerifier)

    def run_act(self, anomaly: Any, diagnosis: Any, snapshot: Any, run_id: str) -> ActResult:
        action_record = None
        action_type = None

        if self.action_selector is not None:
            throttle = self.throttle_defense.request_action(
                anomaly.anomaly_id, "system",
                priority=diagnosis.severity_level if hasattr(diagnosis, "severity_level") else 3,
            )
            if not throttle["allowed"] and not throttle.get("queued"):
                return ActResult(skipped=True)

            resource_check = self.degradation_planner.evaluate_degradation(
                snapshot.system_cpu * 100, snapshot.memory_usage_pct * 100,
            )
            if resource_check["level"] != "FULL" and (
                diagnosis.severity_level > 1 if hasattr(diagnosis, "severity_level") else True
            ):
                return ActResult(skipped=True)

            action_type = self.action_selector.select_action(diagnosis)
            if action_type is not None:
                if str(action_type) in ("SELF_UPGRADE", "PROMPT_EVOLVE", "KNOWLEDGE_INJECT"):
                    mod_check = self.mod_rate_limiter.request_modification(str(action_type), "warning")
                    if not mod_check["allowed"]:
                        return ActResult(skipped=True)

                oscillation_check = self.oscillation_damping.is_allowed(str(action_type))
                if not oscillation_check:
                    return ActResult(skipped=True)

                action_record = self.action_selector.execute(anomaly, diagnosis, action_type)
                self.action_selector.record_result(action_type, action_record.success if action_record else False)

                if action_record is not None:
                    self.action_interaction_detector.record_action(
                        anomaly.anomaly_id, str(action_type),
                        1.0 if action_record.success else -1.0,
                    )
                    self.toil_tracker.record_action(
                        str(action_type), success=action_record.success, human_intervention_required=False,
                    )
                    self.action_decay.record_outcome(str(action_type), action_record.success)
                    self.placebo_detector.record_action_outcome(
                        str(action_type), 1.0 if action_record.success else 0.0,
                    )
                    self.composition_health.record_composition_outcome(
                        f"{run_id}_{action_type}", (str(action_type),), action_record.success,
                    )
                    self.composition_health.record_independent_outcome(str(action_type), action_record.success)

                if action_record and not action_record.success:
                    self.cascading_rollback.record_action_dependency(
                        anomaly.anomaly_id, [str(action_type)],
                    )

        self.bottleneck_detector.record_stage_latency(PipelineStage.ACT, 0.0)

        return ActResult(action_record=action_record, action_type=action_type)

    def run_verify(
        self,
        anomaly: Any,
        diagnosis: Any,
        run_id: str,
        get_current_metric: Any,
    ) -> Any:
        verification = self.verification_engine.verify(
            anomaly_id=anomaly.anomaly_id,
            pre_value=anomaly.evidence.get("value", 0.0),
            post_value=get_current_metric(anomaly.evidence.get("metric_name", "")),
            timestamp=time.time(),
        )

        self.stochastic_verifier.record_diagnosis_run(
            anomaly.anomaly_id, 0,
            diagnosis.root_cause if hasattr(diagnosis, "root_cause") else "unknown",
            diagnosis.confidence if hasattr(diagnosis, "confidence") else 0.5,
        )

        self.placebo_detector.record_control_outcome(
            1.0 if verification.verdict.value == "healthy" else 0.0,
        )

        self.guard_oscillation.record_state_change("verifier", "engaged", "idle")

        pressure = self.context_pressure.check_pressure()
        if pressure.get("needs_compression"):
            removed = self.context_pressure.compress()

        self.bottleneck_detector.record_stage_latency(PipelineStage.VERIFY, 0.0)

        return verification
