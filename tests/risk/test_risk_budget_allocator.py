# [BLUEPRINT] MOD-RK-08 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""RiskBudgetAllocator 单元测试 (MOD-RK-08)。"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from zephyr.risk.core.risk_budget_allocator import (
    BudgetAllocationResult,
    BudgetConfig,
    BudgetOptimizationError,
    InvalidBudgetInputError,
    RiskBudgetAllocator,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _seed():
    np.random.seed(42)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_invalid_max_iter():
    with pytest.raises(InvalidBudgetInputError):
        BudgetConfig(max_iter=5)


def test_config_invalid_ftol():
    with pytest.raises(InvalidBudgetInputError):
        BudgetConfig(ftol=0)


def test_config_invalid_drift_threshold():
    with pytest.raises(InvalidBudgetInputError):
        BudgetConfig(rebalance_drift_threshold=0)


def test_config_max_lt_min_weight():
    with pytest.raises(InvalidBudgetInputError):
        BudgetConfig(min_weight=0.3, max_weight=0.1)


def test_config_negative_min_weight():
    with pytest.raises(InvalidBudgetInputError):
        BudgetConfig(min_weight=-0.1)


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_cov_must_be_square():
    alloc = RiskBudgetAllocator()
    with pytest.raises(InvalidBudgetInputError):
        alloc.equal_risk_contribution(np.array([[1, 2], [3, 4], [5, 6]]))


def test_cov_too_small():
    alloc = RiskBudgetAllocator()
    with pytest.raises(InvalidBudgetInputError):
        alloc.equal_risk_contribution(np.array([[0.04]]))


def test_cov_negative_variance():
    alloc = RiskBudgetAllocator()
    with pytest.raises(InvalidBudgetInputError):
        alloc.equal_risk_contribution(np.array([[-0.04, 0], [0, 0.09]]))


def test_target_budgets_shape_mismatch():
    alloc = RiskBudgetAllocator()
    cov = np.eye(3)
    with pytest.raises(InvalidBudgetInputError):
        alloc.allocate_by_budget(cov, np.array([0.5, 0.5]))  # 应为 3


def test_target_budgets_non_positive():
    alloc = RiskBudgetAllocator()
    cov = np.eye(2)
    with pytest.raises(InvalidBudgetInputError):
        alloc.allocate_by_budget(cov, np.array([0.5, -0.5]))


# ── 等风险贡献 (ERC) ─────────────────────────────────────────────────────────


def test_erc_equal_vol_zero_corr_equal_weights():
    """等波动 + 零相关 → ERC 权重应相等。"""
    alloc = RiskBudgetAllocator()
    cov = np.diag([0.04, 0.04, 0.04])  # 等方差
    result = alloc.equal_risk_contribution(cov, now=T0)
    assert result.is_erc
    assert np.sum(result.weights) == pytest.approx(1.0)
    # 等权 1/3
    for w in result.weights:
        assert w == pytest.approx(1 / 3, rel=1e-3)


def test_erc_pct_contributions_equal():
    """ERC: 各资产百分比贡献应接近 1/N。"""
    alloc = RiskBudgetAllocator()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])  # 不等波动
    result = alloc.equal_risk_contribution(cov, now=T0)
    N = 2
    for p in result.pct_contributions:
        assert p == pytest.approx(1 / N, abs=0.02)  # 容差 2%


def test_erc_weights_sum_to_one():
    alloc = RiskBudgetAllocator()
    cov = np.array([[0.04, 0.01, 0.005], [0.01, 0.09, 0.02], [0.005, 0.02, 0.0225]])
    result = alloc.equal_risk_contribution(cov, now=T0)
    assert np.sum(result.weights) == pytest.approx(1.0)


def test_erc_weights_long_only():
    """ERC 权重应非负 (long-only)。"""
    alloc = RiskBudgetAllocator()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    result = alloc.equal_risk_contribution(cov, now=T0)
    assert np.all(result.weights >= -1e-9)


def test_erc_lower_vol_gets_higher_weight():
    """ERC: 低波动资产应获得更高权重 (风险平价特性)。"""
    alloc = RiskBudgetAllocator()
    cov = np.diag([0.01, 0.09])  # 资产0波动低
    result = alloc.equal_risk_contribution(cov, now=T0)
    assert result.weights[0] > result.weights[1]


def test_erc_ccr_sums_to_total_risk():
    """CCR 之和 = σ_p (守恒)。"""
    alloc = RiskBudgetAllocator()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    result = alloc.equal_risk_contribution(cov, now=T0)
    assert np.sum(result.risk_contributions) == pytest.approx(result.total_risk, rel=1e-6)


def test_erc_contribution_error_small():
    """ERC 收敛后最大贡献偏差应很小。"""
    alloc = RiskBudgetAllocator()
    cov = np.array([[0.04, 0.01, 0.005], [0.01, 0.09, 0.02], [0.005, 0.02, 0.0225]])
    result = alloc.equal_risk_contribution(cov, now=T0)
    assert result.contribution_error < 0.05  # 5% 容差


# ── 自定义预算 ────────────────────────────────────────────────────────────────


def test_budget_normalize_target():
    """target_budgets 自动归一化。"""
    alloc = RiskBudgetAllocator()
    cov = np.eye(2)
    result = alloc.allocate_by_budget(cov, np.array([3.0, 7.0]), now=T0)  # 30/70
    assert result.target_pct == pytest.approx([0.3, 0.7])


