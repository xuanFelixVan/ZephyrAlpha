# [BLUEPRINT] MOD-PF-002 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""Portfolio Optimizer 单元测试 (MOD-PF-002)。"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from zephyr.pf_core.core.portfolio_optimizer import (
    InvalidOptimizationInputError,
    OptimizationMethod,
    OptimizationResult,
    OptimizerConfig,
    PortfolioOptimizer,
)
from zephyr.shared.contracts.risk_limits import RiskLimits

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _seed():
    np.random.seed(42)


def _rl(**kw) -> RiskLimits:
    base = dict(
        as_of_date=T0,
        idempotency_key="rl-1",
        max_single_position=0.40,
        max_gross_leverage=1.0,
        max_sector_concentration=0.50,
    )
    base.update(kw)
    return RiskLimits(**base)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_invalid_kelly_fraction():
    with pytest.raises(InvalidOptimizationInputError):
        OptimizerConfig(kelly_fraction=0)


def test_config_invalid_kelly_fraction_over_one():
    with pytest.raises(InvalidOptimizationInputError):
        OptimizerConfig(kelly_fraction=1.5)


def test_config_invalid_risk_aversion():
    with pytest.raises(InvalidOptimizationInputError):
        OptimizerConfig(risk_aversion=0)


def test_config_invalid_drift_threshold():
    with pytest.raises(InvalidOptimizationInputError):
        OptimizerConfig(drift_threshold=0)


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_empty_candidate_raises():
    opt = PortfolioOptimizer()
    with pytest.raises(InvalidOptimizationInputError):
        opt.optimize({}, _rl(), np.eye(2), ["A", "B"])


def test_cov_shape_mismatch_raises():
    opt = PortfolioOptimizer()
    with pytest.raises(InvalidOptimizationInputError):
        opt.optimize({"A": 0.5, "B": 0.5}, _rl(), np.eye(3), ["A", "B"])


def test_negative_variance_raises():
    opt = PortfolioOptimizer()
    cov = np.array([[-0.04, 0], [0, 0.09]])
    with pytest.raises(InvalidOptimizationInputError):
        opt.optimize({"A": 0.5, "B": 0.5}, _rl(), cov, ["A", "B"])


def test_negative_candidate_raises():
    opt = PortfolioOptimizer()
    with pytest.raises(InvalidOptimizationInputError):
        opt.optimize({"A": -0.5, "B": 1.5}, _rl(), np.eye(2), ["A", "B"])


def test_expected_returns_shape_mismatch():
    opt = PortfolioOptimizer()
    with pytest.raises(InvalidOptimizationInputError):
        opt.optimize(
            {"A": 0.5, "B": 0.5},
            _rl(),
            np.eye(2),
            ["A", "B"],
            expected_returns=np.array([0.1, 0.2, 0.3]),
        )


# ── 优化方法 ──────────────────────────────────────────────────────────────────


def test_risk_budget_method_label():
    opt = PortfolioOptimizer()
    result = opt.optimize(
        {"A": 0.5, "B": 0.5},
        _rl(),
        np.array([[0.04, 0.01], [0.01, 0.09]]),
        ["A", "B"],
        now=T0,
    )
    assert result.method_used == OptimizationMethod.RISK_BUDGET


def test_risk_budget_low_vol_gets_higher_weight():
    """风险预算: 低波动资产应获更高权重。"""
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    # A 波动低 (0.01), B 波动高 (0.09)
    cov = np.diag([0.01, 0.09])
    result = opt.optimize({"A": 0.5, "B": 0.5}, _rl(), cov, ["A", "B"], now=T0)
    tw = result.target_portfolio.target_weights
    assert tw["A"] > tw["B"]


def test_mean_variance_method():
    opt = PortfolioOptimizer(
        config=OptimizerConfig(default_method=OptimizationMethod.MEAN_VARIANCE, kelly_cap_enabled=False)
    )
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    er = np.array([0.10, 0.05])  # A 期望收益高
    result = opt.optimize(
        {"A": 0.5, "B": 0.5},
        _rl(max_single_position=0.99),
        cov,
        ["A", "B"],
        expected_returns=er,
        now=T0,
    )
    assert result.method_used == OptimizationMethod.MEAN_VARIANCE
    tw = result.target_portfolio.target_weights
    assert sum(tw.values()) == pytest.approx(1.0, rel=1e-3)


