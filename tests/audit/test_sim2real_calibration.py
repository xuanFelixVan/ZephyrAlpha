# [A_test] module_id: SRC-TST-1601 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_sim2real_calibration
# [INVARIANTS] gap = |sim_accuracy - real_accuracy|
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_sim2real_calibration.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.sim2real_calibration import Sim2RealCalibration


class TestSim2RealCalibrationInstantiation:
    def test_default_construction(self):
        s2r = Sim2RealCalibration()
        assert s2r.sim_accuracy == pytest.approx(0.0)
        assert s2r.real_accuracy == pytest.approx(0.0)

    def test_custom_params(self):
        s2r = Sim2RealCalibration(sim_accuracy=0.9, real_accuracy=0.85)
        assert s2r.sim_accuracy == pytest.approx(0.9)
        assert s2r.real_accuracy == pytest.approx(0.85)


class TestGap:
    def test_zero_gap(self):
        s2r = Sim2RealCalibration(sim_accuracy=0.8, real_accuracy=0.8)
        assert s2r.gap == pytest.approx(0.0)

    def test_positive_gap(self):
        s2r = Sim2RealCalibration(sim_accuracy=0.9, real_accuracy=0.7)
        assert s2r.gap == pytest.approx(0.2)

    def test_negative_gap_absolute(self):
        s2r = Sim2RealCalibration(sim_accuracy=0.5, real_accuracy=0.8)
        assert s2r.gap == pytest.approx(0.3)

    def test_default_gap(self):
        s2r = Sim2RealCalibration()
        assert s2r.gap == pytest.approx(0.0)

    def test_extreme_gap(self):
        s2r = Sim2RealCalibration(sim_accuracy=1.0, real_accuracy=0.0)
        assert s2r.gap == pytest.approx(1.0)
