# [A_test] module_id: SRC-TST-0963 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_fitness_functions
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.fitness_functions
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_fitness_functions.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.fitness_functions import (
    FitnessFunctionFramework,
    FitnessInputs,
    FitnessThresholds,
    MetricStatus,
    fitness_anomaly_detection_precision,
    fitness_false_positive_rate,
    fitness_mtti_seconds,
    fitness_owner_override_rate,
    from_gate_results,
)


class TestFitnessFunctionFrameworkInstantiation:
    def test_creates_with_defaults(self):
        framework = FitnessFunctionFramework()
        assert framework.thresholds.module_coupling_max == 0.30

    def test_creates_with_custom_thresholds(self):
        t = FitnessThresholds(module_coupling_max=0.5)
        framework = FitnessFunctionFramework(thresholds=t)
        assert framework.thresholds.module_coupling_max == 0.5


class TestMeasureModuleCoupling:
    def test_zero_edges(self):
        framework = FitnessFunctionFramework()
        result = framework.measure_module_coupling([], module_count=5)
        assert result.value == 0.0
        assert result.status == MetricStatus.PASS

    def test_high_coupling_fails(self):
        framework = FitnessFunctionFramework()
        edges = [(f"m{i}", f"m{j}") for i in range(5) for j in range(i + 1, 5)]
        result = framework.measure_module_coupling(edges, module_count=5)
        assert result.value > 0.3
        assert result.status in (MetricStatus.WARN, MetricStatus.FAIL)


class TestMeasureTestCoverage:
    def test_above_minimum(self):
        framework = FitnessFunctionFramework()
        result = framework.measure_test_coverage(80.0)
        assert result.status == MetricStatus.PASS

    def test_below_minimum(self):
        framework = FitnessFunctionFramework()
        result = framework.measure_test_coverage(30.0)
        assert result.status == MetricStatus.FAIL

    def test_boundary_zero(self):
        framework = FitnessFunctionFramework()
        result = framework.measure_test_coverage(0.0)
        assert result.status == MetricStatus.FAIL


class TestMeasureComplianceRate:
    def test_full_compliance(self):
        framework = FitnessFunctionFramework()
        result = framework.measure_compliance_rate(gate_total=10, gate_passed=10)
        assert result.status == MetricStatus.PASS

    def test_zero_gates_passes(self):
        framework = FitnessFunctionFramework()
        result = framework.measure_compliance_rate(gate_total=0, gate_passed=0)
        assert result.status == MetricStatus.PASS

    def test_low_compliance(self):
        framework = FitnessFunctionFramework()
        result = framework.measure_compliance_rate(gate_total=10, gate_passed=5)
        assert result.status == MetricStatus.FAIL


class TestRunAll:
    def test_all_passing(self):
        framework = FitnessFunctionFramework()
        inputs = FitnessInputs(
            dependency_edges=0,
            module_count=1,
            coverage_pct=80.0,
            gate_total=10,
            gate_passed=10,
            ke_total=10,
            ke_activated=5,
            hallucination_total=10,
            hallucination_intercepted=8,
        )
        report = framework.run_all(inputs)
        assert report.passed is True


class TestFromGateResults:
    def test_creates_inputs_from_rows(self):
        rows = [{"passed": True}, {"passed": False}]
        inputs = from_gate_results(rows)
        assert inputs.gate_total == 2
        assert inputs.gate_passed == 1


class TestLegacyFunctions:
    def test_precision(self):
        assert fitness_anomaly_detection_precision(8, 2) == 0.8
        assert fitness_anomaly_detection_precision(0, 0) == 0.0

    def test_false_positive_rate(self):
        assert fitness_false_positive_rate(2, 8) == 0.2
        assert fitness_false_positive_rate(0, 10) == 0.0

    def test_mtti(self):
        assert fitness_mtti_seconds([10.0, 20.0], [5.0, 15.0]) == 5.0
        assert fitness_mtti_seconds([], []) == float("inf")

    def test_owner_override_rate(self):
        assert fitness_owner_override_rate(3, 10) == 0.3
        assert fitness_owner_override_rate(0, 0) == 0.0
