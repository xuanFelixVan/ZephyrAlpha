# [BLUEPRINT] MOD-RK-05 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""VaRCalculator 单元测试 (MOD-RK-05, Phase 1)。"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest
from scipy.stats import norm

from zephyr.risk.core.var_calculator import (
    InsufficientVaRHistoryError,
    InvalidVaRConfigError,
    VaRCalculator,
    VaRConfig,
    VaRMethod,
    VaRResult,
)

NAV = 1_000_000.0
T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


# ── 固定随机种子保证可复现 ──
@pytest.fixture(autouse=True)
def _seed():
    np.random.seed(42)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_invalid_confidence_zero():
    with pytest.raises(InvalidVaRConfigError):
        VaRConfig(confidence_level=0.0)


def test_config_invalid_confidence_above_one():
    with pytest.raises(InvalidVaRConfigError):
        VaRConfig(confidence_level=1.5)


def test_config_invalid_holding_period():
    with pytest.raises(InvalidVaRConfigError):
        VaRConfig(holding_period_days=0)


def test_config_z_alpha_95():
    cfg = VaRConfig(confidence_level=0.95)
    assert cfg.z_alpha == pytest.approx(1.6449, abs=1e-3)


def test_config_z_alpha_99():
    cfg = VaRConfig(confidence_level=0.99)
    assert cfg.z_alpha == pytest.approx(2.3263, abs=1e-3)


def test_config_min_history_must_be_ge_2():
    with pytest.raises(InvalidVaRConfigError):
        VaRConfig(min_history=1)


# ── 参数法 ────────────────────────────────────────────────────────────────────


def test_parametric_method_basic():
    """参数法: 正态分布收益, VaR ≈ z·σ·V (mean≈0)。"""
    cfg = VaRConfig(confidence_level=0.95, method=VaRMethod.PARAMETRIC, min_history=50)
    calc = VaRCalculator(cfg)
    # 构造 mean≈0, std=0.01 的 200 日收益
    returns = np.random.normal(0.0, 0.01, 200)
    result = calc.calculate(returns, NAV, now=T0)
    assert result.method is VaRMethod.PARAMETRIC
    assert result.parametric_var is not None
    assert result.historical_var is None
    # 期望 ≈ 1.6449 * 0.01 * 1e6 ≈ 16449
    assert result.value == pytest.approx(16449, rel=0.15)
    assert result.value > 0


def test_parametric_floor_at_zero_when_high_mean():
    """高均值低波动: z·σ - μ < 0 → VaR 取 0 下限。"""
    cfg = VaRConfig(confidence_level=0.95, method=VaRMethod.PARAMETRIC, min_history=30)
    calc = VaRCalculator(cfg)
    # 均值 0.05 (日 5%!), std 0.001 → z·σ 远小于 μ
    returns = np.random.normal(0.05, 0.001, 100)
    result = calc.calculate(returns, NAV, now=T0)
    assert result.value == pytest.approx(0.0, abs=1e-6)


def test_parametric_99_higher_than_95():
    """99% VaR 应高于 95% VaR。"""
    returns = np.random.normal(0.0, 0.02, 300)
    calc95 = VaRCalculator(VaRConfig(confidence_level=0.95, method=VaRMethod.PARAMETRIC))
    calc99 = VaRCalculator(VaRConfig(confidence_level=0.99, method=VaRMethod.PARAMETRIC))
    r95 = calc95.calculate(returns, NAV)
    r99 = calc99.calculate(returns, NAV)
    assert r99.value > r95.value


def test_parametric_multi_day_scaling():
    """多日 VaR ≈ 日 VaR · sqrt(T)。"""
    cfg1 = VaRConfig(confidence_level=0.95, method=VaRMethod.PARAMETRIC, holding_period_days=1)
    cfg10 = VaRConfig(confidence_level=0.95, method=VaRMethod.PARAMETRIC, holding_period_days=10)
    returns = np.random.normal(0.0, 0.01, 200)
    r1 = VaRCalculator(cfg1).calculate(returns, NAV)
    r10 = VaRCalculator(cfg10).calculate(returns, NAV)
    # 10日 ≈ 1日 · sqrt(10)
    assert r10.value == pytest.approx(r1.value * np.sqrt(10), rel=0.05)


