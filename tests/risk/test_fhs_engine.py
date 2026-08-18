# [BLUEPRINT] MOD-RK-26 | docs/03_modules/_domain_risk/fhs_engine/blueprint.md | §test
# [A_test] module_id: MOD-RK-26 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FHSEngine 单元测试 (MOD-RK-26, MVP)。

覆盖: GARCH(1,1) QMLE 拟合 / 残差重采样 / FHS VaR-ES 输出 / 历史模拟法对照
合理性 / 不收敛回退 (memo 36 §3.16) / 小样本守卫 / Fail-Closed 输入校验 /
ES>=VaR 不变式 / 种子可复现性。
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from zephyr.risk.core.fhs_engine import (
    ExcessiveFHSNonFiniteDataError,
    FHSConfig,
    FHSEngine,
    FHSMethod,
    FHSResult,
    GarchConvergenceError,
    InsufficientFHSHistoryError,
    InvalidFHSConfigError,
)

NAV = 1_000_000.0
T0 = datetime(2026, 8, 18, 10, 0, tzinfo=timezone.utc)


# ── 测试数据生成器 ─────────────────────────────────────────────────────────────


def _make_garch_series(
    n: int,
    omega: float = 2e-6,
    alpha: float = 0.10,
    beta: float = 0.85,
    seed: int = 7,
    burn: int = 200,
) -> np.ndarray:
    """生成已知参数的 GARCH(1,1) 序列 (正态创新)。"""
    rng = np.random.default_rng(seed)
    total = n + burn
    eps = np.zeros(total)
    sig2 = np.zeros(total)
    sig2[0] = omega / (1.0 - alpha - beta)
    z = rng.standard_normal(total)
    for t in range(1, total):
        sig2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sig2[t - 1]
        eps[t] = np.sqrt(sig2[t]) * z[t]
    return eps[burn:]


def _make_regime_shift(seed: int = 1) -> np.ndarray:
    """低波动 200 日 + 高波动 30 日 (近期波动聚集)。"""
    rng = np.random.default_rng(seed)
    calm = rng.normal(0.0, 0.008, 200)
    storm = rng.normal(0.0, 0.03, 30)
    return np.concatenate([calm, storm])


def _make_iid_normal(n: int = 250, sigma: float = 0.015, seed: int = 11) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, sigma, n)


@pytest.fixture()
def engine() -> FHSEngine:
    return FHSEngine(FHSConfig(random_seed=42))


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_defaults():
    cfg = FHSConfig()
    assert cfg.confidence_level == 0.95
    assert cfg.holding_period_days == 1
    assert cfg.min_history == 30
    assert cfg.garch_min_history == 60
    assert cfg.n_simulations == 10_000
    assert cfg.fallback_to_historical is True


def test_config_invalid_confidence():
    with pytest.raises(InvalidFHSConfigError):
        FHSConfig(confidence_level=0.0)
    with pytest.raises(InvalidFHSConfigError):
        FHSConfig(confidence_level=1.0)


def test_config_invalid_holding_period():
    with pytest.raises(InvalidFHSConfigError):
        FHSConfig(holding_period_days=0)


def test_config_invalid_min_history():
    with pytest.raises(InvalidFHSConfigError):
        FHSConfig(min_history=1)


def test_config_garch_min_below_min_history():
    with pytest.raises(InvalidFHSConfigError):
        FHSConfig(min_history=60, garch_min_history=30)


def test_config_invalid_n_simulations():
    with pytest.raises(InvalidFHSConfigError):
        FHSConfig(n_simulations=10)


def test_config_invalid_nonfinite_ratio():
    with pytest.raises(InvalidFHSConfigError):
        FHSConfig(max_nonfinite_ratio=1.0)


# ── 输入校验 (Fail-Closed) ────────────────────────────────────────────────────


def test_insufficient_history_raises(engine: FHSEngine):
    with pytest.raises(InsufficientFHSHistoryError):
        engine.compute(np.full(10, 0.01), portfolio_value=NAV)


def test_portfolio_value_must_be_positive(engine: FHSEngine):
    r = _make_iid_normal(100)
    with pytest.raises(InvalidFHSConfigError):
        engine.compute(r, portfolio_value=0.0)
    with pytest.raises(InvalidFHSConfigError):
        engine.compute(r, portfolio_value=-1.0)


def test_returns_must_be_1d(engine: FHSEngine):
    with pytest.raises(InvalidFHSConfigError):
        engine.compute(np.zeros((50, 2)), portfolio_value=NAV)


