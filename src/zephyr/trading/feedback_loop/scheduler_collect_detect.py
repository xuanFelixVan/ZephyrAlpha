# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.scheduler_collect_detect
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] CollectDetectHandler.run_collect/detect/diagnose return bool (should_early_return)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_scheduler_collect_detect | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from zephyr.trading.feedback_loop.collectors.feedback_collector import FeedbackCollector
from zephyr.trading.feedback_loop.collectors.metrics_collector import MetricsCollector, MetricSnapshot
from zephyr.trading.feedback_loop.detectors.agent_trajectory_anomaly_detector import (
    AgentTrajectoryAnomalyDetector,
    TrajectoryEvent,
)
from zephyr.trading.feedback_loop.detectors.anomaly_detector import AnomalyDetector
from zephyr.trading.feedback_loop.detectors.flapping_detector import AlertState, FlappingDetector
from zephyr.trading.feedback_loop.detectors.guard_oscillation_detector import GuardOscillationDetector
from zephyr.trading.feedback_loop.detectors.heisenbug_detector import HeisenbugDetector
from zephyr.trading.feedback_loop.detectors.intermittent_failure_pattern import IntermittentFailurePattern
from zephyr.trading.feedback_loop.detectors.metric_cardinality_guard import MetricCardinalityGuard
from zephyr.trading.feedback_loop.diagnosers.cold_start_conservative_mode import ColdStartConservativeMode
from zephyr.trading.feedback_loop.diagnosers.diagnosis_engine import DiagnosisEngine
from zephyr.trading.feedback_loop.diagnosers.feedback_delay_compensator import FeedbackDelayCompensator
from zephyr.trading.feedback_loop.diagnosers.guard_self_consistency_auditor import GuardSelfConsistencyAuditor
from zephyr.trading.feedback_loop.diagnosers.numerical_stability_guard import NumericalStabilityGuard
from zephyr.trading.feedback_loop.diagnosers.self_bottleneck_detector import PipelineStage, SelfBottleneckDetector
from zephyr.trading.feedback_loop.diagnosers.statistical_hygiene_auditor import StatisticalHygieneAuditor

logger = logging.getLogger(__name__)


