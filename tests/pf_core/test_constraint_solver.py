# [BLUEPRINT] MOD-PF-006 | docs/03_modules/_domain_portfolio_core/constraint_solver/blueprint.md | §
# [TTL] permanent
"""ConstraintSolver 单元测试 (MOD-PF-006)。"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from zephyr.pf_core.core.constraint_solver import (
    ConstraintSolver,
    ConstraintSolverConfig,
    ConstraintSolveResult,
    ConstraintViolationError,
    CorrelationGateFailure,
)
from zephyr.shared.contracts.risk_limits import RiskLimits

T0 = datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc)


def _rl(**kw) -> RiskLimits:
    """构造 RiskLimits, 默认 max_single=0.10, max_gross_lev=1.0。"""
    defaults = dict(as_of_date=T0, idempotency_key="test-k1")
    defaults.update(kw)
    return RiskLimits(**defaults)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_invalid_max_iter():
    with pytest.raises(ConstraintViolationError):
        ConstraintSolverConfig(max_iter=0)


def test_config_invalid_tol():
    with pytest.raises(ConstraintViolationError):
        ConstraintSolverConfig(tol=0)


def test_config_crowding_threshold_out_of_range():
    with pytest.raises(ConstraintViolationError):
        ConstraintSolverConfig(crowding_threshold=1.5)


def test_config_hard_lt_soft():
    with pytest.raises(ConstraintViolationError):
        ConstraintSolverConfig(crowding_threshold=0.8, crowding_hard_threshold=0.7)


def test_config_crowding_scale_zero():
    with pytest.raises(ConstraintViolationError):
        ConstraintSolverConfig(crowding_scale=0)


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_empty_weights_raises():
    solver = ConstraintSolver()
    with pytest.raises(ConstraintViolationError):
        solver.solve({}, _rl())


def test_negative_weights_raises():
    solver = ConstraintSolver()
    with pytest.raises(ConstraintViolationError):
        solver.solve({"A": -0.1, "B": 0.5}, _rl())


def test_assets_length_mismatch():
    solver = ConstraintSolver()
    with pytest.raises(ConstraintViolationError):
        solver.solve(np.array([0.3, 0.4, 0.3]), _rl(), assets=["A", "B"])


def test_under_invested_portfolio():
    """max_single_position × N < max_gross_leverage → 欠配 (不报错)。"""
    solver = ConstraintSolver()
    result = solver.solve(
        {"A": 0.5, "B": 0.5},
        _rl(max_single_position=0.10, max_gross_leverage=1.0),
    )
    # 2 × 0.10 = 0.20 < 1.0, 组合欠配但有效
    assert float(np.sum(result.weights)) <= 0.20 + 1e-9
    assert result.weights.max() <= 0.10 + 1e-9


# ── C7: 单标的仓位上限 ──────────────────────────────────────────────────────


def test_single_position_clip():
    solver = ConstraintSolver()
    result = solver.solve({"A": 0.15, "B": 0.15, "C": 0.15}, _rl(max_single_position=0.10))
    assert result.weights.max() <= 0.10 + 1e-9
    assert any(v.constraint_id == "C7" for v in result.violations)


def test_symbol_override():
    """symbol_overrides 允许个别标的超限。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.10, symbol_overrides={"A": 0.20})
    result = solver.solve({"A": 0.20, "B": 0.10, "C": 0.10}, rl)
    assert result.weights[0] <= 0.20 + 1e-9
    assert result.weights[1] <= 0.10 + 1e-9


def test_min_position_floor():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50, min_single_position=0.05)
    result = solver.solve({"A": 0.01, "B": 0.49}, rl)
    # A 被提升到 min_single_position
    assert result.weights[0] >= 0.05 - 1e-9


# ── C1: 行业绝对集中度 ───────────────────────────────────────────────────────


def test_sector_absolute_clip():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50, max_sector_concentration=0.30)
    sector = {"A": "tech", "B": "tech", "C": "health", "D": "health"}
    w = {"A": 0.40, "B": 0.40, "C": 0.10, "D": 0.10}
    result = solver.solve(w, rl, sector_mapping=sector)
    # tech 行业 ≤ 30%
    tech_w = result.weights[0] + result.weights[1]
    assert tech_w <= 0.30 + 1e-6
    assert any(v.constraint_id == "C1" for v in result.violations)


# ── C2: 行业相对偏移 ────────────────────────────────────────────────────────