def test_nonfinite_ratio_exceed_raises(engine: FHSEngine):
    arr = np.concatenate([np.full(80, 0.01), np.full(20, np.nan)])
    with pytest.raises(ExcessiveFHSNonFiniteDataError):
        engine.compute(arr, portfolio_value=NAV)


def test_nonfinite_below_ratio_filtered_and_counted(engine: FHSEngine):
    arr = np.concatenate([_make_iid_normal(100), np.array([np.nan, np.inf, -np.inf])])
    res = engine.compute(arr, portfolio_value=NAV)
    assert res.nan_dropped == 3
    assert res.sample_size == 100


# ── GARCH 拟合 ────────────────────────────────────────────────────────────────


def test_garch_fit_converges_on_synthetic_garch(engine: FHSEngine):
    r = _make_garch_series(500)
    res = engine.compute(r, portfolio_value=NAV, now=T0)
    assert res.method_used is FHSMethod.FHS
    assert res.garch_converged is True
    assert res.garch_params is not None
    p = res.garch_params
    assert p.omega > 0
    assert p.alpha >= 0
    assert p.beta >= 0
    assert p.persistence < 1.0  # 平稳性守卫
    assert p.sigma_forecast > 0


def test_garch_params_recovery_loose(engine: FHSEngine):
    """QMLE 参数恢复 (宽容差——500 样本 GARCH 估计本身噪声大)。"""
    r = _make_garch_series(500, omega=2e-6, alpha=0.10, beta=0.85)
    res = engine.compute(r, portfolio_value=NAV)
    p = res.garch_params
    assert p is not None
    assert 0.02 <= p.alpha <= 0.35, f"alpha out of band: {p.alpha}"
    assert 0.50 <= p.beta <= 0.99, f"beta out of band: {p.beta}"
    assert 0.70 <= p.persistence < 1.0, f"persistence out of band: {p.persistence}"


# ── FHS VaR/ES 输出与 HS 对照合理性 ───────────────────────────────────────────


def test_fhs_basic_invariants(engine: FHSEngine):
    r = _make_garch_series(500)
    res = engine.compute(r, portfolio_value=NAV)
    assert res.var >= 0.0
    assert res.es >= res.var  # ES>=VaR 构造性成立
    assert res.var_pct == pytest.approx(res.var / NAV)
    assert res.es_pct == pytest.approx(res.es / NAV)
    assert res.historical_var >= 0.0
    assert res.historical_es >= res.historical_var


def test_regime_shift_fhs_exceeds_hs(engine: FHSEngine):
    """近期波动聚集 (末尾 30 日高波动): FHS 条件波动率预测高于全窗等权 HS。

    这是 FHS 的核心价值——GARCH 对近期波动率加权, HS 对全窗等权;
    风暴在尾部时 FHS VaR 必须显著高于 HS (memo 36 §3.16 设计意图)。
    """
    r = _make_regime_shift()
    res = engine.compute(r, portfolio_value=NAV)
    assert res.method_used is FHSMethod.FHS
    assert res.var > res.historical_var * 1.05, (
        f"FHS 未响应近期波动聚集: fhs={res.var:.0f} hs={res.historical_var:.0f}"
    )


def test_calm_tail_fhs_below_hs(engine: FHSEngine):
    """远期风暴 + 近期平静: FHS 条件波动率回落, VaR 应低于全窗等权 HS。"""
    rng = np.random.default_rng(2)
    storm = rng.normal(0.0, 0.03, 200)
    calm = rng.normal(0.0, 0.008, 60)
    r = np.concatenate([storm, calm])
    res = engine.compute(r, portfolio_value=NAV)
    assert res.method_used is FHSMethod.FHS
    assert res.var < res.historical_var, (
        f"FHS 未响应近期平静: fhs={res.var:.0f} hs={res.historical_var:.0f}"
    )


def test_iid_normal_fhs_close_to_hs(engine: FHSEngine):
    """iid 正态 (无波动聚集): FHS 与 HS 应同量级 (相对偏差 <50%)。

    无 GARCH 结构时 FHS 退化为"以近期 sigma 为尺度的 HS", 两者估计同一
    无条件尾部——偏离过大说明模拟或拟合有 bug。
    """
    r = _make_iid_normal(250)
    res = engine.compute(r, portfolio_value=NAV)
    assert res.method_used is FHSMethod.FHS
    if res.historical_var > 0:
        rel = abs(res.var - res.historical_var) / res.historical_var
        assert rel < 0.50, f"iid 下 FHS/HS 偏离过大: {rel:.2%}"


