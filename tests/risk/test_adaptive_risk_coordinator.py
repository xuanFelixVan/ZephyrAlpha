# [BLUEPRINT] MOD-RK-30 | docs/03_modules/_domain_risk/adaptive_risk_coordinator/blueprint.md | §test
# [A_test] module_id: MOD-RK-30 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AdaptiveRiskCoordinator 单元测试 (MOD-RK-30, C-004 三层联动薄装配 MVP)。

覆盖: B-001~B-006 硬边界注册表(与 config/risk_params.yaml 锚定) / 盘前计划
(sit_out/限额缩放) / regime 自适应乘数(未知状态保守) / 盘中熔断分级
(REDUCE/HALT_NEW/KILL_SWITCH 取最严) / Fail-Closed 配置校验 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped]

from zephyr.risk.core.adaptive_risk_coordinator import (
    AdaptiveRiskDecision,
    CircuitBreakerLevel,
    CoordinatorConfig,
    InvalidCoordinatorConfigError,
    PremarketRiskPlan,
    decide_intraday,
    get_hard_boundaries,
    plan_premarket,
)
from zephyr.risk.core.adaptive_risk_forecast import ForwardVarForecast
from zephyr.risk.core.adaptive_risk_monitor import RiskWatchSnapshot


def _forecast(
    *,
    var_pct: float = 0.01,
    conformal_var_pct: float | None = None,
    limit_scale: float = 1.0,
    limit_breached: bool = False,
    sit_out: bool = False,
) -> ForwardVarForecast:
    cvar = conformal_var_pct if conformal_var_pct is not None else var_pct
    return ForwardVarForecast(
        var_pct=var_pct,
        cvar_pct=cvar,
        conformal_margin_pct=max(0.0, cvar - var_pct),
        conformal_var_pct=cvar,
        limit_scale=limit_scale,
        limit_breached=limit_breached,
        sit_out=sit_out,
        degraded=False,
        n_samples=120,
        n_calibration=60,
    )


def _snapshot(*, severity: str = "normal", liquidity_level: str = "normal", corr: str = "LOW") -> RiskWatchSnapshot:
    return RiskWatchSnapshot(
        n_symbols=5,
        n_illiquid=0,
        illiquid_ratio=0.0,
        liquidity_level=liquidity_level,
        avg_pairwise_correlation=0.2,
        correlation_regime=corr,
        diversification_effective=True,
        overall_severity=severity,
        alerts=(),
    )


# ── B-001~B-006 硬边界注册表 ──────────────────────────────────────────────────


def test_hard_boundaries_six_entries() -> None:
    hb = get_hard_boundaries()
    assert tuple(hb.keys()) == ("B-001", "B-002", "B-003", "B-004", "B-005", "B-006")


def test_hard_boundaries_anchor_risk_params_yaml() -> None:
    params = yaml.safe_load(Path("config/risk_params.yaml").read_text(encoding="utf-8"))
    hb = get_hard_boundaries()
    assert hb["B-001"].value == pytest.approx(params["max_single_position_nav_ratio"])  # 0.05
    assert hb["B-002"].value == pytest.approx(params["max_sector_concentration_nav_ratio"])  # 0.30
    assert hb["B-003"].value == pytest.approx(params["max_gross_leverage"])  # 1.0
    assert hb["B-004"].value == pytest.approx(params["max_strategy_correlation_threshold"])  # 0.85
    assert hb["B-005"].value == pytest.approx(params["max_factor_overlap_threshold"])  # 0.60
    assert hb["B-006"].value == pytest.approx(params["max_universe_overlap_threshold"])  # 0.70


def test_hard_boundaries_immutable_mapping() -> None:
    hb = get_hard_boundaries()
    with pytest.raises(TypeError):
        hb["B-001"] = None  # type: ignore[index]


# ── 盘前计划 ──────────────────────────────────────────────────────────────────


def test_premarket_calm_plan() -> None:
    plan = plan_premarket(_forecast(), regime_state="NORMAL")
    assert isinstance(plan, PremarketRiskPlan)
    assert plan.sit_out is False
    assert plan.limit_scale == pytest.approx(1.0)


