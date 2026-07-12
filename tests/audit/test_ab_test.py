# [A_test] module_id: SRC-TST-0257 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_ab_test
# [INVARIANTS] lift = treatment_group - control_group
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_ab_test.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.ab_test import ABTest


class TestABTestInstantiation:
    def test_default_construction(self):
        ab = ABTest()
        assert ab.control_group == pytest.approx(0.0)
        assert ab.treatment_group == pytest.approx(0.0)

    def test_custom_construction(self):
        ab = ABTest(control_group=0.5, treatment_group=0.7)
        assert ab.control_group == pytest.approx(0.5)
        assert ab.treatment_group == pytest.approx(0.7)


class TestLift:
    def test_positive_lift(self):
        ab = ABTest(control_group=0.5, treatment_group=0.7)
        assert ab.lift == pytest.approx(0.2)

    def test_negative_lift(self):
        ab = ABTest(control_group=0.7, treatment_group=0.5)
        assert ab.lift == pytest.approx(-0.2)

    def test_zero_lift(self):
        ab = ABTest(control_group=0.5, treatment_group=0.5)
        assert ab.lift == pytest.approx(0.0)

    def test_default_lift(self):
        ab = ABTest()
        assert ab.lift == pytest.approx(0.0)

    def test_large_lift(self):
        ab = ABTest(control_group=0.0, treatment_group=1.0)
        assert ab.lift == pytest.approx(1.0)