def test_sector_relative_clip():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50, max_sector_concentration=0.60)
    sector = {"A": "tech", "B": "tech", "C": "health"}
    benchmark = {"tech": 0.40, "health": 0.60}
    w = {"A": 0.30, "B": 0.30, "C": 0.40}  # tech=60%, dev=20%>10%
    result = solver.solve(w, rl, sector_mapping=sector, benchmark_sector_weights=benchmark)
    assert any(v.constraint_id == "C2" for v in result.violations)


# ── C5: 标的相关性 ──────────────────────────────────────────────────────────


def test_correlation_clip():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50)
    assets = ["A", "B", "C"]
    w = {"A": 0.40, "B": 0.40, "C": 0.20}
    # A-B 高相关 0.8, A-C 低相关 0.2
    corr = np.array([[1.0, 0.85, 0.2], [0.85, 1.0, 0.3], [0.2, 0.3, 1.0]])
    result = solver.solve(w, rl, assets=assets, correlation_matrix=corr)
    assert any(v.constraint_id == "C5" for v in result.violations)


def test_correlation_matrix_shape_mismatch():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50)
    with pytest.raises(CorrelationGateFailure):
        solver.solve(
            {"A": 0.5, "B": 0.5},
            rl,
            assets=["A", "B"],
            correlation_matrix=np.eye(3),
        )


# ── C6: 风格因子暴露 ────────────────────────────────────────────────────────


def test_style_exposure_clip():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50)
    style = {"A": 0.5, "B": 0.5, "C": -0.1}  # 加权暴露超 0.3σ
    w = {"A": 0.40, "B": 0.40, "C": 0.20}
    result = solver.solve(w, rl, style_exposures=style)
    assert any(v.constraint_id == "C6" for v in result.violations)


# ── C3: 市值暴露 ─────────────────────────────────────────────────────────────


def test_market_cap_exposure_clip():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50)
    mc = {"A": 0.6, "B": 0.5, "C": -0.2}
    w = {"A": 0.40, "B": 0.40, "C": 0.20}
    result = solver.solve(w, rl, market_cap_exposures=mc)
    assert any(v.constraint_id == "C3" for v in result.violations)


# ── 拥挤检测 ────────────────────────────────────────────────────────────────


def test_crowding_soft_halve():
    """ρ>0.8 → 权重减半。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50)
    assets = ["A", "B", "C"]
    w = {"A": 0.40, "B": 0.40, "C": 0.20}
    corr = np.array([[1.0, 0.85, 0.2], [0.85, 1.0, 0.3], [0.2, 0.3, 1.0]])
    result = solver.solve(w, rl, assets=assets, correlation_matrix=corr)
    assert any(
        v.constraint_name == "crowding_soft" for v in result.violations
    )


def test_crowding_hard_zero():
    """ρ>0.9 → 仅保留其一。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50)
    assets = ["A", "B", "C"]
    w = {"A": 0.40, "B": 0.30, "C": 0.30}
    corr = np.array([[1.0, 0.95, 0.2], [0.95, 1.0, 0.3], [0.2, 0.3, 1.0]])
    result = solver.solve(w, rl, assets=assets, correlation_matrix=corr)
    # B 应被清零 (A 权重更大)
    assert result.weights[1] == 0.0
    assert any(
        v.constraint_name == "crowding_hard" for v in result.violations
    )


# ── 杠杆约束 ────────────────────────────────────────────────────────────────


def test_leverage_clip():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50, max_gross_leverage=0.80)
    w = {"A": 0.40, "B": 0.40, "C": 0.40}  # Σ=1.2 > 0.80
    result = solver.solve(w, rl)
    assert float(np.sum(result.weights)) <= 0.80 + 1e-6
    assert any(v.constraint_name == "gross_leverage" for v in result.violations)


# ── 收敛性 ──────────────────────────────────────────────────────────────────


def test_converges_with_valid_input():
    solver = ConstraintSolver()
    rl = _rl()
    w = {"A": 0.05, "B": 0.05, "C": 0.05, "D": 0.05,
         "E": 0.05, "F": 0.05, "G": 0.05, "H": 0.05,
         "I": 0.05, "J": 0.05}
    result = solver.solve(w, rl)
    assert result.converged
    assert result.iterations <= 100