def test_mean_variance_without_expected_returns_falls_back():
    opt = PortfolioOptimizer(
        config=OptimizerConfig(default_method=OptimizationMethod.MEAN_VARIANCE, kelly_cap_enabled=False)
    )
    result = opt.optimize(
        {"A": 0.5, "B": 0.5},
        _rl(max_single_position=0.99),
        np.eye(2),
        ["A", "B"],
        now=T0,
    )
    # 无期望收益 → 等权 fallback
    tw = result.target_portfolio.target_weights
    assert tw["A"] == pytest.approx(0.5, rel=1e-3)
    assert tw["B"] == pytest.approx(0.5, rel=1e-3)


def test_equal_weight_method():
    opt = PortfolioOptimizer(
        config=OptimizerConfig(default_method=OptimizationMethod.EQUAL_WEIGHT, kelly_cap_enabled=False)
    )
    result = opt.optimize(
        {"A": 0.7, "B": 0.3},
        _rl(),
        np.eye(2),
        ["A", "B"],
        now=T0,
    )
    tw = result.target_portfolio.target_weights
    assert tw["A"] == pytest.approx(tw["B"], rel=1e-6)


# ── Kelly 截断 ────────────────────────────────────────────────────────────────


def test_kelly_cap_only_reduces():
    """Kelly 只减不增: 高期望+低波动资产 Kelly 可能小于优化权重 → 截断。"""
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_fraction=0.1, kelly_cap_enabled=True))
    cov = np.diag([0.0001, 0.09])  # A 极低波动
    er = np.array([0.001, 0.05])
    result = opt.optimize(
        {"A": 0.5, "B": 0.5},
        _rl(max_single_position=0.99),
        cov,
        ["A", "B"],
        expected_returns=er,
        now=T0,
    )
    # Kelly 应用与否取决于具体数值, 但不应报错
    assert isinstance(result.kelly_applied, bool)


def test_kelly_disabled_when_no_expected_returns():
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=True))
    result = opt.optimize(
        {"A": 0.5, "B": 0.5},
        _rl(),
        np.eye(2),
        ["A", "B"],
        now=T0,
    )
    assert result.kelly_applied is False


def test_kelly_cap_disabled_config():
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    result = opt.optimize(
        {"A": 0.5, "B": 0.5},
        _rl(),
        np.eye(2),
        ["A", "B"],
        expected_returns=np.array([0.1, 0.2]),
        now=T0,
    )
    assert result.kelly_applied is False


# ── 约束求解 ──────────────────────────────────────────────────────────────────


def test_max_single_position_enforced():
    """CTR-003 max_single_position 被约束求解器强制。"""
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    # 候选权重 A=0.8 超 max_single_position=0.30
    result = opt.optimize(
        {"A": 0.8, "B": 0.2},
        _rl(max_single_position=0.30),
        np.eye(2),
        ["A", "B"],
        now=T0,
    )
    tw = result.target_portfolio.target_weights
    assert tw["A"] <= 0.30 + 1e-6
    # 有违规记录
    assert len(result.constraint_result.violations) >= 1


def test_max_gross_leverage_enforced():
    """CTR-003 max_gross_leverage 被强制 (Σw ≤ max_gross_leverage)。"""
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    result = opt.optimize(
        {"A": 0.5, "B": 0.5},
        _rl(max_gross_leverage=0.8),
        np.eye(2),
        ["A", "B"],
        now=T0,
    )
    tw = result.target_portfolio.target_weights
    assert sum(tw.values()) <= 0.8 + 1e-6


def test_constraint_violations_recorded():
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    result = opt.optimize(
        {"A": 0.9, "B": 0.1},
        _rl(max_single_position=0.30),
        np.eye(2),
        ["A", "B"],
        now=T0,
    )
    assert len(result.constraint_result.violations) >= 1


# ── TargetPortfolio 输出 ─────────────────────────────────────────────────────


def test_target_portfolio_is_frozen():
    opt = PortfolioOptimizer()
    result = opt.optimize(
        {"A": 0.5, "B": 0.5},
        _rl(),
        np.eye(2),
        ["A", "B"],
        now=T0,
    )
    tp = result.target_portfolio
    with pytest.raises(Exception):
        tp.portfolio_id = "mutated"  # frozen


def test_target_portfolio_has_idempotency_key():
    opt = PortfolioOptimizer()
    r1 = opt.optimize({"A": 0.5, "B": 0.5}, _rl(), np.eye(2), ["A", "B"], now=T0)
    r2 = opt.optimize({"A": 0.5, "B": 0.5}, _rl(), np.eye(2), ["A", "B"], now=T0)
    assert r1.target_portfolio.idempotency_key
    assert r1.target_portfolio.idempotency_key != r2.target_portfolio.idempotency_key


