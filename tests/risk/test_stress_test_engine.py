# [BLUEPRINT] MOD-RK-12 | docs/03_modules/_domain_risk/stress_test_engine/blueprint.md | §
# [TTL] permanent
"""StressTestEngine 单元测试 (MOD-RK-12)。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from zephyr.risk.core.stress_test_engine import (
    HISTORICAL_SCENARIOS,
    InvalidStressTestInputError,
    StressScenarioType,
    StressTestEngine,
)

T0 = datetime(2026, 8, 4, 16, 0, tzinfo=timezone.utc)


def t(offset_seconds: float = 0.0) -> datetime:
    return T0 + timedelta(seconds=offset_seconds)


PV = 1_000_000.0


# ── 历史情景 ──────────────────────────────────────────────────────────────────


def test_historical_2008():
    engine = StressTestEngine()
    result = engine.run_historical(
        weights={"financial": 0.3, "tech": 0.7},
        portfolio_value=PV,
        scenario_name="2008_financial_crisis",
        now=t(),
    )
    assert result.scenario.scenario_type is StressScenarioType.HISTORICAL
    # loss = 0.3*(-0.095) + 0.7*(-0.072) = -0.0285 - 0.0504 = -0.0789
    assert result.portfolio_loss_pct == pytest.approx(-0.0789, abs=1e-6)
    assert result.portfolio_loss_value == pytest.approx(-78900.0, abs=1e-2)
    assert result.is_severe is True  # >= 5%


def test_historical_2015():
    engine = StressTestEngine()
    result = engine.run_historical(
        weights={"tech": 1.0},
        portfolio_value=PV,
        scenario_name="2015_china_stock_crash",
        now=t(),
    )
    assert result.portfolio_loss_pct == pytest.approx(-0.095)


def test_historical_2020_healthcare_resilient():
    engine = StressTestEngine()
    result = engine.run_historical(
        weights={"healthcare": 1.0},
        portfolio_value=PV,
        scenario_name="2020_covid_crash",
        now=t(),
    )
    # 医疗在 2020 仅 -2.8%
    assert result.portfolio_loss_pct == pytest.approx(-0.028)
    assert result.is_severe is False


def test_historical_unknown_scenario():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="unknown historical"):
        engine.run_historical({"tech": 1.0}, PV, "1997_asian_crisis", now=t())


def test_historical_missing_sector_uses_zero():
    """权重中的 sector 不在情景 shocks 中 → shock=0。"""
    engine = StressTestEngine()
    result = engine.run_historical(
        weights={"unknown_sector": 1.0},
        portfolio_value=PV,
        scenario_name="2008_financial_crisis",
        now=t(),
    )
    assert result.portfolio_loss_pct == pytest.approx(0.0)


def test_run_all_historical():
    engine = StressTestEngine()
    results = engine.run_all_historical(weights={"financial": 0.5, "tech": 0.5}, portfolio_value=PV, now=t())
    assert len(results) == 3
    assert all(r.scenario.scenario_type is StressScenarioType.HISTORICAL for r in results)


# ── 假设情景 ──────────────────────────────────────────────────────────────────


def test_hypothetical_basic():
    engine = StressTestEngine()
    result = engine.run_hypothetical(
        weights={"600519": 0.5, "000001": 0.5},
        portfolio_value=PV,
        shocks={"600519": -0.08, "000001": -0.05},
        now=t(),
    )
    # loss = 0.5*(-0.08) + 0.5*(-0.05) = -0.065
    assert result.portfolio_loss_pct == pytest.approx(-0.065)
    assert result.scenario.scenario_type is StressScenarioType.HYPOTHETICAL


def test_hypothetical_weights_auto_normalized():
    engine = StressTestEngine()
    result = engine.run_hypothetical(
        weights={"A": 3.0, "B": 1.0},  # 未归一化 → 0.75/0.25
        portfolio_value=PV,
        shocks={"A": -0.10, "B": -0.04},
        now=t(),
    )
    # loss = 0.75*(-0.10) + 0.25*(-0.04) = -0.085
    assert result.portfolio_loss_pct == pytest.approx(-0.085)


def test_hypothetical_missing_shock():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="missing for symbols"):
        engine.run_hypothetical(
            weights={"A": 0.5, "B": 0.5},
            portfolio_value=PV,
            shocks={"A": -0.08},  # 缺 B
            now=t(),
        )


def test_hypothetical_negative_weights():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="negative weights"):
        engine.run_hypothetical(
            weights={"A": -0.5, "B": 1.5},
            portfolio_value=PV,
            shocks={"A": -0.08, "B": -0.05},
            now=t(),
        )


# ── 反向压力测试 ──────────────────────────────────────────────────────────────


def test_reverse_finds_breaking_point():
    engine = StressTestEngine()
    result = engine.run_reverse(
        weights={"A": 0.5, "B": 0.5},
        portfolio_value=PV,
        target_loss_pct=-0.10,
        base_shocks={"A": -0.02, "B": -0.01},  # 基准: loss=-0.015
        now=t(),
    )
    assert result.scenario.scenario_type is StressScenarioType.REVERSE
    # 放大后 loss 应 <= -0.10
    assert result.portfolio_loss_pct <= -0.10


def test_reverse_invalid_target_positive():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="must be negative"):
        engine.run_reverse({"A": 1.0}, PV, target_loss_pct=0.05)


def test_reverse_default_base_shocks():
    """base_shocks=None → 等权 -1%。"""
    engine = StressTestEngine()
    result = engine.run_reverse(
        weights={"A": 0.5, "B": 0.5},
        portfolio_value=PV,
        target_loss_pct=-0.05,
        now=t(),
    )
    assert result.portfolio_loss_pct <= -0.05


def test_reverse_invalid_max_scale():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="max_scale"):
        engine.run_reverse({"A": 1.0}, PV, -0.05, max_scale=0.5)


# ── 敏感性分析 ────────────────────────────────────────────────────────────────


def test_sensitivity_basic():
    engine = StressTestEngine()
    result = engine.sensitivity_analysis(
        weights={"A": 0.6, "B": 0.4},
        portfolio_value=PV,
        factor="A",
        shock_range=(-0.10, 0.10),
        steps=11,
        now=t(),
    )
    assert len(result.shock_levels) == 11
    assert len(result.pnl_impacts) == 11
    # shock=-0.10, weight=0.6 → impact = 0.6 * -0.10 * 1M = -60000
    assert result.pnl_impacts[0] == pytest.approx(-60000.0)
    # shock=0.10 → +60000
    assert result.pnl_impacts[-1] == pytest.approx(60000.0)
    # 中点 shock=0 → impact=0
    mid = len(result.pnl_impacts) // 2
    assert result.pnl_impacts[mid] == pytest.approx(0.0, abs=1e-6)


def test_sensitivity_factor_not_in_weights():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="not in weights"):
        engine.sensitivity_analysis(weights={"A": 1.0}, portfolio_value=PV, factor="B")


def test_sensitivity_invalid_range():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="increasing"):
        engine.sensitivity_analysis(
            weights={"A": 1.0},
            portfolio_value=PV,
            factor="A",
            shock_range=(0.10, -0.10),
        )


def test_sensitivity_invalid_steps():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="steps"):
        engine.sensitivity_analysis(weights={"A": 1.0}, portfolio_value=PV, factor="A", steps=1)


# ── 传染效应 ──────────────────────────────────────────────────────────────────


def test_contagion_amplifies_loss():
    engine = StressTestEngine()
    assets = ["A", "B"]
    corr = np.array([[1.0, 0.8], [0.8, 1.0]])
    # 无传染
    result_no_contagion = engine.run_with_contagion(
        weights={"A": 0.5, "B": 0.5},
        portfolio_value=PV,
        shocks={"A": -0.08, "B": -0.04},
        correlation_matrix=corr,
        assets=assets,
        contagion_factor=0.0,
        now=t(),
    )
    # 有传染
    result_contagion = engine.run_with_contagion(
        weights={"A": 0.5, "B": 0.5},
        portfolio_value=PV,
        shocks={"A": -0.08, "B": -0.04},
        correlation_matrix=corr,
        assets=assets,
        contagion_factor=0.5,
        now=t(),
    )
    # 传染应放大损失 (更负)
    assert result_contagion.portfolio_loss_pct < result_no_contagion.portfolio_loss_pct


def test_contagion_zero_factor_equals_hypothetical():
    engine = StressTestEngine()
    assets = ["A", "B"]
    corr = np.array([[1.0, 0.5], [0.5, 1.0]])
    result = engine.run_with_contagion(
        weights={"A": 0.5, "B": 0.5},
        portfolio_value=PV,
        shocks={"A": -0.08, "B": -0.04},
        correlation_matrix=corr,
        assets=assets,
        contagion_factor=0.0,
        now=t(),
    )
    # 无传染 = 普通假设情景
    assert result.portfolio_loss_pct == pytest.approx(-0.06)


def test_contagion_invalid_matrix():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="square 2D"):
        engine.run_with_contagion(
            weights={"A": 0.5, "B": 0.5},
            portfolio_value=PV,
            shocks={"A": -0.08, "B": -0.04},
            correlation_matrix=np.array([1.0, 2.0]),
            assets=["A", "B"],
        )


def test_contagion_invalid_factor():
    engine = StressTestEngine()
    corr = np.eye(2)
    with pytest.raises(InvalidStressTestInputError, match="contagion_factor"):
        engine.run_with_contagion(
            weights={"A": 0.5, "B": 0.5},
            portfolio_value=PV,
            shocks={"A": -0.08, "B": -0.04},
            correlation_matrix=corr,
            assets=["A", "B"],
            contagion_factor=1.5,
        )


def test_contagion_assets_count_mismatch():
    engine = StressTestEngine()
    corr = np.eye(3)
    with pytest.raises(InvalidStressTestInputError, match="assets count"):
        engine.run_with_contagion(
            weights={"A": 0.5, "B": 0.5},
            portfolio_value=PV,
            shocks={"A": -0.08, "B": -0.04},
            correlation_matrix=corr,
            assets=["A", "B"],  # 只有 2 个, 矩阵 3x3
        )


# ── VaR 基准 ──────────────────────────────────────────────────────────────────


def test_var_exceeded():
    engine = StressTestEngine(default_var_baseline=50000.0)  # VaR=5万
    result = engine.run_hypothetical(
        weights={"A": 1.0},
        portfolio_value=PV,
        shocks={"A": -0.08},  # 损失 8万 > 5万
        now=t(),
    )
    assert result.var_exceeded is True
    assert result.var_baseline == pytest.approx(50000.0)


def test_var_not_exceeded():
    engine = StressTestEngine(default_var_baseline=100000.0)
    result = engine.run_hypothetical(
        weights={"A": 1.0},
        portfolio_value=PV,
        shocks={"A": -0.08},  # 损失 8万 < 10万
        now=t(),
    )
    assert result.var_exceeded is False


def test_no_var_baseline():
    engine = StressTestEngine()
    result = engine.run_hypothetical(weights={"A": 1.0}, portfolio_value=PV, shocks={"A": -0.08}, now=t())
    assert result.var_exceeded is False
    assert result.var_baseline is None


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_invalid_portfolio_value_zero():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError):
        engine.run_hypothetical(weights={"A": 1.0}, portfolio_value=0, shocks={"A": -0.08}, now=t())


def test_empty_weights():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="non-empty"):
        engine.run_hypothetical(weights={}, portfolio_value=PV, shocks={"A": -0.08}, now=t())


def test_empty_shocks():
    engine = StressTestEngine()
    with pytest.raises(InvalidStressTestInputError, match="non-empty"):
        engine.run_hypothetical(weights={"A": 1.0}, portfolio_value=PV, shocks={}, now=t())


# ── to_dict ──────────────────────────────────────────────────────────────────


def test_result_to_dict():
    engine = StressTestEngine()
    result = engine.run_historical(
        weights={"tech": 1.0},
        portfolio_value=PV,
        scenario_name="2008_financial_crisis",
        now=t(),
    )
    d = result.to_dict()
    assert d["scenario_name"] == "2008_financial_crisis"
    assert d["scenario_type"] == "historical"
    assert d["is_severe"] is True


def test_historical_scenarios_constant():
    """历史情景真源不可改。"""
    assert "2008_financial_crisis" in HISTORICAL_SCENARIOS
    assert "2015_china_stock_crash" in HISTORICAL_SCENARIOS
    assert "2020_covid_crash" in HISTORICAL_SCENARIOS
    assert len(HISTORICAL_SCENARIOS) == 3
