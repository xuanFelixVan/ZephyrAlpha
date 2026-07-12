# [A_test] module_id: SRC-TST-1060 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_golden_test_external
# [INVARIANTS] pass_rate=1.0 when no results; evaluate returns False for unknown test_id
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_golden_test_external.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.golden_test_external import (
    GoldenTest,
    GoldenTestExternal,
)


class TestGoldenTestInstantiation:
    def test_construction(self):
        gt = GoldenTest(
            test_id="GT-001",
            input_symptoms={"cpu": "high"},
            expected_diagnosis="overload",
            expected_action="scale_up",
        )
        assert gt.test_id == "GT-001"
        assert gt.expected_diagnosis == "overload"


class TestGoldenTestExternalInstantiation:
    def test_default_construction(self):
        gte = GoldenTestExternal()
        assert gte.tests == []
        assert gte.results == {}

    def test_with_tests(self):
        gt = GoldenTest(test_id="GT-001", input_symptoms={}, expected_diagnosis="d", expected_action="a")
        gte = GoldenTestExternal(tests=[gt])
        assert len(gte.tests) == 1


class TestRegister:
    def test_register_single(self):
        gte = GoldenTestExternal()
        gt = GoldenTest(test_id="GT-001", input_symptoms={}, expected_diagnosis="d", expected_action="a")
        gte.register(gt)
        assert len(gte.tests) == 1
        assert gte.tests[0].test_id == "GT-001"

    def test_register_multiple(self):
        gte = GoldenTestExternal()
        for i in range(3):
            gte.register(GoldenTest(test_id=f"GT-{i}", input_symptoms={}, expected_diagnosis="d", expected_action="a"))
        assert len(gte.tests) == 3


class TestEvaluate:
    def test_matching_evaluation(self):
        gte = GoldenTestExternal()
        gte.register(
            GoldenTest(test_id="GT-001", input_symptoms={}, expected_diagnosis="overload", expected_action="scale")
        )
        result = gte.evaluate("GT-001", "overload", "scale")
        assert result is True
        assert gte.results["GT-001"] is True

    def test_mismatched_diagnosis(self):
        gte = GoldenTestExternal()
        gte.register(
            GoldenTest(test_id="GT-001", input_symptoms={}, expected_diagnosis="overload", expected_action="scale")
        )
        result = gte.evaluate("GT-001", "underload", "scale")
        assert result is False

    def test_mismatched_action(self):
        gte = GoldenTestExternal()
        gte.register(
            GoldenTest(test_id="GT-001", input_symptoms={}, expected_diagnosis="overload", expected_action="scale")
        )
        result = gte.evaluate("GT-001", "overload", "restart")
        assert result is False

    def test_unknown_test_id(self):
        gte = GoldenTestExternal()
        result = gte.evaluate("GT-999", "overload", "scale")
        assert result is False


class TestPassRate:
    def test_no_results(self):
        gte = GoldenTestExternal()
        assert gte.pass_rate() == pytest.approx(1.0)

    def test_all_pass(self):
        gte = GoldenTestExternal()
        gte.register(GoldenTest(test_id="GT-001", input_symptoms={}, expected_diagnosis="d", expected_action="a"))
        gte.evaluate("GT-001", "d", "a")
        assert gte.pass_rate() == pytest.approx(1.0)

    def test_mixed_results(self):
        gte = GoldenTestExternal()
        gte.register(GoldenTest(test_id="GT-001", input_symptoms={}, expected_diagnosis="d1", expected_action="a1"))
        gte.register(GoldenTest(test_id="GT-002", input_symptoms={}, expected_diagnosis="d2", expected_action="a2"))
        gte.evaluate("GT-001", "d1", "a1")
        gte.evaluate("GT-002", "wrong", "wrong")
        assert gte.pass_rate() == pytest.approx(0.5)