def test_not_converged_returns_last():
    """max_iter=1 时不收敛仍返回结果。"""
    solver = ConstraintSolver(ConstraintSolverConfig(max_iter=1))
    rl = _rl(max_single_position=0.50, max_sector_concentration=0.30)
    sector = {"A": "s1", "B": "s1", "C": "s2", "D": "s2"}
    w = {"A": 0.45, "B": 0.45, "C": 0.05, "D": 0.05}
    result = solver.solve(w, rl, sector_mapping=sector)
    assert not result.converged
    assert result.iterations == 1
    assert len(result.weights) == 4


# ── 退化场景 ────────────────────────────────────────────────────────────────


def test_single_asset():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=1.0, max_gross_leverage=1.0)
    result = solver.solve({"A": 1.0}, rl)
    assert len(result.weights) == 1
    assert result.weights[0] <= 1.0 + 1e-9


def test_all_zero_weights():
    """全零权重 → 原样返回 (不报错)。"""
    solver = ConstraintSolver()
    rl = _rl()
    result = solver.solve({"A": 0.0, "B": 0.0, "C": 0.0}, rl)
    assert float(np.sum(result.weights)) == 0.0


def test_numpy_array_input():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50)
    w = np.array([0.40, 0.40, 0.20])
    result = solver.solve(w, rl, assets=["A", "B", "C"])
    assert result.weights.shape == (3,)
    assert float(np.sum(result.weights)) <= 1.0 + 1e-6


# ── 不变量验证 ──────────────────────────────────────────────────────────────


def test_invariant_max_single_position():
    """输出权重 w_i ≤ max_single_position。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.10)
    w = {f"stock_{i}": 0.05 for i in range(20)}
    result = solver.solve(w, rl)
    assert result.weights.max() <= 0.10 + 1e-9


def test_invariant_gross_leverage():
    """输出 Σw ≤ max_gross_leverage。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.20, max_gross_leverage=0.90)
    w = {f"s{i}": 0.15 for i in range(10)}  # Σ=1.5 > 0.90
    result = solver.solve(w, rl)
    assert float(np.sum(result.weights)) <= 0.90 + 1e-6


def test_invariant_same_dimension():
    """输出与输入同维度。"""
    solver = ConstraintSolver()
    rl = _rl()
    w = {f"s{i}": 0.02 for i in range(50)}
    result = solver.solve(w, rl)
    assert len(result.weights) == 50


def test_invariant_non_negative():
    """输出权重非负 (long-only)。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.30)
    w = {"A": 0.40, "B": 0.35, "C": 0.25}
    corr = np.array([[1.0, 0.95, 0.2], [0.95, 1.0, 0.3], [0.2, 0.3, 1.0]])
    result = solver.solve(w, rl, assets=["A", "B", "C"], correlation_matrix=corr)
    assert np.all(result.weights >= -1e-12)


# ── 结果序列化 ──────────────────────────────────────────────────────────────


def test_result_to_dict():
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.10)
    w = {"A": 0.15, "B": 0.15, "C": 0.15, "D": 0.15,
         "E": 0.15, "F": 0.15, "G": 0.05, "H": 0.05}
    result = solver.solve(w, rl)
    d = result.to_dict()
    assert "weights" in d
    assert "violations" in d
    assert "converged" in d
    assert isinstance(d["weights"], list)
    assert isinstance(d["violations"], list)


# ── 幂等性 ──────────────────────────────────────────────────────────────────


def test_idempotent_solve():
    """相同输入多次求解结果一致。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.15)
    w = {"A": 0.20, "B": 0.30, "C": 0.20, "D": 0.15, "E": 0.15}
    r1 = solver.solve(w, rl)
    r2 = solver.solve(w, rl)
    np.testing.assert_allclose(r1.weights, r2.weights)
    assert r1.converged == r2.converged
    assert r1.iterations == r2.iterations


# ── AI-NIGHT-001 坍缩防护（#205/#207/兜底）────────────────────────────────


