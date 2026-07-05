# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.fitness_functions
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_fitness_functions | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

METRIC_COMPLIANCE_RATE = "METRIC_COMPLIANCE_RATE"
METRIC_HALLUCINATION_INTERCEPTION = "METRIC_HALLUCINATION_INTERCEPTION"
METRIC_KNOWLEDGE_ACTIVATION = "METRIC_KNOWLEDGE_ACTIVATION"
METRIC_MODULE_COUPLING = "METRIC_MODULE_COUPLING"
METRIC_TEST_COVERAGE = "METRIC_TEST_COVERAGE"


class MetricStatus(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass
class FitnessThresholds:
    module_coupling_max: float = 0.30
    test_coverage_min: float = 65.0
    compliance_rate_min: float = 0.90
    knowledge_activation_min: float = 0.30
    hallucination_interception_min: float = 0.70
    warn_margin: float = 0.05


@dataclass
class FitnessInputs:
    dependency_edges: int = 0
    module_count: int = 1
    coverage_pct: float = 0.0
    gate_total: int = 0
    gate_passed: int = 0
    ke_total: int = 0
    ke_activated: int = 0
    hallucination_total: int = 0
    hallucination_intercepted: int = 0


@dataclass
class MetricResult:
    metric_name: str
    value: float
    threshold: float
    status: MetricStatus = MetricStatus.PASS
    message: str = ""


@dataclass
class FitnessReport:
    report_id: str = ""
    overall_status: MetricStatus = MetricStatus.PASS
    passed: bool = False
    metrics: list[MetricResult] = field(default_factory=list)

    def get_metric(self, name: str) -> MetricResult | None:
        for m in self.metrics:
            if m.metric_name == name:
                return m
        return None


@dataclass
class FitnessScores:
    anomaly_detection_precision: float = 0.0
    false_positive_rate: float = 0.0
    mtti_seconds: float = 0.0
    owner_override_rate: float = 0.0


@dataclass
class FitnessFunctionFramework:
    thresholds: FitnessThresholds = field(default_factory=FitnessThresholds)

    def _status(self, value: float, lo_threshold: float) -> MetricStatus:
        delta = lo_threshold - value
        if delta <= 0:
            return MetricStatus.PASS
        if lo_threshold > 1.0:
            if delta <= self.thresholds.warn_margin * 100:
                return MetricStatus.WARN
        else:
            if delta <= self.thresholds.warn_margin:
                return MetricStatus.WARN
        return MetricStatus.FAIL

    def _status_hi(self, value: float, hi_threshold: float) -> MetricStatus:
        delta = value - hi_threshold
        if delta <= 0:
            return MetricStatus.PASS
        if delta <= self.thresholds.warn_margin:
            return MetricStatus.WARN
        return MetricStatus.FAIL

    # ----- measure_module_coupling -----
    def measure_module_coupling(
        self,
        edges: list[tuple[str, str]] | None = None,
        *,
        module_count: int = 1,
    ) -> MetricResult:
        deduped: set[tuple[str, str]] = set()
        if edges is not None:
            for a, b in edges:
                deduped.add((a, b) if a <= b else (b, a))
        dep_count = len(deduped)
        mc = max(module_count, 1)
        max_edges = mc * (mc - 1) / 2
        coupling = dep_count / max_edges if max_edges > 0 else 0.0
        t = self.thresholds.module_coupling_max
        st = self._status_hi(coupling, t)
        msg = ""
        if st is not MetricStatus.PASS:
            msg = f"Coupling {coupling:.3f} exceeds max {t}"
        return MetricResult(
            metric_name=METRIC_MODULE_COUPLING,
            value=coupling,
            threshold=t,
            status=st,
            message=msg,
        )

    # ----- measure_test_coverage -----
    def measure_test_coverage(
        self,
        coverage_pct: float = 0.0,
    ) -> MetricResult:
        t = self.thresholds.test_coverage_min
        st = self._status(coverage_pct, t)
        msg = ""
        if st is not MetricStatus.PASS:
            msg = f"Coverage {coverage_pct:.2f}% below minimum {t}"
        return MetricResult(
            metric_name=METRIC_TEST_COVERAGE,
            value=coverage_pct,
            threshold=t,
            status=st,
            message=msg,
        )

    # ----- measure_compliance_rate -----
    def measure_compliance_rate(
        self,
        *,
        gate_total: int = 0,
        gate_passed: int = 0,
    ) -> MetricResult:
        rate = gate_passed / gate_total if gate_total > 0 else 0.0
        t = self.thresholds.compliance_rate_min
        if gate_total == 0:
            return MetricResult(
                metric_name=METRIC_COMPLIANCE_RATE,
                value=1.0,
                threshold=t,
                status=MetricStatus.PASS,
                message="",
            )
        st = self._status(rate, t)
        msg = ""
        if st is not MetricStatus.PASS:
            msg = f"Compliance {rate:.2%} below minimum {t:.0%}"
        return MetricResult(
            metric_name=METRIC_COMPLIANCE_RATE,
            value=rate,
            threshold=t,
            status=st,
            message=msg,
        )

    # ----- measure_knowledge_activation_rate -----
    def measure_knowledge_activation_rate(
        self,
        *,
        ke_total: int = 0,
        ke_activated: int = 0,
    ) -> MetricResult:
        rate = ke_activated / ke_total if ke_total > 0 else 0.0
        t = self.thresholds.knowledge_activation_min
        st = self._status(rate, t)
        msg = ""
        if st is not MetricStatus.PASS:
            msg = f"KE activation {rate:.2%} below minimum {t:.0%}"
        return MetricResult(
            metric_name=METRIC_KNOWLEDGE_ACTIVATION,
            value=rate,
            threshold=t,
            status=st,
            message=msg,
        )

    # ----- measure_hallucination_interception_rate -----
    def measure_hallucination_interception_rate(
        self,
        *,
        hallucination_total: int = 0,
        hallucination_intercepted: int = 0,
    ) -> MetricResult:
        rate = hallucination_intercepted / hallucination_total if hallucination_total > 0 else 0.0
        t = self.thresholds.hallucination_interception_min
        if hallucination_total == 0:
            return MetricResult(
                metric_name=METRIC_HALLUCINATION_INTERCEPTION,
                value=0.0,
                threshold=t,
                status=MetricStatus.PASS,
                message="",
            )
        st = self._status(rate, t)
        msg = ""
        if st is not MetricStatus.PASS:
            msg = f"Hallucination interception {rate:.2%} below minimum {t:.0%}"
        return MetricResult(
            metric_name=METRIC_HALLUCINATION_INTERCEPTION,
            value=rate,
            threshold=t,
            status=st,
            message=msg,
        )

    # ----- run_all -----
    def run_all(self, inputs: FitnessInputs) -> FitnessReport:
        import time as _time

        dep_edges = inputs.dependency_edges
        if isinstance(dep_edges, list):
            dep_edges_count = len(dep_edges)
            edges_dummy = dep_edges if dep_edges else []
        else:
            dep_edges_count = dep_edges
            edges_dummy = [("_", "_") for _ in range(dep_edges_count)] if dep_edges_count > 0 else []

        metrics = [
            self.measure_module_coupling(
                edges_dummy,
                module_count=inputs.module_count,
            ),
            self.measure_test_coverage(inputs.coverage_pct),
            self.measure_compliance_rate(
                gate_total=inputs.gate_total,
                gate_passed=inputs.gate_passed,
            ),
            self.measure_knowledge_activation_rate(
                ke_total=inputs.ke_total,
                ke_activated=inputs.ke_activated,
            ),
            self.measure_hallucination_interception_rate(
                hallucination_total=inputs.hallucination_total,
                hallucination_intercepted=inputs.hallucination_intercepted,
            ),
        ]
        all_passed = all(m.status == MetricStatus.PASS for m in metrics)
        overall = MetricStatus.PASS
        for m in metrics:
            if m.status == MetricStatus.FAIL:
                overall = MetricStatus.FAIL
                break
            elif m.status == MetricStatus.WARN:
                overall = MetricStatus.WARN
        return FitnessReport(
            report_id=f"FF-{_time.time_ns()}",
            overall_status=overall,
            passed=all_passed,
            metrics=metrics,
        )

    @staticmethod
    def to_json_report(report: FitnessReport) -> str:
        import json as _json

        data = {
            "report_id": report.report_id,
            "overall_status": report.overall_status.value,
            "passed": report.passed,
            "metrics": [
                {
                    "metric_name": m.metric_name,
                    "value": m.value,
                    "threshold": m.threshold,
                    "status": m.status.value,
                    "message": m.message,
                }
                for m in report.metrics
            ],
        }
        return _json.dumps(data, default=str)

    @staticmethod
    def to_trend_data(reports: list[FitnessReport] | None = None) -> list[dict[str, object]]:
        import time as _time

        _reports = reports or []
        result: list[dict[str, object]] = []
        for report in _reports:
            row: dict[str, object] = {
                "timestamp": _time.time(),
                "overall_status": report.overall_status.value,
            }
            for m in report.metrics:
                row[m.metric_name] = m.value
            result.append(row)
        return result


def from_gate_results(
    rows: list[dict[str, Any]] | None = None,
    *,
    gate_total: int | None = None,
    gate_passed: int | None = None,
    coverage_pct: float | None = None,
    ke_total: int | None = None,
    ke_activated: int | None = None,
    hallucination_total: int | None = None,
    hallucination_intercepted: int | None = None,
    dependency_edges: int | None = None,
    module_count: int | None = None,
    **extra: Any,
) -> FitnessInputs:
    _rows = rows or []
    gt = gate_total if gate_total is not None else len(_rows)
    gp = gate_passed if gate_passed is not None else sum(1 for r in _rows if r.get("passed", False))
    return FitnessInputs(
        gate_total=gt,
        gate_passed=gp,
        coverage_pct=coverage_pct or 0.0,
        ke_total=ke_total or 0,
        ke_activated=ke_activated or 0,
        hallucination_total=hallucination_total or 0,
        hallucination_intercepted=hallucination_intercepted or 0,
        dependency_edges=dependency_edges or 0,
        module_count=module_count or 1,
    )


# --- legacy exports for backward compatibility ---


def fitness_anomaly_detection_precision(
    true_positives: int,
    false_positives: int,
) -> float:
    total = true_positives + false_positives
    return true_positives / total if total > 0 else 0.0


def fitness_false_positive_rate(
    false_positives: int,
    total_negatives: int,
) -> float:
    total = false_positives + total_negatives
    return false_positives / total if total > 0 else 0.0


def fitness_mtti_seconds(
    detection_timestamps: list[float],
    anomaly_timestamps: list[float],
) -> float:
    if not detection_timestamps or not anomaly_timestamps:
        return float("inf")
    delays = []
    for at in anomaly_timestamps:
        later = [d for d in detection_timestamps if d >= at]
        if later:
            delays.append(min(later) - at)
    return sum(delays) / len(delays) if delays else float("inf")


def fitness_owner_override_rate(
    overrides: int,
    total_owner_notifications: int,
) -> float:
    return overrides / total_owner_notifications if total_owner_notifications > 0 else 0.0
