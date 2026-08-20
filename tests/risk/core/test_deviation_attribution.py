# [BLUEPRINT] MOD-RK-23 | docs/03_modules/_domain_risk/strategy_deviation_monitor/blueprint.md
# [MODULE] tests.risk.core.test_deviation_attribution
# [DOMAIN] D_RISK
# [INVARIANTS] 加性恒等; NaN/inf拒绝; 残差轧差; 只读纯计算
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDeviationDecompositionError
# [TESTS] self
# [TTL] permanent
"""偏离归因分解 H-A~D 四因子测试（55 号 §6 暂缓项，AI-NIGHT-001 包P）。"""

from __future__ import annotations

import pytest

from zephyr.risk.core.deviation_attribution import (
    InvalidDeviationDecompositionError,
    decompose_deviation,
)


class TestDecomposition:
    def test_additive_identity_always_holds(self):
        result = decompose_deviation(
            total_deviation=-0.045,
            execution_cost_drag=-0.012,
            timing_lag=-0.008,
            position_weight_pairs=[(0.05, 0.10), (-0.03, -0.20)],
        )
        # H-C = 0.05×0.10 + (-0.03)×(-0.20) = 0.005 + 0.006 = 0.011
        assert result["factors"]["H_C"] == pytest.approx(0.011)
        # H-D = -0.045 - (-0.012 - 0.008 + 0.011) = -0.036
        assert result["factors"]["H_D"] == pytest.approx(-0.036)
        assert result["invariant_status"] == "PASS"
        assert result["sum_check"] == pytest.approx(-0.045)

    def test_dominant_factor(self):
        result = decompose_deviation(
            total_deviation=-0.05,
            execution_cost_drag=-0.04,
            timing_lag=-0.005,
            position_weight_pairs=[],
        )
        assert result["dominant_factor"] == "H_A"

    def test_residual_dominant_flags_unexplained(self):
        result = decompose_deviation(
            total_deviation=-0.10,
            execution_cost_drag=-0.01,
            timing_lag=-0.01,
            position_weight_pairs=[],
        )
        assert result["dominant_factor"] == "H_D"
        assert result["shares"]["H_D"] == pytest.approx(0.8)

    def test_zero_total_degenerate(self):
        result = decompose_deviation(
            total_deviation=0.0,
            execution_cost_drag=0.0,
            timing_lag=0.0,
            position_weight_pairs=[],
        )
        assert result["invariant_status"] == "PASS"
        assert all(v == 0.0 for v in result["shares"].values())

    def test_position_weight_pairs_math(self):
        result = decompose_deviation(
            total_deviation=0.02,
            execution_cost_drag=0.0,
            timing_lag=0.0,
            position_weight_pairs=[(0.10, 0.20)],  # 超配 10% 的标的涨 20% → +2%
        )
        assert result["factors"]["H_C"] == pytest.approx(0.02)
        assert result["factors"]["H_D"] == pytest.approx(0.0)

    def test_nan_rejected(self):
        with pytest.raises(InvalidDeviationDecompositionError):
            decompose_deviation(float("nan"), 0.0, 0.0, [])

    def test_inf_rejected(self):
        with pytest.raises(InvalidDeviationDecompositionError):
            decompose_deviation(0.0, float("inf"), 0.0, [])

    def test_nan_in_weight_pair_rejected(self):
        with pytest.raises(InvalidDeviationDecompositionError):
            decompose_deviation(0.0, 0.0, 0.0, [(float("nan"), 0.1)])

    def test_malformed_pair_rejected(self):
        with pytest.raises(InvalidDeviationDecompositionError):
            decompose_deviation(0.0, 0.0, 0.0, [(0.1,)])  # 缺 symbol_return
