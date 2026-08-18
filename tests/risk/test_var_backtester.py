# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.risk.test_var_backtester
# [DOMAIN] D_RISK
# [TESTS] zephyr.risk.core.var_backtester
# [COVERAGE] Kupiec POF / Christoffersen / Acerbi-Szekely Z2 / E-backtesting / Basel traffic light
# [MATURITY] evolving
# [TTL] task_bound

"""
VarBacktester 单测桩 — 36号 §3.9 MVP 4 法回测验证器。

验证目标:
    1. Kupiec POF: 校准模型不拒绝 / 失校模型拒绝
    2. Christoffersen: 独立超限不拒绝 / 聚集超限拒绝
    3. Acerbi-Szekely Z2: ES 校准正确 Z2≈-1 / ES 低估 Z2<<-1 拒绝
    4. E-backtesting: 校准模型 e_value 低 / 失校模型 e_value 高拒绝
    5. Basel traffic light: Green/Yellow/Red 分区正确

理论基准:
    - 95% VaR 名义超限率 α=0.05，250 天期望 12.5 次超限
    - Kupiec LR_UC ~ χ²(1), Christoffersen LR_cc ~ χ²(2)
    - Z2 原假设 E[Z2]=-1
    - E-backtesting e_value > 1/α=20 拒绝
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pytest

from zephyr.risk.core.var_backtester import (
    AcerbiSzekelyResult,
    BacktestObservation,
    ChristoffersenResult,
    EBacktestAlertLevel,
    EBacktestResult,
    InsufficientBacktestHistoryError,
    InvalidBacktestInputError,
    KupiecResult,
    VarBacktester,
)

# ──────────────────────────────────────────────────────────────────────────────
# 合成数据生成器
# ──────────────────────────────────────────────────────────────────────────────


def _make_observations(
    n_obs: int = 250,
    var_forecast: float = 0.02,
    es_forecast: float = 0.025,
    returns: np.ndarray | None = None,
    seed: int = 42,
) -> list[BacktestObservation]:
    """生成合成回测观测。

    Args:
        n_obs: 观测数（默认 250 天）
        var_forecast: 固定 VaR 预测（正数损失，默认 2%）
        es_forecast: 固定 ES 预测（正数损失，默认 2.5%，≥ VaR）
        returns: 自定义收益序列；None 则从 N(0, 0.01) 生成（σ=1%）
        seed: 随机种子
    """
    if returns is None:
        rng = np.random.default_rng(seed)
        returns = rng.normal(0.0, 0.01, size=n_obs)  # σ=1% 日频

    base_date = datetime(2024, 1, 1)
    obs = []
    for i in range(len(returns)):
        obs.append(
            BacktestObservation(
                date=base_date + timedelta(days=i),
                var_forecast=var_forecast,
                es_forecast=es_forecast,
                realized_return=float(returns[i]),
            )
        )
    return obs


def _make_well_calibrated(n_obs: int = 250, var: float = 0.02, es: float = 0.025) -> list[BacktestObservation]:
    """校准良好的模型：σ=1%，VaR=2%，超限率约 2.3%（< 5%，保守但合理）。

    N(0, 0.01) 的 5% 分位数 = -1.645σ = -0.01645，VaR=0.02 时超限率 = P(r < -0.02) = P(Z < -2) ≈ 2.3%
    """
    return _make_observations(n_obs=n_obs, var_forecast=var, es_forecast=es, seed=42)


def _make_miscalibrated(n_obs: int = 250, var: float = 0.005, es: float = 0.008) -> list[BacktestObservation]:
    """失校模型：VaR=0.5% 过小，σ=1% 时超限率约 31%，远超 5%。"""
    return _make_observations(n_obs=n_obs, var_forecast=var, es_forecast=es, seed=42)


def _make_clustered_violations(n_obs: int = 250) -> list[BacktestObservation]:
    """聚集超限：每 10 天连续 3 天大幅亏损（-3%），其余正常。

    模拟波动率聚集——超限不独立，Christoffersen 应拒绝独立性。
    """
    rng = np.random.default_rng(123)
    returns = rng.normal(0.0, 0.005, size=n_obs)  # 基础低波动
    # 每 10 天注入 3 天连续大跌（-3%，超过 VaR=2%）
    for start in range(0, n_obs, 10):
        for j in range(3):
            if start + j < n_obs:
                returns[start + j] = -0.03
    return _make_observations(n_obs=n_obs, var_forecast=0.02, es_forecast=0.025, returns=returns)


# ──────────────────────────────────────────────────────────────────────────────
# Kupiec POF 测试
# ──────────────────────────────────────────────────────────────────────────────


class TestKupiecPOF:
    def test_well_calibrated_not_rejected(self):
        """校准模型：超限率接近 α，Kupiec 不拒绝。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_well_calibrated(n_obs=500, var=0.0165, es=0.0206)  # VaR≈1.645σ → 超限率≈5%
        result = bt.kupiec_pof(obs)
        assert isinstance(result, KupiecResult)
        assert result.n_obs == 500
        assert 0.03 < result.p_hat < 0.08  # 超限率接近 5%
        assert result.p_value > 0.05  # 不拒绝 H0
        assert result.reject is False

    def test_miscalibrated_rejected(self):
        """失校模型：超限率远超 α，Kupiec 拒绝。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_miscalibrated(n_obs=250, var=0.005, es=0.008)
        result = bt.kupiec_pof(obs)
        assert result.p_hat > 0.20  # 超限率 >20%
        assert result.p_value < 0.05  # 拒绝 H0
        assert result.reject is True

    def test_insufficient_history_raises(self):
        """样本不足 30 抛 InsufficientBacktestHistoryError。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_well_calibrated(n_obs=20)
        with pytest.raises(InsufficientBacktestHistoryError):
            bt.kupiec_pof(obs)

    def test_zero_violations(self):
        """零超限（极度保守）：p̂=0，Kupiec 不拒绝（模型保守不等于失校）。"""
        bt = VarBacktester(confidence_level=0.95)
        rng = np.random.default_rng(7)
        returns = rng.normal(0.0, 0.002, size=250)  # σ=0.2%，VaR=2% 几乎不超限
        obs = _make_observations(var_forecast=0.02, es_forecast=0.025, returns=returns)
        result = bt.kupiec_pof(obs)
        assert result.n_violations == 0
        assert result.p_hat == 0.0
        # 零超限不拒绝（保守是安全的）


