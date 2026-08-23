# [BLUEPRINT] MOD-SIG-069 | 待统筹登记（supplement：GAP-F-33 趋势线/压力支撑识别；主号=指数共振评分）
# [MODULE] tests.signal_ashare.test_trendline_sr_detector
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.trendline_sr_detector
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成 K 线不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=趋势线/压力支撑识别逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-069_sr_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-069 supplement 趋势线/压力支撑识别 单元测试（GAP-F-33，合成 K 线）。

覆盖：分形极值识别（窗口 k）、价位聚类（容差 %）、支撑/压力选取（现价下方最近=
支撑/上方最近=压力，触点数为强度）、趋势线（最近两显著低点=上升线/高点=下降线，
当前值与距离 %）、数据不足降级、非法输入 fail-closed、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.signal_ashare.trendline_sr_detector import (
    SRBar,
    TrendSRConfig,
    analyze_trend_sr,
)


def _cfg(**kw) -> TrendSRConfig:
    return TrendSRConfig(**kw)


def _bar(day: int, high: float, low: float, close: float) -> SRBar:
    return SRBar(date=f"2026-08-{day:02d}", high=high, low=low, close=close)


# 合成序列：两次探底 95/95.2（day3/day9，均满窗）+ 两次摸高 105/105.2（day5/day11）
BARS = [
    _bar(1, 100.5, 98.0, 99.0),
    _bar(2, 99.0, 96.5, 97.0),
    _bar(3, 98.0, 95.0, 96.0),   # 分形低 95（idx2 满窗）
    _bar(4, 100.0, 99.0, 99.5),
    _bar(5, 105.0, 99.5, 104.0), # 分形高 105
    _bar(6, 104.0, 100.0, 101.0),
    _bar(7, 101.5, 98.0, 98.5),
    _bar(8, 99.0, 96.0, 97.0),
    _bar(9, 97.5, 95.2, 96.0),   # 分形低 95.2（与 95 容差内聚类）
    _bar(10, 100.0, 96.5, 99.5),
    _bar(11, 105.2, 99.0, 104.5),# 分形高 105.2（与 105 容差内聚类）
    _bar(12, 104.0, 100.0, 101.0),
    _bar(13, 102.0, 99.0, 100.5),# 最新收 100.5
]


# ------------------------------------------------------------------
# 支撑/压力位
# ------------------------------------------------------------------


def test_levels_clustered_with_touches() -> None:
    out = analyze_trend_sr(BARS, config=_cfg())
    assert out.degraded is False
    # 95/95.2 聚类 1 个支撑位（2 触点）；105/105.2 聚类 1 个压力位（2 触点）
    assert out.support is not None
    assert out.resistance is not None
    assert out.support.touches == 2
    assert out.resistance.touches == 2
    assert out.support.price == pytest.approx(95.1, abs=0.2)
    assert out.resistance.price == pytest.approx(105.1, abs=0.2)


def test_support_below_close_resistance_above() -> None:
    out = analyze_trend_sr(BARS, config=_cfg())
    assert out.support.price < BARS[-1].close
    assert out.resistance.price > BARS[-1].close
    assert out.support.kind == "support"
    assert out.resistance.kind == "resistance"


def test_level_dates_attached() -> None:
    out = analyze_trend_sr(BARS, config=_cfg())
    assert out.support.first_date == "2026-08-03"
    assert out.resistance.first_date == "2026-08-05"


def test_no_level_one_side() -> None:
    # 单边上涨：无上方分形高 → 压力 None 降级标注
    up = [_bar(d, 100.0 + d, 99.0 + d, 99.5 + d) for d in range(1, 14)]
    out = analyze_trend_sr(up, config=_cfg())
    assert out.resistance is None
    assert any("压力" in n for n in out.notes)


# ------------------------------------------------------------------
# 趋势线
# ------------------------------------------------------------------


def test_uptrend_line_from_recent_lows() -> None:
    out = analyze_trend_sr(BARS, config=_cfg())
    up_lines = [t for t in out.trendlines if t.kind == "uptrend"]
    assert up_lines
    line = up_lines[0]
    assert line.slope_per_bar > 0
    assert line.anchor_dates[0] < line.anchor_dates[1]
    assert line.current_value > 0
    assert isinstance(line.distance_pct, float)


def test_downtrend_line_from_recent_highs() -> None:
    # 高点下移序列（两个有效分形高 112 → 106.5）
    down = [
        _bar(1, 108.0, 104.0, 105.0),
        _bar(2, 111.0, 106.0, 110.0),
        _bar(3, 112.0, 108.0, 109.0),  # 分形高 112
        _bar(4, 106.0, 102.0, 103.0),
        _bar(5, 104.0, 100.0, 101.0),
        _bar(6, 106.5, 101.0, 106.0),  # 分形高 106.5（更低）
        _bar(7, 103.0, 99.0, 100.0),
        _bar(8, 101.0, 97.0, 98.0),
        _bar(9, 99.5, 95.5, 96.0),
    ]
    out = analyze_trend_sr(down, config=_cfg())
    dn_lines = [t for t in out.trendlines if t.kind == "downtrend"]
    assert dn_lines
    assert dn_lines[0].slope_per_bar < 0


def test_insufficient_bars_degraded() -> None:
    out = analyze_trend_sr(BARS[:3], config=_cfg(fractal_window=2))
    assert out.degraded is True
    assert any("不足" in n for n in out.notes)


def test_no_extrema_degraded() -> None:
    flat = [_bar(d, 100.0, 99.0, 99.5) for d in range(1, 10)]
    out = analyze_trend_sr(flat, config=_cfg())
    # 全平无分形 → 至少 notes 留痕（levels 空）
    assert out.levels == []
    assert any("分形" in n or "极值" in n for n in out.notes)


def test_invalid_bars_fail_closed() -> None:
    with pytest.raises(ValueError, match="bars 元素非法"):
        analyze_trend_sr([{"x": 1}], config=_cfg())  # type: ignore[list-item]
    with pytest.raises(ValueError, match="价格非法"):
        analyze_trend_sr([_bar(d, -1.0, -2.0, -1.5) for d in range(1, 10)], config=_cfg())


def test_json_serializable() -> None:
    out = analyze_trend_sr(BARS, config=_cfg())
    json.dumps(asdict(out), ensure_ascii=False)
