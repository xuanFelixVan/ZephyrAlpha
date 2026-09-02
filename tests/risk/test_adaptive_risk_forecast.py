# [BLUEPRINT] MOD-RK-28 | docs/03_modules/_domain_risk/adaptive_risk_forecast/blueprint.md | §test
# [A_test] module_id: MOD-RK-28 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AdaptiveRiskForecast 单元测试 (MOD-RK-28, MVP)。

覆盖: 条件PDF VaR/CVaR 产出 / 共形缓冲叠加 / 无校准降级 / 条件桶回退 degraded /
限额对照 limit_scale/limit_breached / sit_out 预判 / Fail-Closed 配置校验 /
frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from zephyr.risk.core.adaptive_risk_forecast import (
    ForwardVarConfig,
    ForwardVarForecast,
    InvalidForwardVarConfigError,
    forecast_forward_var,
)


def _calm_returns(n: int = 120) -> list[float]:
    """低波动收益序列 (std≈0.5%)。"""
    rng = np.random.default_rng(42)
    return (rng.normal(0.0005, 0.005, n)).tolist()


def _crashy_returns(n: int = 120) -> list[float]:
    """重尾亏损序列 (含 -6% 极端亏损)。"""
    rng = np.random.default_rng(7)
    base = rng.normal(-0.002, 0.02, n)
    base[::10] = -0.06
    return base.tolist()


# ── 基本产出 ──────────────────────────────────────────────────────────────────


def test_basic_forecast_fields() -> None:
    fc = forecast_forward_var(_calm_returns())
    assert isinstance(fc, ForwardVarForecast)
    assert fc.var_pct > 0.0
    assert fc.cvar_pct >= fc.var_pct
    assert fc.conformal_var_pct >= fc.var_pct
    assert fc.n_samples == 120
    assert 0.0 < fc.limit_scale <= 1.0


def test_cvar_not_less_than_var() -> None:
    fc = forecast_forward_var(_crashy_returns())
    assert fc.cvar_pct >= fc.var_pct - 1e-12


# ── 共形缓冲 ──────────────────────────────────────────────────────────────────


def test_conformal_margin_added_when_calibrated() -> None:
    returns = _calm_returns()
    # 校准残差偏大 (预测恒 0, 实际=收益) → margin > 0
    fc = forecast_forward_var(
        returns,
        calibration_predictions=[0.0] * 80,
        calibration_actuals=_crashy_returns(80),
    )
    assert fc.conformal_margin_pct > 0.0
    assert fc.conformal_var_pct == pytest.approx(fc.var_pct + fc.conformal_margin_pct)
    assert fc.n_calibration == 80
    assert fc.degraded is False


def test_no_calibration_degrades() -> None:
    fc = forecast_forward_var(_calm_returns())
    assert fc.conformal_margin_pct == 0.0
    assert fc.n_calibration == 0
    assert fc.degraded is True


# ── 条件桶 ──────────────────────────────────────────────────────────────────


def test_condition_bucket_fallback_degraded() -> None:
    returns = _calm_returns(100)
    conditions = ["LOW"] * 95 + ["HIGH"] * 5  # HIGH 桶仅 5 样本 < min_samples
    cfg = ForwardVarConfig(density_min_samples=60)
    fc = forecast_forward_var(returns, conditions=conditions, condition="HIGH", config=cfg)
    assert fc.degraded is True


def test_high_vol_bucket_has_larger_var() -> None:
    rng = np.random.default_rng(11)
    low = rng.normal(0.0, 0.004, 100).tolist()
    high = rng.normal(0.0, 0.03, 100).tolist()
    returns = low + high
    conditions = ["LOW"] * 100 + ["HIGH"] * 100
    cfg = ForwardVarConfig(density_min_samples=60)
    # 提供共形校准 → degraded 仅反映条件桶是否回退
    cal_p = [0.0] * 60
    cal_a = rng.normal(0.0, 0.01, 60).tolist()
    fc_high = forecast_forward_var(
        returns,
        conditions=conditions,
        condition="HIGH",
        calibration_predictions=cal_p,
        calibration_actuals=cal_a,
        config=cfg,
    )
    fc_low = forecast_forward_var(
        returns,
        conditions=conditions,
        condition="LOW",
        calibration_predictions=cal_p,
        calibration_actuals=cal_a,
        config=cfg,
    )
    assert fc_high.degraded is False
    assert fc_high.var_pct > fc_low.var_pct


# ── 限额对照 ──────────────────────────────────────────────────────────────────


def test_limit_breach_scales_down() -> None:
    cfg = ForwardVarConfig(var_limit_pct=0.02)
    fc = forecast_forward_var(_crashy_returns(), config=cfg)
    assert fc.limit_breached is True
    assert fc.limit_scale == pytest.approx(min(1.0, 0.02 / fc.conformal_var_pct))
    assert fc.limit_scale < 1.0


def test_calm_series_no_breach() -> None:
    cfg = ForwardVarConfig(var_limit_pct=0.20)
    fc = forecast_forward_var(_calm_returns(), config=cfg)
    assert fc.limit_breached is False
    assert fc.limit_scale == 1.0


# ── sit_out 预判 ──────────────────────────────────────────────────────────────


def test_sit_out_triggered_on_extreme_var() -> None:
    cfg = ForwardVarConfig(sit_out_var_pct=0.04)
    fc = forecast_forward_var(_crashy_returns(), config=cfg)
    assert fc.sit_out is True


def test_sit_out_not_triggered_on_calm() -> None:
    fc = forecast_forward_var(_calm_returns())
    assert fc.sit_out is False


# ── Fail-Closed 校验 ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "kwargs",
    [
        {"var_level": 1.5},
        {"var_level": 0.0},
        {"conformal_alpha": 0.0},
        {"conformal_alpha": 1.0},
        {"var_limit_pct": 0.0},
        {"var_limit_pct": -0.01},
        {"sit_out_var_pct": 0.0},
        {"density_window": 0},
        {"density_min_samples": 0},
    ],
)
def test_invalid_config_fail_closed(kwargs: dict) -> None:
    with pytest.raises(InvalidForwardVarConfigError):
        ForwardVarConfig(**kwargs)


def test_too_short_returns_raises() -> None:
    with pytest.raises(ValueError):
        forecast_forward_var([0.01])


def test_calibration_length_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        forecast_forward_var(
            _calm_returns(),
            calibration_predictions=[0.0] * 5,
            calibration_actuals=[0.0] * 6,
        )


# ── 不可变 ────────────────────────────────────────────────────────────────────


def test_result_frozen() -> None:
    fc = forecast_forward_var(_calm_returns())
    with pytest.raises(dataclasses.FrozenInstanceError):
        fc.var_pct = 9.9  # type: ignore[misc]