def test_budget_matches_target_pct():
    """自定义预算: 实际百分比贡献应接近目标。"""
    alloc = RiskBudgetAllocator()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    result = alloc.allocate_by_budget(cov, np.array([0.3, 0.7]), now=T0)
    assert result.pct_contributions[0] == pytest.approx(0.3, abs=0.03)
    assert result.pct_contributions[1] == pytest.approx(0.7, abs=0.03)


def test_budget_method_label():
    alloc = RiskBudgetAllocator()
    cov = np.eye(2)
    result = alloc.allocate_by_budget(cov, np.array([0.4, 0.6]), now=T0)
    assert result.method == "budget"
    assert not result.is_erc


def test_budget_higher_budget_higher_weight():
    """高预算资产应获得更高权重 (正相关)。"""
    alloc = RiskBudgetAllocator()
    cov = np.diag([0.04, 0.04])  # 等波动
    result = alloc.allocate_by_budget(cov, np.array([0.2, 0.8]), now=T0)
    assert result.weights[1] > result.weights[0]


# ── 约束处理 ──────────────────────────────────────────────────────────────────


def test_max_weight_constraint_respected():
    """max_weight 约束应被遵守 (须可行: N·max ≥ 1)。"""
    # 3 资产, max=0.4 → 0.4+0.4+0.2=1.0 可行
    cfg = BudgetConfig(max_weight=0.4)
    alloc = RiskBudgetAllocator(cfg)
    cov = np.diag([0.01, 0.09, 0.04])  # 资产0波动最低, ERC 想让其占高
    result = alloc.equal_risk_contribution(cov, now=T0)
    assert np.all(result.weights <= 0.4 + 1e-6)
    assert np.sum(result.weights) == pytest.approx(1.0)


def test_min_weight_constraint_respected():
    cfg = BudgetConfig(min_weight=0.1)
    alloc = RiskBudgetAllocator(cfg)
    cov = np.diag([0.01, 0.09])
    result = alloc.equal_risk_contribution(cov, now=T0)
    assert np.all(result.weights >= 0.1 - 1e-6)


# ── 再平衡触发 ────────────────────────────────────────────────────────────────


def test_needs_rebalance_when_drift_large():
    """当前权重与目标风险贡献漂移大 → 触发再平衡。"""
    alloc = RiskBudgetAllocator(BudgetConfig(rebalance_drift_threshold=0.05))
    cov = np.diag([0.01, 0.09])  # 资产0低波动
    target = alloc.equal_risk_contribution(cov).weights
    # 当前用等权 (偏离 ERC 目标)
    current = np.array([0.5, 0.5])
    assert alloc.needs_rebalance(cov, current, target)


def test_no_rebalance_when_close():
    """当前权重接近目标 → 不触发。"""
    alloc = RiskBudgetAllocator(BudgetConfig(rebalance_drift_threshold=0.05))
    cov = np.diag([0.04, 0.04])
    target = np.array([0.5, 0.5])
    current = np.array([0.51, 0.49])  # 接近
    assert not alloc.needs_rebalance(cov, current, target)


def test_needs_rebalance_returns_bool():
    alloc = RiskBudgetAllocator()
    cov = np.eye(2)
    result = alloc.needs_rebalance(cov, np.array([0.5, 0.5]), np.array([0.5, 0.5]))
    assert isinstance(result, bool)


# ── 风险贡献复用 (RK-16) ────────────────────────────────────────────────────


def test_risk_contributions_method():
    alloc = RiskBudgetAllocator()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    w = np.array([0.6, 0.4])
    sigma, ccr, pct = alloc.risk_contributions(cov, w)
    assert sigma == pytest.approx(np.sqrt(0.6**2 * 0.04 + 2 * 0.6 * 0.4 * 0.01 + 0.4**2 * 0.09))
    assert np.sum(pct) == pytest.approx(1.0)
    assert np.sum(ccr) == pytest.approx(sigma, rel=1e-9)


# ── 结果属性 ──────────────────────────────────────────────────────────────────


def test_to_dict_contains_all_fields():
    alloc = RiskBudgetAllocator()
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    result = alloc.equal_risk_contribution(cov, now=T0)
    d = result.to_dict()
    for key in (
        "weights",
        "total_risk",
        "risk_contributions",
        "pct_contributions",
        "target_pct",
        "contribution_error",
        "converged",
        "method",
    ):
        assert key in d
    assert d["method"] == "erc"


def test_erc_with_correlated_assets():
    """高相关资产的 ERC 仍应让百分比贡献接近相等。"""
    alloc = RiskBudgetAllocator()
    # 两资产高相关
    cov = np.array([[0.04, 0.05], [0.05, 0.09]])
    result = alloc.equal_risk_contribution(cov, now=T0)
    assert result.pct_contributions[0] == pytest.approx(0.5, abs=0.05)


def test_erc_four_assets():
    """4 资产 ERC: 每个贡献约 25%。"""
    alloc = RiskBudgetAllocator()
    np.random.seed(7)
    A = np.random.randn(1000, 4)
    cov = np.cov(A.T)
    result = alloc.equal_risk_contribution(cov, now=T0)
    for p in result.pct_contributions:
        assert p == pytest.approx(0.25, abs=0.03)
    assert np.sum(result.weights) == pytest.approx(1.0)
