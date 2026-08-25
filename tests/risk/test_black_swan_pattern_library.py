# [BLUEPRINT] MOD-RK-31 | docs/03_modules/_domain_risk/black_swan_pattern_library/blueprint.md | §test
# [A_test] module_id: MOD-RK-31 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""BlackSwanPatternLibrary 单元测试 (MOD-RK-31, C-038 MVP)。

覆盖: 7 模板齐备且枚举复用 MOD-POS-008 / 平静市场零命中 / 流动性枯竭单模式命中
提前降仓 / 多模式命中(≥2)升级 C-004(BS-007 语义) / 显式 BS-007 / 评分单调性 /
匹配记录留痕 / Fail-Closed 输入与配置校验 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.position.core.drawdown_controller import BlackSwanMode
from zephyr.risk.core.black_swan_pattern_library import (
    BlackSwanScreenResult,
    InvalidBlackSwanConfigError,
    InvalidMarketFeaturesError,
    MarketFeatures,
    get_pattern_templates,
    screen_black_swan,
)


def _calm() -> MarketFeatures:
    return MarketFeatures(
        volatility_ratio=1.0,
        drawdown_pct=0.02,
        avg_correlation=0.2,
        liquidity_shrink=0.1,
        gap_pct=0.003,
        limit_down_ratio=0.0,
        cross_market_drop=0.005,
    )


def _liquidity_crisis() -> MarketFeatures:
    return MarketFeatures(
        volatility_ratio=1.8,
        drawdown_pct=0.06,
        avg_correlation=0.4,
        liquidity_shrink=0.85,
        gap_pct=0.01,
        limit_down_ratio=0.35,
        cross_market_drop=0.01,
    )


def _multi_crisis() -> MarketFeatures:
    return MarketFeatures(
        volatility_ratio=4.5,
        drawdown_pct=0.18,
        avg_correlation=0.9,
        liquidity_shrink=0.8,
        gap_pct=0.04,
        limit_down_ratio=0.3,
        cross_market_drop=0.06,
    )


# ── 模板库 ────────────────────────────────────────────────────────────────────


def test_seven_templates_cover_all_modes() -> None:
    templates = get_pattern_templates()
    assert len(templates) == 7
    assert set(templates.keys()) == set(BlackSwanMode)


def test_templates_immutable() -> None:
    templates = get_pattern_templates()
    with pytest.raises(TypeError):
        templates[BlackSwanMode.BS001_LIQUIDITY] = None  # type: ignore[index]


# ── 匹配 ──────────────────────────────────────────────────────────────────────


def test_calm_market_no_match() -> None:
    res = screen_black_swan(_calm())
    assert isinstance(res, BlackSwanScreenResult)
    assert res.matched_modes == ()
    assert res.escalate_to_c004 is False
    assert res.suggested_position_scale == pytest.approx(1.0)
    assert len(res.matching_log) == 7  # 全模式留痕


def test_liquidity_crisis_matches_bs001() -> None:
    res = screen_black_swan(_liquidity_crisis())
    assert BlackSwanMode.BS001_LIQUIDITY in res.matched_modes
    assert res.suggested_position_scale < 1.0
    assert res.escalate_to_c004 is False  # 单模式不升级
    entry = next(m for m in res.matching_log if m.mode is BlackSwanMode.BS001_LIQUIDITY)
    assert entry.matched is True
    assert entry.score >= entry.threshold


def test_multi_mode_escalates_to_c004() -> None:
    res = screen_black_swan(_multi_crisis())
    assert len(res.matched_modes) >= 2
    assert res.escalate_to_c004 is True
    assert res.suggested_position_scale <= 0.5


def test_explicit_bs007_escalates() -> None:
    features = MarketFeatures(
        volatility_ratio=6.0,
        drawdown_pct=0.30,
        avg_correlation=0.95,
        liquidity_shrink=0.95,
        gap_pct=0.08,
        limit_down_ratio=0.5,
        cross_market_drop=0.10,
    )
    res = screen_black_swan(features)
    assert BlackSwanMode.BS007_SYSTEMIC in res.matched_modes
    assert res.escalate_to_c004 is True
    assert res.suggested_position_scale == 0.0


def test_score_monotonic_in_features() -> None:
    mild = dataclasses.replace(_calm(), liquidity_shrink=0.4)
    severe = dataclasses.replace(_calm(), liquidity_shrink=0.9)
    s_mild = next(m.score for m in screen_black_swan(mild).matching_log if m.mode is BlackSwanMode.BS001_LIQUIDITY)
    s_severe = next(m.score for m in screen_black_swan(severe).matching_log if m.mode is BlackSwanMode.BS001_LIQUIDITY)
    assert s_severe > s_mild


# ── Fail-Closed 校验 ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "field,bad",
    [
        ("volatility_ratio", -0.1),
        ("drawdown_pct", float("nan")),
        ("avg_correlation", float("inf")),
        ("liquidity_shrink", -1.0),
        ("gap_pct", -0.5),
        ("limit_down_ratio", -0.2),
        ("cross_market_drop", -0.3),
    ],
)
def test_invalid_features_fail_closed(field: str, bad: float) -> None:
    with pytest.raises(InvalidMarketFeaturesError):
        dataclasses.replace(_calm(), **{field: bad})


def test_invalid_config_threshold() -> None:
    from zephyr.risk.core.black_swan_pattern_library import BlackSwanConfig

    with pytest.raises(InvalidBlackSwanConfigError):
        BlackSwanConfig(match_threshold=0.0)
    with pytest.raises(InvalidBlackSwanConfigError):
        BlackSwanConfig(match_threshold=1.5)


def test_threshold_override_changes_matching() -> None:
    from zephyr.risk.core.black_swan_pattern_library import BlackSwanConfig

    strict = screen_black_swan(_liquidity_crisis(), config=BlackSwanConfig(match_threshold=0.999))
    assert strict.matched_modes == ()


# ── 不可变 ────────────────────────────────────────────────────────────────────


def test_result_frozen() -> None:
    res = screen_black_swan(_calm())
    with pytest.raises(dataclasses.FrozenInstanceError):
        res.escalate_to_c004 = True  # type: ignore[misc]
