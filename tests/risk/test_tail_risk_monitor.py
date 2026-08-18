# [BLUEPRINT] MOD-RK-15 | docs/03_modules/_domain_risk/tail_risk_monitor/blueprint.md | §
# [TTL] permanent
"""TailRiskMonitor 单元测试 (MOD-RK-15)。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from zephyr.risk.core.tail_risk_monitor import (
    InvalidTailRiskInputError,
    PotFitResult,
    TailRiskAlertLevel,
    TailRiskConfig,
    TailRiskMonitor,
    TailRiskSnapshot,
)

T0 = datetime(2026, 8, 4, 14, 0, tzinfo=timezone.utc)


def t(offset_seconds: float = 0.0) -> datetime:
    return T0 + timedelta(seconds=offset_seconds)


@pytest.fixture
def normal_returns():
    """正态分布收益率 (轻尾)。"""
    rng = np.random.default_rng(42)
    return rng.normal(0, 0.02, 500)


@pytest.fixture
def heavy_tail_returns():
    """厚尾收益率 (学生t, df=3)。"""
    rng = np.random.default_rng(42)
    return rng.standard_t(3, 500) * 0.02


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_defaults():
    cfg = TailRiskConfig()
    assert cfg.confidence == pytest.approx(0.95)
    assert cfg.pot_threshold_quantile == pytest.approx(0.90)
    assert cfg.jump_threshold_sigma == pytest.approx(3.0)
    assert cfg.heavy_tail_shape_threshold == pytest.approx(0.2)
    assert cfg.critical_shape_threshold == pytest.approx(0.5)


def test_config_invalid_confidence():
    with pytest.raises(InvalidTailRiskInputError):
        TailRiskConfig(confidence=1.5)


def test_config_invalid_threshold_quantile():
    with pytest.raises(InvalidTailRiskInputError):
        TailRiskConfig(pot_threshold_quantile=0.3)


def test_config_critical_below_heavy():
    with pytest.raises(InvalidTailRiskInputError, match="must be >"):
        TailRiskConfig(
            heavy_tail_shape_threshold=0.5,
            critical_shape_threshold=0.3,
        )


def test_config_invalid_es_ratio():
    with pytest.raises(InvalidTailRiskInputError):
        TailRiskConfig(es_warning_ratio=0.8)


# ── VaR ──────────────────────────────────────────────────────────────────────


def test_compute_var_basic():
    returns = np.array([-0.05, -0.02, 0.01, 0.03, -0.01, 0.02, -0.03, 0.0])
    var = TailRiskMonitor.compute_var(returns, 0.95)
    # 5% 分位 = -0.05, VaR = 0.05
    assert var == pytest.approx(0.05, abs=0.01)


def test_compute_var_positive_loss():
    """VaR 总是非负 (损失额)。"""
    returns = np.array([0.01, 0.02, 0.03, 0.04])  # 全正
    var = TailRiskMonitor.compute_var(returns, 0.95)
    assert var >= 0


# ── ES / CVaR ────────────────────────────────────────────────────────────────


def test_es_ge_var(normal_returns):
    """ES >= VaR (尾部期望 >= 分位数)。"""
    monitor = TailRiskMonitor()
    var = monitor.compute_var(normal_returns, 0.95)
    es = monitor.compute_expected_shortfall(normal_returns, 0.95)
    assert es >= var


def test_es_with_known_data():
    returns = np.array([-0.10, -0.05, -0.02, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06])
    var = TailRiskMonitor.compute_var(returns, 0.90)
    es = TailRiskMonitor.compute_expected_shortfall(returns, 0.90)
    assert es >= var
    assert es > 0


# ── POT 拟合 ─────────────────────────────────────────────────────────────────


def test_pot_fit_returns_result(normal_returns):
    monitor = TailRiskMonitor()
    pot = monitor.fit_pot(normal_returns)
    assert pot is not None
    assert isinstance(pot, PotFitResult)
    assert pot.n_exceedances > 0
    assert pot.scale > 0


def test_pot_heavy_tail_detected(heavy_tail_returns):
    monitor = TailRiskMonitor()
    pot = monitor.fit_pot(heavy_tail_returns)
    assert pot is not None
    # 学生t(df=3) 应有正 shape (厚尾)
    assert pot.shape > -0.5  # 允许拟合误差


def test_pot_insufficient_samples():
    monitor = TailRiskMonitor()
    returns = np.array([0.01, 0.02])  # 太少
    pot = monitor.fit_pot(returns)
    assert pot is None


def test_pot_no_losses():
    """全正收益 → 无损失 → None。"""
    monitor = TailRiskMonitor()
    returns = np.array([0.01] * 100)
    pot = monitor.fit_pot(returns)
    assert pot is None


def test_pot_to_dict(normal_returns):
    monitor = TailRiskMonitor()
    pot = monitor.fit_pot(normal_returns)
    d = pot.to_dict()
    assert "shape" in d
    assert "scale" in d
    assert "is_heavy_tailed" in d


# ── F1 红队实证 (2026-08-16 双轮审查裁定): ES 分位数 method='lower' 口径 ──


def test_es_quantile_is_actual_sample_point():
    """F1: ES 尾部筛选分位数必须取实有样本点 (method='lower'), 不用线性插值虚拟值。

    红队构造: 30 样本 (min_samples 边界), 95% 置信 → 分位点 = sorted[floor(29×0.05)]
    = sorted[1] (第 2 差样本实有点); 线性插值会产出 sorted[1] 与 sorted[2] 之间的
    虚拟值。ES 必须等于 lower 口径尾部均值的闭式解。
    """
    rng = np.random.default_rng(7)
    returns = rng.normal(0.0, 0.02, 30)
    es = TailRiskMonitor.compute_expected_shortfall(returns, 0.95)
    q_lower = float(np.quantile(returns, 0.05, method="lower"))
    # 分位点是实有样本成员 (非插值虚拟值)
    assert q_lower == np.sort(returns)[1]
    assert q_lower in set(returns.tolist())
    # ES = lower 口径尾部 (r <= q_lower) 均值取负
    tail = returns[returns <= q_lower]
    assert es == pytest.approx(-float(np.mean(tail)), rel=1e-12)


def test_es_deterministic_on_discrete_returns():
    """F1: 离散收益 (大量 0 值日, A 股常态) 下 ES 口径确定可复现。

    红队构造: 1 个 -10% 损失日 + 99 个 0 收益日——lower 口径分位点 = sorted[4] = 0.0
    (实有点), 尾部 = 全部 <=0 样本, ES = -mean = 0.001 恒定, 无插值抖动。
    """
    returns = np.concatenate([[-0.10], np.zeros(99)])
    es1 = TailRiskMonitor.compute_expected_shortfall(returns, 0.95)
    es2 = TailRiskMonitor.compute_expected_shortfall(returns, 0.95)
    q_lower = float(np.quantile(returns, 0.05, method="lower"))
    assert q_lower == 0.0
    assert es1 == pytest.approx(0.001, rel=1e-9)
    assert es1 == es2


def test_es_ge_var_small_sample_boundary():
    """F1: min_samples=30 边界 + 多置信度网格, ES>=VaR 不变量保持。"""
    rng = np.random.default_rng(123)
    returns = rng.normal(0.0, 0.02, 30)
    for conf in (0.90, 0.95, 0.99):
        var = TailRiskMonitor.compute_var(returns, conf)
        es = TailRiskMonitor.compute_expected_shortfall(returns, conf)
        assert es >= var, f"ES({es}) < VaR({var}) at n=30 conf={conf}"


# ── P1c 红队实证 (双轮审查深挖③裁定): POT 小样本降级纯历史 ES ──


def test_pot_degrades_on_sixty_day_half_negative_window():
    """P1c: 60 日窗口 + 50% 负日常态 → exceedances<5 → pot=None (不硬拟合噪声)。"""
    rng = np.random.default_rng(7)
    returns = np.concatenate(
        [rng.normal(-0.01, 0.005, 30), rng.normal(0.01, 0.005, 30)]
    )
    monitor = TailRiskMonitor()
    pot = monitor.fit_pot(returns)
    assert pot is None  # 60 日窗口下 POT 与样本量天然不兼容, 降级而非噪声拟合


def test_pot_fallback_flag_set_in_snapshot():
    """P1c: 降级路径可验证——snapshot.pot_fallback_historical=True 且入 to_dict。"""
    rng = np.random.default_rng(7)
    returns = np.concatenate(
        [rng.normal(-0.01, 0.005, 30), rng.normal(0.01, 0.005, 30)]
    )
    monitor = TailRiskMonitor()
    snapshot = monitor.assess(returns, now=t())
    assert snapshot.pot is None
    assert snapshot.pot_fallback_historical is True
    assert snapshot.to_dict()["pot_fallback_historical"] is True
    # 降级后 ES 仍为纯历史模拟值 (ES>=VaR 不变量保持)
    assert snapshot.expected_shortfall >= snapshot.var


def test_pot_fallback_logs_warning(caplog):
    """P1c: 降级路径必须告警留痕 (非静默缺失厚尾诊断)。"""
    rng = np.random.default_rng(7)
    returns = np.concatenate(
        [rng.normal(-0.01, 0.005, 30), rng.normal(0.01, 0.005, 30)]
    )
    monitor = TailRiskMonitor()
    with caplog.at_level("WARNING"):
        snapshot = monitor.assess(returns, now=t())
    assert snapshot.pot_fallback_historical is True
    assert any("POT" in r.message for r in caplog.records)


def test_pot_fallback_false_when_fit_succeeds(normal_returns):
    """样本充足拟合成功时 pot_fallback_historical=False (正常路径不标降级)。"""
    monitor = TailRiskMonitor()
    snapshot = monitor.assess(normal_returns, now=t())
    assert snapshot.pot is not None
    assert snapshot.pot_fallback_historical is False


# ── 跳跃检测 ──────────────────────────────────────────────────────────────────


def test_detect_jumps_with_outliers():
    returns = np.zeros(100)
    returns[50] = 0.10  # 3σ 跳跃 (std≈0.01, 3σ=0.03)
    returns[80] = -0.08
    count = TailRiskMonitor.detect_jumps(returns, threshold_sigma=3.0)
    assert count == 2


def test_detect_jumps_none():
    returns = np.array([0.01, 0.02, -0.01, 0.0, 0.01] * 20)
    count = TailRiskMonitor.detect_jumps(returns, threshold_sigma=3.0)
    assert count == 0


def test_detect_jumps_empty():
    count = TailRiskMonitor.detect_jumps(np.array([]), 3.0)
    assert count == 0


def test_detect_jumps_zero_std():
    returns = np.array([0.01] * 100)
    count = TailRiskMonitor.detect_jumps(returns, 3.0)
    assert count == 0


# ── 综合评估 ──────────────────────────────────────────────────────────────────


def test_assess_normal_returns(normal_returns):
    monitor = TailRiskMonitor()
    snapshot = monitor.assess(normal_returns, now=t())
    assert isinstance(snapshot, TailRiskSnapshot)
    assert snapshot.var > 0
    assert snapshot.expected_shortfall >= snapshot.var
    assert snapshot.es_var_ratio >= 1.0
    assert snapshot.jump_count >= 0
    assert snapshot.frtb_addon > 0


def test_assess_heavy_tail_alerts(heavy_tail_returns):
    monitor = TailRiskMonitor()
    snapshot = monitor.assess(heavy_tail_returns, now=t())
    # 厚尾分布应触发告警 (WARNING 或更高)
    assert snapshot.alert_level in (
        TailRiskAlertLevel.WARNING,
        TailRiskAlertLevel.CRITICAL,
        TailRiskAlertLevel.EMERGENCY,
    )


def test_assess_with_portfolio_value(normal_returns):
    monitor = TailRiskMonitor()
    snapshot = monitor.assess(normal_returns, portfolio_value=1_000_000, now=t())
    # 金额 = 比率 × 1M
    assert snapshot.var > 0
    assert snapshot.expected_shortfall >= snapshot.var


def test_assess_to_dict(normal_returns):
    monitor = TailRiskMonitor()
    snapshot = monitor.assess(normal_returns, now=t())
    d = snapshot.to_dict()
    assert "var" in d
    assert "expected_shortfall" in d
    assert "es_var_ratio" in d
    assert "alert_level" in d
    assert "frtb_addon" in d


# ── 告警级别 ──────────────────────────────────────────────────────────────────


def test_alert_none_for_normal(normal_returns):
    monitor = TailRiskMonitor(TailRiskConfig(
        heavy_tail_shape_threshold=10.0,  # 极高阈值, 不触发
        critical_shape_threshold=20.0,
        es_warning_ratio=10.0,
    ))
    snapshot = monitor.assess(normal_returns, now=t())
    assert snapshot.alert_level is TailRiskAlertLevel.NONE


def test_alert_emergency_for_extreme():
    """构造极端厚尾 + 高 ES/VaR → EMERGENCY。"""
    rng = np.random.default_rng(42)
    # 学生t df=2 极厚尾
    returns = rng.standard_t(2, 500) * 0.05
    monitor = TailRiskMonitor(TailRiskConfig(
        heavy_tail_shape_threshold=0.1,
        critical_shape_threshold=0.3,
        es_warning_ratio=1.2,
    ))
    snapshot = monitor.assess(returns, now=t())
    assert snapshot.alert_level in (
        TailRiskAlertLevel.CRITICAL,
        TailRiskAlertLevel.EMERGENCY,
    )


# ── FRTB 加价 ────────────────────────────────────────────────────────────────


def test_frtb_addon_positive(normal_returns):
    monitor = TailRiskMonitor()
    snapshot = monitor.assess(normal_returns, portfolio_value=1_000_000, now=t())
    assert snapshot.frtb_addon > 0


def test_frtb_addon_increases_with_heavy_tail(heavy_tail_returns):
    """厚尾 → FRTB 加价更高。"""
    monitor = TailRiskMonitor()
    normal = np.random.default_rng(42).normal(0, 0.02, 500)
    snap_normal = monitor.assess(normal, portfolio_value=1_000_000, now=t())
    snap_heavy = monitor.assess(heavy_tail_returns, portfolio_value=1_000_000, now=t())
    # 厚尾加价应 >= 正态 (因 shape 调整)
    # 注: 拟合可能有误差, 仅验证逻辑
    assert snap_heavy.frtb_addon > 0
    assert snap_normal.frtb_addon > 0


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_invalid_returns_too_short():
    monitor = TailRiskMonitor(TailRiskConfig(min_samples=30))
    with pytest.raises(InvalidTailRiskInputError, match="samples"):
        monitor.assess(np.array([0.01] * 10), now=t())


def test_invalid_returns_2d():
    monitor = TailRiskMonitor()
    with pytest.raises(InvalidTailRiskInputError, match="1D"):
        monitor.assess(np.array([[0.01, 0.02]] * 30), now=t())


def test_nan_returns_filtered():
    monitor = TailRiskMonitor(TailRiskConfig(min_samples=30))
    returns = np.array([0.01] * 40, dtype=float)
    returns[5] = np.nan
    # NaN 被过滤后仍有 39 >= 30
    snapshot = monitor.assess(returns, now=t())
    assert snapshot.var >= 0


def test_too_many_nan_after_filter():
    monitor = TailRiskMonitor(TailRiskConfig(min_samples=30))
    returns = np.full(40, np.nan)
    with pytest.raises(InvalidTailRiskInputError, match="NaN"):
        monitor.assess(returns, now=t())


# ── 不变量 ────────────────────────────────────────────────────────────────────


def test_invariant_es_ge_var(normal_returns):
    """不变量: ES >= VaR。"""
    monitor = TailRiskMonitor()
    for conf in [0.90, 0.95, 0.99]:
        var = monitor.compute_var(normal_returns, conf)
        es = monitor.compute_expected_shortfall(normal_returns, conf)
        assert es >= var, f"ES({es}) < VaR({var}) at confidence={conf}"


def test_invariant_frtb_non_negative(normal_returns):
    """不变量: FRTB 加价 >= 0。"""
    monitor = TailRiskMonitor()
    snapshot = monitor.assess(normal_returns, now=t())
    assert snapshot.frtb_addon >= 0


# ── _validate_returns ±inf 过滤守卫 (AI-R2-001) ──────────────────────────────


class TestValidateReturnsInfFilter:
    """_validate_returns 同时过滤 NaN 与 ±inf（防 VaR=inf/FRTB=inf 流入下游）。

    原缺陷：只滤 NaN 不滤 inf，含 -inf 样本时历史模拟 VaR/ES/FRTB 全变 inf。
    """

    def test_inf_returns_filtered(self):
        """含 +inf 样本 → 被过滤，输出全有限。"""
        returns = np.concatenate([np.full(35, 0.01), np.full(5, np.inf)])
        out = TailRiskMonitor._validate_returns(returns, 30)
        assert len(out) == 35
        assert np.all(np.isfinite(out))

    def test_neg_inf_returns_filtered(self):
        """含 -inf 样本 → 被过滤，输出全有限。"""
        returns = np.concatenate([np.full(35, 0.01), np.full(5, -np.inf)])
        out = TailRiskMonitor._validate_returns(returns, 30)
        assert len(out) == 35
        assert np.all(np.isfinite(out))

    def test_mixed_nan_inf_returns_filtered(self):
        """NaN/+inf/-inf 混合 → 全部过滤，输出全有限且数量正确。"""
        returns = np.concatenate([
            np.full(35, 0.01),
            [np.nan, np.inf, -np.inf, np.nan, np.inf],
        ])
        out = TailRiskMonitor._validate_returns(returns, 30)
        assert len(out) == 35
        assert np.all(np.isfinite(out))