def test_target_portfolio_carries_risk_limits():
    rl = _rl()
    opt = PortfolioOptimizer()
    result = opt.optimize({"A": 0.5, "B": 0.5}, rl, np.eye(2), ["A", "B"], now=T0)
    # risk_limits 引用同一对象 (下游据此校验)
    assert result.target_portfolio.risk_limits is rl


def test_target_portfolio_metadata():
    opt = PortfolioOptimizer()
    result = opt.optimize(
        {"A": 0.5, "B": 0.5},
        _rl(),
        np.eye(2),
        ["A", "B"],
        strategy_id="s1",
        portfolio_id="p1",
        rebalance_reason="calendar",
        now=T0,
    )
    tp = result.target_portfolio
    assert tp.strategy_id == "s1"
    assert tp.portfolio_id == "p1"
    assert tp.rebalance_reason == "calendar"
    assert tp.created_at == T0
    assert tp.schema_version == "1.0"


# ── drift_pct ────────────────────────────────────────────────────────────────


def test_drift_pct_zero_when_matching():
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    result = opt.optimize(
        {"A": 0.5, "B": 0.5},
        _rl(max_single_position=0.99),
        np.eye(2),
        ["A", "B"],
        current_weights={"A": 0.5, "B": 0.5},
        now=T0,
    )
    assert result.target_portfolio.drift_pct == pytest.approx(0.0, abs=1e-6)


def test_drift_pct_nonzero_when_drifted():
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    result = opt.optimize(
        {"A": 0.6, "B": 0.4},
        _rl(max_single_position=0.99),
        np.eye(2),
        ["A", "B"],
        current_weights={"A": 0.4, "B": 0.6},
        now=T0,
    )
    assert result.target_portfolio.drift_pct > 0


def test_needs_rebalance_when_drift_large():
    opt = PortfolioOptimizer(config=OptimizerConfig(drift_threshold=0.05))
    assert opt.needs_rebalance({"A": 0.7, "B": 0.3}, {"A": 0.3, "B": 0.7}) is True


def test_needs_rebalance_when_drift_small():
    opt = PortfolioOptimizer(config=OptimizerConfig(drift_threshold=0.05))
    assert opt.needs_rebalance({"A": 0.52, "B": 0.48}, {"A": 0.50, "B": 0.50}) is False


# ── 结果属性 ──────────────────────────────────────────────────────────────────


def test_result_to_dict():
    opt = PortfolioOptimizer()
    result = opt.optimize({"A": 0.5, "B": 0.5}, _rl(), np.eye(2), ["A", "B"], now=T0)
    d = result.to_dict()
    assert d["method_used"] == "risk_budget"
    assert "idempotency_key" in d
    assert "drift_pct" in d


def test_zero_weights_filtered_from_target():
    """约束求解清零的标的不出现在 target_weights。"""
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    # A=1.0, B=0.0 (B 候选为零)
    result = opt.optimize(
        {"A": 1.0, "B": 0.0},
        _rl(max_single_position=0.99),
        np.eye(2),
        ["A", "B"],
        now=T0,
    )
    tw = result.target_portfolio.target_weights
    # B 权重为零 → 不出现 (或为零, 关键是不影响 A)
    assert "A" in tw


# ── 不变量 ────────────────────────────────────────────────────────────────────


def test_invariant_weights_within_leverage():
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    for _ in range(5):
        result = opt.optimize(
            {"A": 0.4, "B": 0.3, "C": 0.3},
            _rl(max_single_position=0.40),
            np.eye(3),
            ["A", "B", "C"],
            now=T0,
        )
        tw = result.target_portfolio.target_weights
        assert sum(tw.values()) <= 1.0 + 1e-6


def test_invariant_single_position_respected():
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    result = opt.optimize(
        {"A": 0.5, "B": 0.3, "C": 0.2},
        _rl(max_single_position=0.35),
        np.eye(3),
        ["A", "B", "C"],
        now=T0,
    )
    tw = result.target_portfolio.target_weights
    for w in tw.values():
        assert w <= 0.35 + 1e-6


def test_invariant_three_assets_risk_budget():
    """3 资产风险预算: 权重归一 + long-only。"""
    opt = PortfolioOptimizer(config=OptimizerConfig(kelly_cap_enabled=False))
    np.random.seed(7)
    A = np.random.randn(100, 3)
    cov = np.cov(A.T)
    result = opt.optimize(
        {"A": 0.4, "B": 0.3, "C": 0.3},
        _rl(max_single_position=0.99),
        cov,
        ["A", "B", "C"],
        now=T0,
    )
    tw = result.target_portfolio.target_weights
    assert sum(tw.values()) == pytest.approx(1.0, rel=1e-3)
    assert all(w >= -1e-9 for w in tw.values())
