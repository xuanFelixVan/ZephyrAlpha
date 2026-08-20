# [BLUEPRINT] MOD-RK-16 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""RiskDecomposer 单元测试 (MOD-RK-16)。"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from zephyr.risk.core.risk_decomposition import (
    DecompositionResult,
    InvalidDecompositionInputError,
    RiskDecomposer,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _seed():
    np.random.seed(42)


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_cov_must_be_square():
    decomposer = RiskDecomposer()
    cov = np.array([[1, 2, 3], [4, 5, 6]])  # 非方阵
    w = np.array([0.5, 0.5])
    with pytest.raises(InvalidDecompositionInputError):
        decomposer.decompose(cov, w)


def test_weights_shape_mismatch():
    decomposer = RiskDecomposer()
    cov = np.eye(3)
    w = np.array([0.5, 0.5])  # 应为 3
    with pytest.raises(InvalidDecompositionInputError):
        decomposer.decompose(cov, w)


def test_negative_weights_rejected():
    decomposer = RiskDecomposer()
    cov = np.eye(2)
    w = np.array([-0.5, 1.5])
    with pytest.raises(InvalidDecompositionInputError):
        decomposer.decompose(cov, w)


def test_zero_weights_sum_rejected():
    decomposer = RiskDecomposer()
    cov = np.eye(2)
    w = np.array([0.0, 0.0])
    with pytest.raises(InvalidDecompositionInputError):
        decomposer.decompose(cov, w)


def test_weights_auto_normalized():
    """权重自动归一化。"""
    decomposer = RiskDecomposer()
    cov = np.eye(2)
    result = decomposer.decompose(cov, np.array([3.0, 1.0]), now=T0)
    assert result.weights == pytest.approx([0.75, 0.25])


# ── 基础分解 (无因子模型) ─────────────────────────────────────────────────────


def test_total_variance_diagonal_cov():
    """对角协方差: σ_p² = Σ w_i² σ_i²。"""
    decomposer = RiskDecomposer()
    cov = np.diag([0.04, 0.09])  # std 0.2, 0.3
    w = np.array([0.5, 0.5])
    result = decomposer.decompose(cov, w, now=T0)
    # 0.5²·0.04 + 0.5²·0.09 = 0.01 + 0.0225 = 0.0325
    assert result.total_variance == pytest.approx(0.0325)
    assert result.total_risk == pytest.approx(np.sqrt(0.0325))


def test_ccr_sums_to_total_risk():
    """CCR 之和 = σ_p (守恒)。"""
    decomposer = RiskDecomposer()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    w = np.array([0.6, 0.4])
    result = decomposer.decompose(cov, w, now=T0)
    assert np.sum(result.ccr) == pytest.approx(result.total_risk, rel=1e-9)


def test_pct_contribution_sums_to_one():
    decomposer = RiskDecomposer()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    w = np.array([0.6, 0.4])
    result = decomposer.decompose(cov, w, now=T0)
    assert np.sum(result.pct_contribution) == pytest.approx(1.0)


def test_mcr_formula():
    """MCR_i = (Σw)_i / σ_p。"""
    decomposer = RiskDecomposer()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    w = np.array([0.6, 0.4])
    result = decomposer.decompose(cov, w, now=T0)
    expected_mcr = (cov @ result.weights) / result.total_risk
    assert result.mcr == pytest.approx(expected_mcr, rel=1e-9)


def test_ccr_equals_weight_times_mcr():
    """CCR_i = w_i · MCR_i。"""
    decomposer = RiskDecomposer()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    w = np.array([0.6, 0.4])
    result = decomposer.decompose(cov, w, now=T0)
    assert result.ccr == pytest.approx(result.weights * result.mcr, rel=1e-9)


