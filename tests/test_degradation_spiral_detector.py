# [A_test] module_id: SRC-TST-0727 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md | §test
# [MODULE] tests.test_degradation_spiral_detector
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_degradation_spiral_detector.py

import pytest

mod = pytest.importorskip(
    "zephyr.ops.capacity_assurance.degradation_spiral_detector", reason="degradation_spiral_detector not available"
)
DegradationSpiralDetector = mod.DegradationSpiralDetector


class TestDegradationSpiralDetector:
    def test_instantiation(self):
        dsd = DegradationSpiralDetector()
        assert dsd._baseline_set is False

    def test_set_baseline(self):
        dsd = DegradationSpiralDetector()
        dsd.set_baseline(1000.0)
        assert dsd._baseline_set is True
        assert dsd._baseline_tokens == 1000.0

    def test_detect_no_spiral(self):
        dsd = DegradationSpiralDetector()
        dsd.set_baseline(1000.0)
        result = dsd.detect(0.05, 1500)
        assert result["spiral_detected"] is False
        assert result["require_intervention"] is False

    def test_detect_spiral(self):
        dsd = DegradationSpiralDetector()
        dsd.set_baseline(1000.0)
        result = dsd.detect(0.5, 3000)
        assert result["spiral_detected"] is True
        assert result["spiral_coefficient"] > 1.0

    def test_detect_high_hallucination_no_baseline(self):
        dsd = DegradationSpiralDetector()
        result = dsd.detect(0.15, 3000)
        assert result["spiral_detected"] is False

    def test_detect_low_hallucination(self):
        dsd = DegradationSpiralDetector()
        dsd.set_baseline(1000.0)
        result = dsd.detect(0.05, 3000)
        assert result["spiral_detected"] is False

    def test_detect_zero_baseline(self):
        dsd = DegradationSpiralDetector()
        dsd.set_baseline(0)
        result = dsd.detect(0.15, 3000)
        assert result["spiral_detected"] is False

    def test_sli_id_constant(self):
        assert DegradationSpiralDetector.SLI_ID == "CAP-SPI-001"

    def test_thresholds(self):
        assert DegradationSpiralDetector.HALLUCINATION_THRESHOLD == 0.10
        assert DegradationSpiralDetector.TOKEN_MULTIPLIER_THRESHOLD == 2.0
        assert DegradationSpiralDetector.SPIRAL_COEFFICIENT_THRESHOLD == 1.5