@dataclass
class CollectDetectHandler:
    numerical_guard: NumericalStabilityGuard
    cold_start: ColdStartConservativeMode
    bottleneck_detector: SelfBottleneckDetector
    stats_hygiene: StatisticalHygieneAuditor
    guard_consistency: GuardSelfConsistencyAuditor
    guard_oscillation: GuardOscillationDetector
    metrics_collector: MetricsCollector
    feedback_collector: FeedbackCollector

    anomaly_detector: AnomalyDetector = field(init=False)
    trajectory_detector: AgentTrajectoryAnomalyDetector = field(default_factory=AgentTrajectoryAnomalyDetector)
    heisenbug_detector: HeisenbugDetector = field(default_factory=HeisenbugDetector)
    cardinality_guard: MetricCardinalityGuard = field(default_factory=MetricCardinalityGuard)
    flapping_detector: FlappingDetector = field(default_factory=FlappingDetector)
    delay_compensator: FeedbackDelayCompensator = field(default_factory=FeedbackDelayCompensator)
    diagnosis_engine: DiagnosisEngine = field(default_factory=DiagnosisEngine)
    intermittent_pattern: IntermittentFailurePattern = field(default_factory=IntermittentFailurePattern)

    def __post_init__(self) -> None:
        self.anomaly_detector = AnomalyDetector(
            metrics_collector=self.metrics_collector,
            feedback_collector=self.feedback_collector,
        )

    def run_collect(self, event: Any, now: float, run_id: str, metrics_collector: Any) -> Any:
        phase_start = time.time()
        self.cold_start.tick()

        self.trajectory_detector.record_step(
            TrajectoryEvent(
                phase="collect",
                component="metrics_collector",
                timestamp=now,
                input_hash="",
                output_hash=run_id,
            )
        )
        snapshot = MetricSnapshot(
            timestamp=now,
            system_cpu=0.0,
            memory_usage_pct=0.0,
            disk_io_wait=0.0,
            network_errors_count=0,
            detection_latency_ms=0.0,
        )

        for attr_name in (
            "system_cpu",
            "memory_usage_pct",
            "disk_io_wait",
            "network_errors_count",
            "detection_latency_ms",
        ):
            raw = getattr(snapshot, attr_name, 0.0)
            result = self.numerical_guard.validate(attr_name, raw)
            if result["classification"] != "CLEAN":
                logger.warning(
                    "FLE numerical anomaly: %s=%s -> sanitized=%s",
                    attr_name,
                    result["classification"],
                    result["sanitized"],
                )

        metrics_collector.collect(snapshot)
        event.snapshot = snapshot
        self.bottleneck_detector.record_stage_latency(PipelineStage.COLLECT, (time.time() - phase_start) * 1000)
        return snapshot

    def run_detect(self, event: Any, snapshot: Any, run_id: str) -> bool:
        phase_start = time.time()

        self.trajectory_detector.record_step(
            TrajectoryEvent(
                phase="detect",
                component="anomaly_detector",
                timestamp=time.time(),
                input_hash=run_id,
                output_hash="",
            )
        )

        anomaly = self.anomaly_detector.detect(snapshot)

        trajectory_anomalies = self.trajectory_detector.detect_trajectory_anomalies()
        if trajectory_anomalies.get("status") == "anomalous":
            logger.warning("FLE trajectory anomalies: %s", trajectory_anomalies["anomalies"])
        self.heisenbug_detector.detect_heisenbug()
        self.cardinality_guard.record_labels("fle_anomaly", (("source", "scheduler"),))

        if anomaly is None:
            self.bottleneck_detector.record_stage_latency(PipelineStage.DETECT, (time.time() - phase_start) * 1000)
            return True

        flapping = self.flapping_detector.record_state_change(anomaly.anomaly_id, AlertState.ACTIVE)
        if flapping.get("suppressed"):
            logger.info("FLE flapping suppressed: %s", anomaly.anomaly_id)
            self.bottleneck_detector.record_stage_latency(PipelineStage.DETECT, (time.time() - phase_start) * 1000)
            return True

        event.phase = "detect"
        event.anomaly = anomaly
        self.bottleneck_detector.record_stage_latency(PipelineStage.DETECT, (time.time() - phase_start) * 1000)
        return False

    def run_diagnose(self, event: Any, metrics_collector: Any) -> bool:
        phase_start = time.time()
        anomaly = event.anomaly

        hygiene_check = self.stats_hygiene.check_sample_size(
            metrics_collector.baseline.total_samples,
            anomaly.anomaly_id,
        )
        if hygiene_check.get("violation"):
            logger.info("FLE stats hygiene: %s suppressed", anomaly.anomaly_id)
            self.bottleneck_detector.record_stage_latency(PipelineStage.DIAGNOSE, (time.time() - phase_start) * 1000)
            return True

        metric_name = anomaly.evidence.get("metric_name", "")
        delay_check = self.delay_compensator.should_suppress(metric_name)
        if delay_check.get("suppress"):
            logger.info(
                "FLE delay compensation: %s suppressed (%ss remaining)",
                anomaly.anomaly_id,
                delay_check["remaining_seconds"],
            )
            self.bottleneck_detector.record_stage_latency(PipelineStage.DIAGNOSE, (time.time() - phase_start) * 1000)
            return True

        diagnosis = self.diagnosis_engine.diagnose(anomaly.anomaly_id, anomaly.evidence)

        self.trajectory_detector.record_step(
            TrajectoryEvent(
                phase="diagnose",
                component="diagnosis_engine",
                timestamp=time.time(),
                input_hash=anomaly.anomaly_id,
                output_hash="",
            )
        )

        self.guard_consistency.record_outcome("stats_hygiene", not hygiene_check.get("violation"))
        self.guard_consistency.record_outcome("delay_compensator", not delay_check.get("suppress"))
        self.guard_oscillation.record_state_change("diagnosis_engine", "idle", "engaged")

        event.phase = "diagnose"
        event.diagnosis = diagnosis
        self.bottleneck_detector.record_stage_latency(PipelineStage.DIAGNOSE, (time.time() - phase_start) * 1000)
        return False