def test_higher_weight_higher_contribution():
    """波动率相同时, 权重大的资产贡献更大。"""
    decomposer = RiskDecomposer()
    cov = np.diag([0.04, 0.04])  # 等波动
    w = np.array([0.8, 0.2])
    result = decomposer.decompose(cov, w, now=T0)
    assert result.ccr[0] > result.ccr[1]
    assert result.pct_contribution[0] > result.pct_contribution[1]


def test_equal_weights_equal_contribution_when_equal_vol():
    """等权 + 等波动 + 零相关 → 等贡献。"""
    decomposer = RiskDecomposer()
    cov = np.diag([0.04, 0.04, 0.04, 0.04])
    w = np.array([0.25, 0.25, 0.25, 0.25])
    result = decomposer.decompose(cov, w, now=T0)
    # 每个贡献应接近 1/4
    for p in result.pct_contribution:
        assert p == pytest.approx(0.25, rel=1e-9)


def test_no_factor_model_when_basic():
    """基础分解: 因子相关字段为 None。"""
    decomposer = RiskDecomposer()
    cov = np.eye(2)
    result = decomposer.decompose(cov, np.array([0.5, 0.5]), now=T0)
    assert not result.has_factor_model
    assert result.factor_variance is None
    assert result.residual_variance is None
    assert result.factor_contribution_pct is None


# ── 因子模型分解 ──────────────────────────────────────────────────────────────


def test_factor_decomposition_variance_split():
    """因子方差 + 残差方差 = 总方差 (单因子模型)。"""
    decomposer = RiskDecomposer()
    N = 3
    # 单因子: B (N,1), Σ_f (1,1), ε (N,)
    B = np.array([[0.8], [1.0], [1.2]])
    factor_cov = np.array([[0.01]])  # 因子方差
    resid_var = np.array([0.01, 0.02, 0.03])
    # 构造一致协方差: Σ = B Σ_f B' + diag(ε)
    cov = B @ factor_cov @ B.T + np.diag(resid_var)
    w = np.array([0.3, 0.3, 0.4])
    result = decomposer.decompose_with_factors(cov, w, B, factor_cov, resid_var, now=T0)
    assert result.has_factor_model
    # 因子 + 残差 = 总方差
    assert result.factor_variance + result.residual_variance == pytest.approx(result.total_variance, rel=1e-9)


def test_factor_contribution_pct_in_range():
    decomposer = RiskDecomposer()
    B = np.array([[0.9], [1.1]])
    factor_cov = np.array([[0.02]])
    resid_var = np.array([0.005, 0.005])
    cov = B @ factor_cov @ B.T + np.diag(resid_var)
    w = np.array([0.5, 0.5])
    result = decomposer.decompose_with_factors(cov, w, B, factor_cov, resid_var, now=T0)
    assert 0 <= result.factor_contribution_pct <= 1
    assert 0 <= result.residual_contribution_pct <= 1
    assert result.factor_contribution_pct + result.residual_contribution_pct == pytest.approx(1.0)


def test_factor_decomposition_dominant_factor():
    """大因子方差 → 因子贡献占主导。"""
    decomposer = RiskDecomposer()
    B = np.array([[1.0], [1.0]])
    factor_cov = np.array([[0.09]])  # 大因子方差
    resid_var = np.array([0.0001, 0.0001])  # 小残差
    cov = B @ factor_cov @ B.T + np.diag(resid_var)
    w = np.array([0.5, 0.5])
    result = decomposer.decompose_with_factors(cov, w, B, factor_cov, resid_var, now=T0)
    assert result.factor_contribution_pct > 0.95  # 因子占主导


def test_factor_decomposition_dominant_residual():
    """小因子方差 + 大残差 → 残差贡献占主导。"""
    decomposer = RiskDecomposer()
    B = np.array([[1.0], [1.0]])
    factor_cov = np.array([[0.0001]])
    resid_var = np.array([0.09, 0.09])
    cov = B @ factor_cov @ B.T + np.diag(resid_var)
    w = np.array([0.5, 0.5])
    result = decomposer.decompose_with_factors(cov, w, B, factor_cov, resid_var, now=T0)
    assert result.residual_contribution_pct > 0.95


