# [BLUEPRINT] MOD-SIM-027 | docs/03_modules/_domain_simulation/blueprint.md
# [A_module] module_id=MOD-SIM-027 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-SIM-027 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.simulation.test_volume_aware_impact
# [DOMAIN] D_SIMULATION
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/simulation/test_volume_aware_impact.py
# [TTL] task_bound
"""citrusquant volume-aware sqrt impact 单元测试(53号 §3.2 v2.0 候选).

覆盖 citrusquant PR 四条验收标准:
  ① 单调性(|Δw|增→impact增) ② zero/NaN volume fallback(impact=0不崩)
  ③ sign symmetry(买卖对称) ④ impact_coef=0 恒零(legacy flat 向后兼容)
另含: 公式正确性、批量形式、参数校验与退化。
"""

from __future__ import annotations

import math

import pytest

from zephyr.simulation.volume_aware_impact import (
    VolumeAwareImpactError,
    volume_aware_sqrt_impact,
    volume_aware_sqrt_impact_batch,
)


class TestFormula:
    def test_exact_value(self):
        # impact = 0.142 * sqrt(0.01*1e6/5e7) = 0.142*sqrt(0.0002)
        r = volume_aware_sqrt_impact(0.01, 1_000_000, 50_000_000, 0.142)
        assert r == pytest.approx(0.142 * math.sqrt(0.0002))

    def test_zero_delta_weight(self):
        assert volume_aware_sqrt_impact(0.0, 1e6, 5e7, 0.142) == 0.0


class TestAcceptanceCriteria:
    def test_1_monotonicity(self):
        impacts = [volume_aware_sqrt_impact(dw, 1e6, 5e7, 0.142) for dw in (0.001, 0.005, 0.01, 0.05, 0.1)]
        assert all(b > a for a, b in zip(impacts, impacts[1:]))

    def test_2_zero_volume_fallback(self):
        assert volume_aware_sqrt_impact(0.05, 1e6, 0.0, 0.142) == 0.0
        assert volume_aware_sqrt_impact(0.05, 1e6, -100.0, 0.142) == 0.0
        assert volume_aware_sqrt_impact(0.05, 1e6, float("nan"), 0.142) == 0.0
        assert volume_aware_sqrt_impact(0.05, 1e6, float("inf"), 0.142) == 0.0

    def test_3_sign_symmetry(self):
        buy = volume_aware_sqrt_impact(0.05, 1e6, 5e7, 0.142)
        sell = volume_aware_sqrt_impact(-0.05, 1e6, 5e7, 0.142)
        assert buy == sell
        assert buy > 0

    def test_4_zero_coef_legacy_compat(self):
        # impact_coef=0 → 恒 0(legacy flat slippage 行为逐位复现位)
        assert volume_aware_sqrt_impact(0.05, 1e6, 5e7, 0.0) == 0.0
        assert volume_aware_sqrt_impact(0.99, 1e6, 1.0, 0.0) == 0.0


class TestBatch:
    def test_batch_matches_scalar(self):
        dws = [0.01, -0.02, 0.05]
        dvs = [5e7, 3e7, 1e8]
        batch = volume_aware_sqrt_impact_batch(dws, 1e6, dvs, 0.142)
        scalar = [volume_aware_sqrt_impact(dw, 1e6, dv, 0.142) for dw, dv in zip(dws, dvs)]
        assert batch == pytest.approx(scalar)

    def test_batch_empty(self):
        assert volume_aware_sqrt_impact_batch([], 1e6, [], 0.142) == []

    def test_batch_length_mismatch(self):
        with pytest.raises(VolumeAwareImpactError):
            volume_aware_sqrt_impact_batch([0.01], 1e6, [5e7, 3e7], 0.142)


class TestValidation:
    def test_negative_notional(self):
        with pytest.raises(VolumeAwareImpactError):
            volume_aware_sqrt_impact(0.01, -1.0, 5e7, 0.142)

    def test_negative_coef(self):
        with pytest.raises(VolumeAwareImpactError):
            volume_aware_sqrt_impact(0.01, 1e6, 5e7, -0.1)

    def test_non_finite_delta_weight(self):
        with pytest.raises(VolumeAwareImpactError):
            volume_aware_sqrt_impact(float("nan"), 1e6, 5e7, 0.142)
        with pytest.raises(VolumeAwareImpactError):
            volume_aware_sqrt_impact(float("inf"), 1e6, 5e7, 0.142)

    def test_non_numeric(self):
        with pytest.raises(VolumeAwareImpactError):
            volume_aware_sqrt_impact("abc", 1e6, 5e7, 0.142)
        with pytest.raises(VolumeAwareImpactError):
            volume_aware_sqrt_impact(0.01, "big", 5e7, 0.142)
        with pytest.raises(VolumeAwareImpactError):
            volume_aware_sqrt_impact(0.01, 1e6, "big", 0.142)

    def test_error_code(self):
        assert VolumeAwareImpactError("x").error_code == "ZA-SIM-0027"