def test_soft_crowding_one_shot_no_collapse():
    """#205：软拥挤一次性缩放——原实现每轮迭代重复减半，{0.5,0.5} ρ=0.85 实证 16 轮
    Σw≈8.3e-7 且 converged=True（静默清零组合）。修复后同一对只缩一次。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.60)
    assets = ["A", "B"]
    w = {"A": 0.5, "B": 0.5}
    corr = np.array([[1.0, 0.85], [0.85, 1.0]])
    result = solver.solve(w, rl, assets=assets, correlation_matrix=corr)
    total = float(np.sum(result.weights))
    assert total > 0.1, f"软拥挤一次性缩放后 Σw={total} 不应坍缩（原实证 8.3e-7）"
    assert result.converged
    # 一次性：soft violation 仅一条（首轮响应后不重复记录）
    soft = [v for v in result.violations if v.constraint_name == "crowding_soft"]
    assert len(soft) == 1


def test_same_sign_style_exposure_infeasible_no_collapse():
    """#207：全同号风格暴露下统一缩放数学无效（加权均值对缩放不变）——原实现每轮
    ×scale 必坍缩（实证 4 标的 +1σ → Σw≈1.2e-6 且 converged=True）。修复后标
    infeasible 不缩放（fail-visible）。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.40)
    assets = ["A", "B", "C", "D"]
    w = {"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25}
    style = {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0}  # 全 +1σ 同号（上限 0.3σ）
    result = solver.solve(w, rl, assets=assets, style_exposures=style)
    total = float(np.sum(result.weights))
    assert total > 0.9, f"infeasible 不缩放，Σw={total} 应保持 ~1.0（原实证 1.2e-6）"
    assert any(v.constraint_name == "style_exposure_infeasible" for v in result.violations)


def test_mixed_sign_exposure_still_scales():
    """#207 对照组：存在反向暴露锚时缩放仍生效（加权均值可移动，约束可达）。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.40)
    assets = ["A", "B", "C", "D"]
    w = {"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25}
    # A/B +1.5σ，C/D -1.5σ（有反向锚）→ 缩放有效，不应标 infeasible
    style = {"A": 1.5, "B": 1.5, "C": -1.5, "D": -1.5}
    result = solver.solve(w, rl, assets=assets, style_exposures=style)
    assert not any(v.constraint_name == "style_exposure_infeasible" for v in result.violations)
    assert float(np.sum(result.weights)) > 0.5  # 不坍缩


def test_collapse_guard_not_triggered_on_legit_hard_crowding():
    """坍缩兜底不误报：硬拥挤连环清零属合法约束响应（保留最大者），Σw 量级正常。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.90)
    assets = ["A", "B", "C"]
    w = {"A": 0.34, "B": 0.33, "C": 0.33}
    corr = np.ones((3, 3)) * 0.99
    np.fill_diagonal(corr, 1.0)
    result = solver.solve(w, rl, assets=assets, correlation_matrix=corr)
    total = float(np.sum(result.weights))
    assert total > 0.1, "硬拥挤保留最大者，量级正常"
    assert not any(v.constraint_id == "COLLAPSE" for v in result.violations)


# ── AI-NIGHT-001 #208-②③：非有限输入 fail-closed + 零权重刻意排除 ─────────────


def test_nan_weights_raise_fail_closed():
    """#208-②：NaN 权重必须 fail-closed——原实现 np.any(w<0) 对 NaN 为 False，
    NaN 静默通过校验进入迭代投影，全组合权重被污染为 NaN（H 级安全模块
    最恶劣失效形态）。与空/负权重同口径 raise ConstraintViolationError。"""
    solver = ConstraintSolver()
    with pytest.raises(ConstraintViolationError):
        solver.solve({"A": float("nan"), "B": 0.5}, _rl())


def test_inf_weights_raise_fail_closed():
    """#208-②：+Inf 权重同为非有限输入（Σw=Inf 绕过杠杆约束），同口径拒绝。"""
    solver = ConstraintSolver()
    with pytest.raises(ConstraintViolationError):
        solver.solve({"A": float("inf"), "B": 0.5}, _rl())


def test_nan_ndarray_weights_raise_fail_closed():
    """#208-②：ndarray 输入路径同样 fail-closed（dict/ndarray 两入口同口径）。"""
    solver = ConstraintSolver()
    with pytest.raises(ConstraintViolationError):
        solver.solve(np.array([0.3, float("nan"), 0.4]), _rl(), assets=["A", "B", "C"])


def test_zero_weight_deliberate_exclusion_not_raised():
    """#208-③：输入 w=0 是"刻意排除"语义，不应被 min_single_position 每轮强制
    抬回——区分"零权重排除"与"小权重抬升"（0<w<min_pos 仍抬升，由既有
    test_min_position_floor 用 w=0.01 作对照）。"""
    solver = ConstraintSolver()
    rl = _rl(max_single_position=0.50, min_single_position=0.05)
    result = solver.solve({"A": 0.0, "B": 0.5}, rl)
    assert result.weights[0] == 0.0, (
        f"刻意排除（w=0）的标的不应被 min_pos 抬回，实际 {result.weights[0]}"
    )