def test_portfolio_value_scaling(engine: FHSEngine):
    r = _make_garch_series(500)
    res1 = engine.compute(r, portfolio_value=NAV)
    res2 = engine.compute(r, portfolio_value=2 * NAV)
    assert res2.var == pytest.approx(2 * res1.var, rel=1e-9)
    assert res2.es == pytest.approx(2 * res1.es, rel=1e-9)


def test_multiday_holding_period():
    """多日 horizon 走 GARCH 递归 (非 sqrt(T)): T=5 VaR 应大于 T=1。"""
    eng1 = FHSEngine(FHSConfig(random_seed=42, holding_period_days=1))
    eng5 = FHSEngine(FHSConfig(random_seed=42, holding_period_days=5))
    r = _make_garch_series(500)
    res1 = eng1.compute(r, portfolio_value=NAV)
    res5 = eng5.compute(r, portfolio_value=NAV)
    assert res5.var > res1.var, (
        f"多日 VaR 未增长: T1={res1.var:.0f} T5={res5.var:.0f}"
    )


def test_seed_reproducibility():
    r = _make_garch_series(500)
    eng = FHSEngine(FHSConfig(random_seed=42))
    res1 = eng.compute(r, portfolio_value=NAV)
    res2 = eng.compute(r, portfolio_value=NAV)
    assert res1.var == res2.var
    assert res1.es == res2.es
    assert res1.random_seed_used == res2.random_seed_used == 42


# ── 不收敛回退 (memo 36 §3.16) ────────────────────────────────────────────────


def test_fallback_on_zero_variance(engine: FHSEngine):
    """常零序列: 方差=0 无波动结构可拟合 → 回退 historical。"""
    res = engine.compute(np.zeros(100), portfolio_value=NAV)
    assert res.method_used is FHSMethod.HISTORICAL_FALLBACK
    assert res.garch_converged is False
    assert res.garch_params is None
    assert res.fallback_reason is not None
    assert res.var == res.historical_var == 0.0
    assert res.es == res.historical_es == 0.0


def test_fallback_on_small_sample_guard(engine: FHSEngine):
    """n=40 (min_history=30 <= n < garch_min_history=60): 不尝试 GARCH 直接回退。"""
    r = _make_iid_normal(40)
    res = engine.compute(r, portfolio_value=NAV)
    assert res.method_used is FHSMethod.HISTORICAL_FALLBACK
    assert res.garch_converged is False
    assert res.garch_params is None
    assert "garch_min_history" in (res.fallback_reason or "")
    assert res.var == pytest.approx(res.historical_var)
    assert res.es == pytest.approx(res.historical_es)


def test_fallback_disabled_raises():
    eng = FHSEngine(FHSConfig(random_seed=42, fallback_to_historical=False))
    with pytest.raises(GarchConvergenceError):
        eng.compute(np.zeros(100), portfolio_value=NAV)


def test_fallback_still_reports_hs_benchmark(engine: FHSEngine):
    """回退路径下 HS 对照仍完整产出 (供审计比对)。"""
    r = _make_iid_normal(40)
    res = engine.compute(r, portfolio_value=NAV)
    assert res.historical_var >= 0.0
    assert res.historical_es >= res.historical_var


# ── 结果对象 ──────────────────────────────────────────────────────────────────


def test_result_to_dict(engine: FHSEngine):
    r = _make_garch_series(500)
    res = engine.compute(r, portfolio_value=NAV, now=T0)
    d = res.to_dict()
    for key in (
        "var",
        "es",
        "var_pct",
        "es_pct",
        "method_used",
        "garch_converged",
        "garch_params",
        "historical_var",
        "historical_es",
        "fallback_reason",
        "confidence_level",
        "holding_period_days",
        "portfolio_value",
        "sample_size",
        "nan_dropped",
        "n_simulations",
        "random_seed_used",
    ):
        assert key in d, f"to_dict 缺键: {key}"
    assert d["method_used"] == "fhs"
    assert d["garch_params"]["persistence"] < 1.0
    assert res.timestamp == T0


def test_result_is_frozen(engine: FHSEngine):
    r = _make_garch_series(500)
    res = engine.compute(r, portfolio_value=NAV)
    assert isinstance(res, FHSResult)
    with pytest.raises(AttributeError):
        res.var = 1.0  # type: ignore[misc]