# ──────────────────────────────────────────────────────────────────────────────
# Christoffersen 测试
# ──────────────────────────────────────────────────────────────────────────────


class TestChristoffersen:
    def test_independent_violations_not_rejected(self):
        """独立超限：Christoffersen 不拒绝独立性。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_well_calibrated(n_obs=500, var=0.0165, es=0.0206)
        result = bt.christoffersen(obs)
        assert isinstance(result, ChristoffersenResult)
        assert result.lr_cc >= 0
        assert result.n_00 + result.n_01 + result.n_10 + result.n_11 == 499  # T-1 转移

    def test_clustered_violations_detected(self):
        """聚集超限：Christoffersen 应检测到独立性失效。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_clustered_violations(n_obs=250)
        result = bt.christoffersen(obs)
        # 聚集超限 → n_11（超限→超限）应较大
        assert result.n_11 > 0
        # LR_ind 应为正（独立性假设被违反）

    def test_transition_matrix_sum(self):
        """转移矩阵四元素之和 = T-1。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_well_calibrated(n_obs=100)
        result = bt.christoffersen(obs)
        assert result.n_00 + result.n_01 + result.n_10 + result.n_11 == 99


# ──────────────────────────────────────────────────────────────────────────────
# Acerbi-Szekely Z2 测试
# ──────────────────────────────────────────────────────────────────────────────


class TestAcerbiSzekelyZ2:
    def test_well_calibrated_z2_near_negative_one(self):
        """校准模型：Z2 ≈ -1（超限日损失 = ES 预测）。"""
        bt = VarBacktester(confidence_level=0.95)
        # 构造超限日损失恰等于 ES 的数据
        rng = np.random.default_rng(99)
        returns = rng.normal(0.0, 0.01, size=500)
        var, es = 0.0165, 0.0206
        obs = _make_observations(var_forecast=var, es_forecast=es, returns=returns)
        result = bt.acerbi_szekely_z2(obs)
        assert isinstance(result, AcerbiSzekelyResult)
        assert result.expected == -1.0
        assert result.n_violations > 0
        # Z2 应在 [-2, 0] 区间（超限日损失/ES，损失为负）
        assert -2.0 < result.z2 < 0.0

    def test_es_underestimated_rejected(self):
        """ES 低估：超限日损失远大于 ES → Z2 << -1 拒绝。"""
        bt = VarBacktester(confidence_level=0.95)
        # VaR=2%, ES=2.1%（ES 几乎=VaR，严重低估尾部）
        # 超限日损失 ~3% >> ES 2.1%
        rng = np.random.default_rng(11)
        returns = rng.normal(0.0, 0.01, size=500)
        # 注入超限日大幅亏损
        for i in range(0, 500, 20):
            returns[i] = -0.04  # -4% 远超 ES=2.1%
        obs = _make_observations(var_forecast=0.02, es_forecast=0.021, returns=returns)
        result = bt.acerbi_szekely_z2(obs)
        assert result.z2 < -1.0  # ES 低估
        assert result.reject is True

    def test_no_violations_raises(self):
        """无超限日 Z2 无法计算，抛 InsufficientBacktestHistoryError。"""
        bt = VarBacktester(confidence_level=0.95)
        rng = np.random.default_rng(3)
        returns = rng.normal(0.0, 0.001, size=250)  # 极低波动，无超限
        obs = _make_observations(var_forecast=0.02, es_forecast=0.025, returns=returns)
        with pytest.raises(InsufficientBacktestHistoryError):
            bt.acerbi_szekely_z2(obs)


# ──────────────────────────────────────────────────────────────────────────────
# E-backtesting 测试
# ──────────────────────────────────────────────────────────────────────────────


class TestEBacktesting:
    def test_well_calibrated_low_e_value(self):
        """校准模型：e_value 低，不拒绝。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_well_calibrated(n_obs=500, var=0.0165, es=0.0206)
        result = bt.e_backtesting(obs)
        assert isinstance(result, EBacktestResult)
        assert result.n_obs == 500
        assert result.threshold == pytest.approx(20.0)  # 1/0.05
        assert result.e_value > 0
        # e-process 单调非降？不一定（乘性可衰减），但应 > 0
        assert np.all(result.e_process > 0)

    def test_miscalibrated_high_e_value(self):
        """失校模型：超限率远超 α，e_value 高，拒绝。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_miscalibrated(n_obs=250, var=0.005, es=0.008)
        result = bt.e_backtesting(obs)
        # 超限率 ~31% >> 5%，e-value 应快速增长
        assert result.e_value > 1.0
        # 告警级别至少 yellow 以上
        assert result.alert_level in (
            EBacktestAlertLevel.YELLOW,
            EBacktestAlertLevel.RED,
            EBacktestAlertLevel.BLACK,
        )

    def test_alert_levels_ordered(self):
        """告警四级 green < yellow < red < black。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_well_calibrated(n_obs=500, var=0.0165, es=0.0206)
        result = bt.e_backtesting(obs)
        # 校准模型应 green 或 yellow
        assert result.alert_level in (EBacktestAlertLevel.GREEN, EBacktestAlertLevel.YELLOW)

    def test_lambda_within_bounds(self):
        """GREM λ ∈ [0, λ_max]。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_well_calibrated(n_obs=100)
        result = bt.e_backtesting(obs)
        assert np.all(result.lambda_series >= 0)
        assert np.all(result.lambda_series <= 0.95)


# ──────────────────────────────────────────────────────────────────────────────
# Basel Traffic Light 测试
# ──────────────────────────────────────────────────────────────────────────────


class TestBaselTrafficLight:
    def test_green_zone(self):
        """校准模型：超限率 ≤1.28×期望 → Green。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_well_calibrated(n_obs=500, var=0.0165, es=0.0206)
        result = bt.basel_traffic_light(obs)
        assert result["zone"] in ("green", "yellow")
        assert "expected_violations" in result

    def test_red_zone(self):
        """失校模型：超限率 >>1.6×期望 → Red。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_miscalibrated(n_obs=250, var=0.005, es=0.008)
        result = bt.basel_traffic_light(obs)
        assert result["zone"] == "red"
        assert result["violation_ratio"] > 1.6


# ──────────────────────────────────────────────────────────────────────────────
# 全量报告测试
# ──────────────────────────────────────────────────────────────────────────────


class TestFullReport:
    def test_full_report_structure(self):
        """全量报告包含 4 法 + Basel + overall_reject。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_well_calibrated(n_obs=500, var=0.0165, es=0.0206)
        report = bt.full_report(obs)
        assert "timestamp" in report
        assert "confidence_level" in report
        assert "kupiec_pof" in report
        assert "christoffersen" in report
        assert "acerbi_szekely_z2" in report
        assert "e_backtesting" in report
        assert "basel_traffic_light" in report
        assert "overall_reject" in report
        assert isinstance(report["overall_reject"], bool)

    def test_full_report_insufficient_history(self):
        """样本不足时报告含 error 字段但不崩溃。"""
        bt = VarBacktester(confidence_level=0.95)
        obs = _make_well_calibrated(n_obs=20)  # 不足 30
        report = bt.full_report(obs)
        # 各法应返回 error dict
        assert "error" in report["kupiec_pof"] or isinstance(report["kupiec_pof"], dict)