def test_factor_loadings_shape_mismatch():
    decomposer = RiskDecomposer()
    cov = np.eye(3)
    w = np.array([1 / 3, 1 / 3, 1 / 3])
    B = np.array([[0.8], [1.0]])  # 应为 (3, K)
    factor_cov = np.array([[0.01]])
    resid_var = np.array([0.01, 0.02, 0.03])
    with pytest.raises(InvalidDecompositionInputError):
        decomposer.decompose_with_factors(cov, w, B, factor_cov, resid_var)


def test_factor_cov_shape_mismatch():
    decomposer = RiskDecomposer()
    N = 2
    B = np.array([[0.8], [1.0]])  # (2, 1)
    # 用正确的 (1,1) factor_cov 构造合法 cov
    correct_factor_cov = np.array([[0.01]])
    resid_var = np.array([0.01, 0.02])
    cov = B @ correct_factor_cov @ B.T + np.diag(resid_var)
    w = np.array([0.5, 0.5])
    # 传入形状错误的 factor_cov (2,2) 应触发校验
    wrong_factor_cov = np.eye(2)
    with pytest.raises(InvalidDecompositionInputError):
        decomposer.decompose_with_factors(cov, w, B, wrong_factor_cov, resid_var)


def test_residual_var_shape_mismatch():
    decomposer = RiskDecomposer()
    N = 2
    B = np.array([[0.8], [1.0]])
    factor_cov = np.array([[0.01]])
    resid_var = np.array([0.01, 0.02, 0.03])  # 应为 (2,)
    cov = np.eye(2)
    w = np.array([0.5, 0.5])
    with pytest.raises(InvalidDecompositionInputError):
        decomposer.decompose_with_factors(cov, w, B, factor_cov, resid_var)


# ── 边界情况 ──────────────────────────────────────────────────────────────────


def test_zero_volatility_portfolio():
    """零波动组合 (协方差全零): risk=0, contributions=0。"""
    decomposer = RiskDecomposer()
    cov = np.zeros((2, 2))
    w = np.array([0.5, 0.5])
    result = decomposer.decompose(cov, w, now=T0)
    assert result.total_risk == 0.0
    assert np.all(result.mcr == 0)
    assert np.all(result.ccr == 0)


def test_to_dict_contains_all_fields():
    decomposer = RiskDecomposer()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    w = np.array([0.6, 0.4])
    result = decomposer.decompose(cov, w, assets=["A", "B"], now=T0)
    d = result.to_dict()
    for key in (
        "total_risk",
        "total_variance",
        "mcr",
        "ccr",
        "pct_contribution",
        "weights",
        "assets",
        "factor_risk",
        "factor_variance",
        "residual_risk",
        "residual_variance",
        "factor_contribution_pct",
        "residual_contribution_pct",
    ):
        assert key in d
    assert d["assets"] == ["A", "B"]


def test_multi_factor_model():
    """双因子模型分解。"""
    decomposer = RiskDecomposer()
    N = 4
    np.random.seed(123)
    B = np.random.randn(N, 2) * 0.5  # (4, 2)
    factor_cov = np.array([[0.04, 0.01], [0.01, 0.02]])
    resid_var = np.array([0.01, 0.02, 0.015, 0.025])
    cov = B @ factor_cov @ B.T + np.diag(resid_var)
    w = np.array([0.25, 0.25, 0.25, 0.25])
    result = decomposer.decompose_with_factors(cov, w, B, factor_cov, resid_var, now=T0)
    assert result.has_factor_model
    assert result.factor_variance + result.residual_variance == pytest.approx(result.total_variance, rel=1e-9)
    # CCR 守恒
    assert np.sum(result.ccr) == pytest.approx(result.total_risk, rel=1e-9)