# ── 历史模拟法 ────────────────────────────────────────────────────────────────


def test_historical_method_basic():
    """历史模拟法: VaR = -quantile(r, 0.05)·V。"""
    cfg = VaRConfig(confidence_level=0.95, method=VaRMethod.HISTORICAL, min_history=50)
    calc = VaRCalculator(cfg)
    returns = np.random.normal(0.0, 0.01, 500)
    result = calc.calculate(returns, NAV, now=T0)
    assert result.method is VaRMethod.HISTORICAL
    assert result.historical_var is not None
    assert result.parametric_var is None
    expected_q = np.quantile(returns, 0.05)
    assert result.value == pytest.approx(-expected_q * NAV, rel=1e-9)
    assert result.value > 0


def test_historical_captures_tail_better_than_parametric():
    """厚尾分布: 历史模拟法应比参数法给出更高 VaR (尾部更肥)。"""
    # 自由度 3 的 t 分布 (厚尾)
    returns = np.random.standard_t(3, 2000) * 0.01
    calc_p = VaRCalculator(VaRConfig(confidence_level=0.99, method=VaRMethod.PARAMETRIC))
    calc_h = VaRCalculator(VaRConfig(confidence_level=0.99, method=VaRMethod.HISTORICAL))
    rp = calc_p.calculate(returns, NAV)
    rh = calc_h.calculate(returns, NAV)
    # 厚尾下历史模拟通常 ≥ 参数法 (允许相等容差)
    assert rh.value >= rp.value * 0.95


# ── conservative_max (默认) ──────────────────────────────────────────────────


def test_conservative_max_takes_maximum():
    """conservative_max = max(parametric, historical)。"""
    cfg = VaRConfig(confidence_level=0.95, method=VaRMethod.CONSERVATIVE_MAX)
    calc = VaRCalculator(cfg)
    returns = np.random.normal(0.0, 0.01, 200)
    result = calc.calculate(returns, NAV, now=T0)
    assert result.method is VaRMethod.CONSERVATIVE_MAX
    assert result.parametric_var is not None
    assert result.historical_var is not None
    assert result.value == pytest.approx(
        max(result.parametric_var, result.historical_var)
    )


def test_default_method_is_conservative_max():
    calc = VaRCalculator()
    assert calc.config.method is VaRMethod.CONSERVATIVE_MAX


def test_default_confidence_is_95():
    calc = VaRCalculator()
    assert calc.config.confidence_level == 0.95


# ── 多资产组合 ────────────────────────────────────────────────────────────────


def test_calculate_portfolio_two_assets():
    """多资产组合: 组合收益 = weights @ asset_returns。"""
    calc = VaRCalculator(VaRConfig(confidence_level=0.95, method=VaRMethod.PARAMETRIC))
    # 两资产, 200 日
    asset_returns = np.random.normal(0.0, 0.01, (200, 2))
    weights = np.array([0.6, 0.4])
    result = calc.calculate_portfolio(asset_returns, weights, NAV, now=T0)
    # 组合收益 = 0.6*r1 + 0.4*r2, 应等于手动合成
    synthetic = asset_returns @ weights
    expected = VaRCalculator(VaRConfig(confidence_level=0.95, method=VaRMethod.PARAMETRIC)).calculate(
        synthetic, NAV
    )
    assert result.value == pytest.approx(expected.value, rel=1e-9)


def test_calculate_portfolio_weight_shape_mismatch_raises():
    calc = VaRCalculator()
    asset_returns = np.random.normal(0.0, 0.01, (100, 3))
    weights = np.array([0.5, 0.5])  # 只有两个, 应为 3
    with pytest.raises(InvalidVaRConfigError):
        calc.calculate_portfolio(asset_returns, weights, NAV)


