# [BLUEPRINT] MOD-RK-29 | docs/03_modules/_domain_risk/adaptive_risk_monitor/blueprint.md | §test
# [A_test] module_id: MOD-RK-29 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AdaptiveRiskMonitor 单元测试 (MOD-RK-29, MVP)。

覆盖: 流动性占比分级(黄/红) / 相关性 regime 透传(HIGH→橙告警) / 综合严重度取最严 /
无相关性输入 NA / 告警数据级别语义对齐 AlertLevel / Fail-Closed 配置与输入校验 /
frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from zephyr.risk.core.adaptive_risk_monitor import (
    InvalidLiquidityWatchInputError,
    InvalidRiskWatchConfigError,
    LiquidityWatchInput,
    RiskWatchConfig,
    RiskWatchSnapshot,
    assess_risk_watch,
)
from zephyr.risk.core.alert_generator import AlertLevel


def _liq(symbol: str, *, illiquid: bool = False, amihud: float = 1e-9, shrink: float = 1.0) -> LiquidityWatchInput:
    return LiquidityWatchInput(
        symbol=symbol,
        amihud_illiq=amihud,
        volume_shrinkage_ratio=shrink,
        is_illiquid=illiquid,
    )


def _corr_returns(n: int = 4, corr: float = 0.9, samples: int = 120) -> dict[str, list[float]]:
    rng = np.random.default_rng(3)
    base = rng.normal(0.0, 0.01, samples)
    out: dict[str, list[float]] = {}
    for i in range(n):
        noise = rng.normal(0.0, 0.01, samples)
        out[f"S{i:02d}"] = (corr * base + np.sqrt(max(1e-12, 1 - corr**2)) * noise).tolist()
    return out


# ── 流动性分级 ────────────────────────────────────────────────────────────────


def test_all_liquid_normal() -> None:
    snap = assess_risk_watch([_liq(f"S{i}") for i in range(5)])
    assert isinstance(snap, RiskWatchSnapshot)
    assert snap.liquidity_level == "normal"
    assert snap.illiquid_ratio == 0.0
    assert snap.n_illiquid == 0
    assert snap.overall_severity == "normal"
    assert snap.alerts == ()


def test_yellow_on_partial_illiquid() -> None:
    inputs = [_liq("A", illiquid=True)] + [_liq(f"S{i}") for i in range(4)]  # 20%
    snap = assess_risk_watch(inputs)
    assert snap.illiquid_ratio == pytest.approx(0.2)
    assert snap.liquidity_level == "yellow"
    assert snap.overall_severity == "yellow"
    assert len(snap.alerts) == 1
    assert snap.alerts[0].level == AlertLevel.YELLOW.value
    assert snap.alerts[0].source == "liquidity_watch"


def test_red_on_majority_illiquid() -> None:
    inputs = [_liq(f"X{i}", illiquid=True) for i in range(3)] + [_liq("S0")]  # 75%
    snap = assess_risk_watch(inputs)
    assert snap.liquidity_level == "red"
    assert snap.overall_severity == "red"
    assert snap.alerts[0].level == AlertLevel.RED.value


# ── 相关性体制 ────────────────────────────────────────────────────────────────


def test_high_correlation_regime_orange_alert() -> None:
    snap = assess_risk_watch([_liq("A")], correlation_returns=_corr_returns(corr=0.95))
    assert snap.correlation_regime == "HIGH"
    assert snap.diversification_effective is False
    assert snap.avg_pairwise_correlation is not None and snap.avg_pairwise_correlation > 0.6
    assert any(a.source == "correlation_regime" and a.level == AlertLevel.ORANGE.value for a in snap.alerts)
    assert snap.overall_severity == "orange"


def test_low_correlation_regime_no_alert() -> None:
    snap = assess_risk_watch([_liq("A")], correlation_returns=_corr_returns(corr=0.05))
    assert snap.correlation_regime in ("LOW", "NORMAL")
    assert snap.diversification_effective is True
    assert snap.alerts == ()


def test_no_correlation_input_marks_na() -> None:
    snap = assess_risk_watch([_liq("A")])
    assert snap.correlation_regime == "NA"
    assert snap.avg_pairwise_correlation is None


# ── 取最严 ────────────────────────────────────────────────────────────────────


def test_overall_severity_takes_worst() -> None:
    inputs = [_liq(f"X{i}", illiquid=True) for i in range(3)] + [_liq("S0")]  # red 流动性
    snap = assess_risk_watch(inputs, correlation_returns=_corr_returns(corr=0.95))  # orange 相关
    assert snap.overall_severity == "red"
    assert len(snap.alerts) == 2


# ── Fail-Closed 校验 ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "kwargs",
    [
        {"illiquid_ratio_yellow": -0.1},
        {"illiquid_ratio_yellow": 1.5},
        {"illiquid_ratio_red": 0.0},
        {"illiquid_ratio_yellow": 0.6, "illiquid_ratio_red": 0.5},  # 乱序
    ],
)
def test_invalid_config_fail_closed(kwargs: dict) -> None:
    with pytest.raises(InvalidRiskWatchConfigError):
        RiskWatchConfig(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"symbol": "", "amihud_illiq": 1e-9, "volume_shrinkage_ratio": 1.0, "is_illiquid": False},
        {"symbol": "A", "amihud_illiq": -1.0, "volume_shrinkage_ratio": 1.0, "is_illiquid": False},
        {"symbol": "A", "amihud_illiq": 1e-9, "volume_shrinkage_ratio": -0.5, "is_illiquid": False},
    ],
)
def test_invalid_liquidity_input_fail_closed(kwargs: dict) -> None:
    with pytest.raises(InvalidLiquidityWatchInputError):
        LiquidityWatchInput(**kwargs)


def test_empty_liquidity_inputs_raises() -> None:
    with pytest.raises(InvalidLiquidityWatchInputError):
        assess_risk_watch([])


# ── 不可变 ────────────────────────────────────────────────────────────────────


def test_result_frozen() -> None:
    snap = assess_risk_watch([_liq("A")])
    with pytest.raises(dataclasses.FrozenInstanceError):
        snap.overall_severity = "red"  # type: ignore[misc]