def test_premarket_breach_scales_limit() -> None:
    plan = plan_premarket(_forecast(limit_scale=0.5, limit_breached=True), regime_state="NORMAL")
    assert plan.limit_scale == pytest.approx(0.5)


def test_premarket_sit_out_passthrough() -> None:
    plan = plan_premarket(_forecast(sit_out=True), regime_state="NORMAL")
    assert plan.sit_out is True
    assert any("sit_out" in r for r in plan.reasons)


def test_premarket_regime_tightens() -> None:
    plan = plan_premarket(_forecast(limit_scale=1.0), regime_state="TURBULENT")
    assert plan.limit_scale == pytest.approx(0.7)
    assert plan.regime_multiplier == pytest.approx(0.7)


def test_premarket_unknown_regime_conservative() -> None:
    plan = plan_premarket(_forecast(limit_scale=1.0), regime_state="WEIRD_STATE")
    assert plan.limit_scale == pytest.approx(0.7)
    assert any("未知" in r or "unknown" in r for r in plan.reasons)


def test_premarket_scale_never_exceeds_one() -> None:
    plan = plan_premarket(_forecast(limit_scale=1.0), regime_state="CALM")
    assert 0.0 < plan.limit_scale <= 1.0


# ── 盘中熔断分级 ──────────────────────────────────────────────────────────────


def test_intraday_all_calm_none() -> None:
    d = decide_intraday(_snapshot())
    assert isinstance(d, AdaptiveRiskDecision)
    assert d.level is CircuitBreakerLevel.NONE
    assert d.allow_new_positions is True
    assert d.kill_switch_advised is False
    assert d.position_cap_scale == pytest.approx(1.0)


def test_intraday_orange_reduce() -> None:
    d = decide_intraday(_snapshot(severity="orange", corr="HIGH"))
    assert d.level is CircuitBreakerLevel.REDUCE_POSITION
    assert d.position_cap_scale == pytest.approx(0.5)
    assert d.allow_new_positions is True


def test_intraday_red_halt_new() -> None:
    d = decide_intraday(_snapshot(severity="red", liquidity_level="red"))
    assert d.level is CircuitBreakerLevel.HALT_NEW
    assert d.allow_new_positions is False


def test_intraday_forecast_breach_reduce() -> None:
    d = decide_intraday(_snapshot(), forecast=_forecast(limit_breached=True, limit_scale=0.4))
    assert d.level is CircuitBreakerLevel.REDUCE_POSITION
    assert d.position_cap_scale == pytest.approx(0.4)


def test_intraday_sit_out_halt_new() -> None:
    d = decide_intraday(_snapshot(), forecast=_forecast(sit_out=True))
    assert d.level is CircuitBreakerLevel.HALT_NEW


def test_intraday_black_swan_kill_switch() -> None:
    d = decide_intraday(_snapshot(severity="red", liquidity_level="red"), black_swan_escalated=True)
    assert d.level is CircuitBreakerLevel.KILL_SWITCH
    assert d.kill_switch_advised is True
    assert d.allow_new_positions is False
    assert d.position_cap_scale == 0.0


def test_intraday_worst_of_monitor_and_forecast() -> None:
    d = decide_intraday(_snapshot(severity="orange", corr="HIGH"), forecast=_forecast(sit_out=True))
    assert d.level is CircuitBreakerLevel.HALT_NEW


# ── Fail-Closed 校验 ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "kwargs",
    [
        {"reduce_cap_scale": 0.0},
        {"reduce_cap_scale": 1.5},
        {"unknown_regime_multiplier": 0.0},
        {"unknown_regime_multiplier": 1.2},
        {"regime_multipliers": {"X": 0.0}},
        {"regime_multipliers": {"X": 1.5}},
    ],
)
def test_invalid_config_fail_closed(kwargs: dict) -> None:
    with pytest.raises(InvalidCoordinatorConfigError):
        CoordinatorConfig(**kwargs)


# ── 不可变 ────────────────────────────────────────────────────────────────────


def test_result_frozen() -> None:
    d = decide_intraday(_snapshot())
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.level = CircuitBreakerLevel.KILL_SWITCH  # type: ignore[misc]