def test_calculate_portfolio_1d_returns_raises():
    calc = VaRCalculator()
    returns = np.random.normal(0.0, 0.01, 100)
    weights = np.array([0.5, 0.5])
    with pytest.raises(InvalidVaRConfigError):
        calc.calculate_portfolio(returns, weights, NAV)


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_insufficient_history_raises():
    cfg = VaRConfig(min_history=100, method=VaRMethod.HISTORICAL)
    calc = VaRCalculator(cfg)
    returns = np.random.normal(0.0, 0.01, 50)  # < 100
    with pytest.raises(InsufficientVaRHistoryError):
        calc.calculate(returns, NAV)


def test_nan_returns_filtered():
    """NaN 收益应被过滤, 剩余样本足够则正常计算。"""
    cfg = VaRConfig(min_history=50, method=VaRMethod.PARAMETRIC)
    calc = VaRCalculator(cfg)
    returns = np.random.normal(0.0, 0.01, 100)
    returns[:10] = np.nan  # 10 个 NaN, 剩余 90 >= 50
    result = calc.calculate(returns, NAV, now=T0)
    assert result.sample_size == 90
    assert result.value > 0


def test_non_positive_portfolio_value_raises():
    calc = VaRCalculator()
    returns = np.random.normal(0.0, 0.01, 100)
    with pytest.raises(InvalidVaRConfigError):
        calc.calculate(returns, 0.0)
    with pytest.raises(InvalidVaRConfigError):
        calc.calculate(returns, -1.0)


def test_2d_returns_raises():
    calc = VaRCalculator()
    returns = np.random.normal(0.0, 0.01, (100, 2))
    with pytest.raises(InvalidVaRConfigError):
        calc.calculate(returns, NAV)


# ── 结果属性 ──────────────────────────────────────────────────────────────────


def test_result_value_pct():
    calc = VaRCalculator(VaRConfig(method=VaRMethod.PARAMETRIC))
    returns = np.random.normal(0.0, 0.01, 200)
    result = calc.calculate(returns, NAV, now=T0)
    assert result.value_pct == pytest.approx(result.value / NAV)


def test_result_annualized_vol():
    calc = VaRCalculator(VaRConfig(method=VaRMethod.PARAMETRIC))
    returns = np.random.normal(0.0, 0.01, 200)
    result = calc.calculate(returns, NAV, now=T0)
    # 年化波动率 = std * sqrt(252)
    assert result.annualized_vol == pytest.approx(result.std_return * np.sqrt(252))


def test_result_annualized_vol_uses_config_factor():
    """annualization_factor 配置必须被 annualized_vol 消费 (默认 252, 可调如 244)。"""
    calc = VaRCalculator(VaRConfig(method=VaRMethod.PARAMETRIC, annualization_factor=244))
    returns = np.random.normal(0.0, 0.01, 200)
    result = calc.calculate(returns, NAV, now=T0)
    assert result.annualization_factor == 244
    assert result.annualized_vol == pytest.approx(result.std_return * np.sqrt(244))


def test_result_to_dict_contains_all_fields():
    calc = VaRCalculator()
    returns = np.random.normal(0.0, 0.01, 200)
    result = calc.calculate(returns, NAV, now=T0)
    d = result.to_dict()
    for key in (
        "value", "value_pct", "method", "confidence_level", "holding_period_days",
        "parametric_var", "historical_var", "portfolio_value", "mean_return",
        "std_return", "sample_size", "annualized_vol",
    ):
        assert key in d
    assert d["method"] == "conservative_max"


def test_result_var_non_negative():
    """VaR 始终非负。"""
    calc = VaRCalculator()
    # 多种收益分布
    for _ in range(10):
        returns = np.random.normal(0.0, 0.005, 200)
        result = calc.calculate(returns, NAV, now=T0)
        assert result.value >= 0.0
