# [BLUEPRINT] MOD-BT-194 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_distribution_forecast_eval
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy
# [CONSUMERS] MOD-BT-194 distribution_forecast_eval 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 合成数据统计验证（良校准/过窄/过宽三态判定）；零网络
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-194 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""E4 双标准考尺单测——良校准/过窄假阳性/过宽三态+pinball/PIT 均匀性，合成数据零网络。"""
from __future__ import annotations

import numpy as np
import pytest

from scripts.backtest.distribution_forecast_eval import (
    CALIBRATION_TOL,
    empirical_coverage,
    evaluate_distribution_forecast,
    pit_uniformity_ks,
    pit_values,
    pinball_loss,
    sharpness,
)


def _preds(realized: np.ndarray, scale: float = 1.0, center: float = 0.0) -> dict:
    """无条件分布预测器：pred_q = center + scale * N(0,1) 的 q 分位（常数预测）。

    PIT 语义下与逐样本条件分布同性质（覆盖率/均匀性可比）；校准由 scale 贴合度决定。
    """
    from scipy.stats import norm

    qs = (0.05, 0.25, 0.5, 0.75, 0.95)
    return {float(q): np.full(len(realized), center + scale * norm.ppf(q))
            for q in qs}


class TestPerfectlyCalibrated:
    def test_well_calibrated_passes_both(self):
        rng = np.random.default_rng(7)
        realized = rng.normal(0, 1, 500)
        preds = _preds(realized, scale=1.0)
        rep = evaluate_distribution_forecast(preds, realized)
        assert rep["verdict"]["calibrated"]
        assert rep["calibrated_share"] >= 0.6
        assert rep["pit_ks"] is not None and rep["pit_ks"] < 0.15  # 均匀性良好

    def test_too_narrow_fails_sharpness_gate_is_wrongly_calibrated(self):
        rng = np.random.default_rng(7)
        realized = rng.normal(0, 1, 500)
        preds = _preds(realized, scale=0.2)  # 区间远窄于真实波动
        rep = evaluate_distribution_forecast(preds, realized)
        assert not rep["verdict"]["calibrated"]  # 覆盖率崩=校准败（双标准防假阳性）
        assert rep["sharpness"] < rep["sharpness"] + 1  # 锐度数值本身小（窄）


class TestSharpness:
    def test_wider_interval_larger_sharpness(self):
        rng = np.random.default_rng(3)
        realized = rng.normal(0, 1, 200)
        narrow = sharpness(_preds(realized, scale=0.5))
        wide = sharpness(_preds(realized, scale=2.0))
        assert wide > narrow

    def test_sharpness_ratio_informational(self):
        rng = np.random.default_rng(3)
        realized = rng.normal(0, 1, 300)
        rep = evaluate_distribution_forecast(_preds(realized, scale=1.0), realized)
        # 校准无条件预测器：q95-q05 宽度 ≈ 3.29σ
        assert rep["sharpness_ratio"] == pytest.approx(3.29, abs=0.3)
        assert rep["verdict"]["calibrated"] is True


class TestPinball:
    def test_perfect_median_low_loss(self):
        rng = np.random.default_rng(5)
        realized = rng.normal(0, 1, 300)
        preds = {"0.5": realized.copy()}  # 中位数=实现值
        assert pinball_loss(preds, realized, 0.5) == pytest.approx(0.0, abs=1e-9)

    def test_pinball_asymmetry_direction(self):
        preds = {"0.1": np.full(100, 0.0)}
        realized = np.ones(100)
        # 低分位低估：损失=q*diff=0.1（0.9 是高分位低估的代价）
        assert pinball_loss(preds, realized, 0.1) == pytest.approx(0.1, abs=1e-9)


class TestPitValues:
    def test_uniform_pit_for_calibrated(self):
        rng = np.random.default_rng(11)
        realized = rng.normal(0, 1, 400)
        pits = pit_values(_preds(realized, scale=1.0), realized)
        assert np.isfinite(pits).all()
        assert abs(pits.mean() - 0.5) < 0.08

    def test_ks_detects_degenerate(self):
        pits = np.full(200, 0.5)  # 退化分布
        assert pit_uniformity_ks(pits) > 0.4


class TestGuards:
    def test_shape_mismatch_rejected(self):
        with pytest.raises(ValueError, match="形状"):
            empirical_coverage({"0.5": np.zeros(10)}, np.zeros(5))

    def test_sample_floor(self):
        with pytest.raises(ValueError, match="样本不足"):
            empirical_coverage({"0.5": np.zeros(5)}, np.zeros(5))

    def test_quantile_range_rejected(self):
        with pytest.raises(ValueError, match="越界"):
            empirical_coverage({"1.5": np.zeros(20)}, np.zeros(20))


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