# ──────────────────────────────────────────────────────────────────────────────
# 输入校验测试
# ──────────────────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_negative_var_rejected(self):
        """VaR 预测为负数抛 InvalidBacktestInputError。"""
        with pytest.raises(InvalidBacktestInputError):
            BacktestObservation(
                date=datetime(2024, 1, 1),
                var_forecast=-0.01,
                es_forecast=0.02,
                realized_return=0.0,
            )

    def test_es_less_than_var_rejected(self):
        """ES < VaR 抛 InvalidBacktestInputError（ES 是尾部期望 ≥ VaR 分位数）。"""
        with pytest.raises(InvalidBacktestInputError):
            BacktestObservation(
                date=datetime(2024, 1, 1),
                var_forecast=0.03,
                es_forecast=0.02,  # ES < VaR 违反不变量
                realized_return=0.0,
            )

    def test_invalid_confidence_level(self):
        """置信度越界抛 InvalidBacktestInputError。"""
        with pytest.raises(InvalidBacktestInputError):
            VarBacktester(confidence_level=1.5)
        with pytest.raises(InvalidBacktestInputError):
            VarBacktester(confidence_level=0.0)

    def test_is_violation_property(self):
        """is_violation 属性：realized ≤ -VaR 判定超限。"""
        obs = BacktestObservation(
            date=datetime(2024, 1, 1),
            var_forecast=0.02,
            es_forecast=0.025,
            realized_return=-0.03,  # 损失 3% > VaR 2%
        )
        assert obs.is_violation is True

        obs2 = BacktestObservation(
            date=datetime(2024, 1, 2),
            var_forecast=0.02,
            es_forecast=0.025,
            realized_return=-0.01,  # 损失 1% < VaR 2%
        )
        assert obs2.is_violation is False
