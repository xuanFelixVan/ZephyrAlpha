# [BLUEPRINT] MOD-SIG-069 | 待统筹登记（supplement：图形技术库四件要单——RANSAC 趋势线/层次聚类变体测试）
# [MODULE] tests.signal_ashare.test_trendline_sr_variants
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.trendline_sr_detector
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成 K 线不触库不触网；默认 two_point/greedy 输出与旧版逐字段相等；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=RANSAC/层次聚类变体缺陷或旧口径破坏
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-069_sr_variants_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-069 变体单测：RANSAC 趋势线（抗离群）与 1-D 平均链接层次聚类。

覆盖：默认 two_point/greedy 输出与旧口径逐字段相等（不破坏兼容）、RANSAC
离群低点下斜率稳定性（两点线失效而 RANSAC 线存活）、average 聚类与 greedy
在良分簇数据上同簇、配置非法值 fail-closed、JSON 可序列化兼容。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.signal_ashare.trendline_sr_detector import (
    SRBar,
    TrendSRConfig,
    _cluster_levels,
    analyze_trend_sr,
)


def _bar(day: int, high: float, low: float, close: float) -> SRBar:
    return SRBar(date=f"2026-09-{day:02d}", high=high, low=low, close=close)


# 上升低点阶梯 90/91/92/93（5 个满窗分形低点，RANSAC 最少点数门槛）+ 末位离群崩低 80：
# 两点线取最后两低（93→80）斜率转负不出上升线；RANSAC 应剔除 80 存活。
_STAIR_LOWS = [
    99.0,
    97.0,
    90.0,
    95.0,
    94.0,
    93.5,
    93.0,
    91.0,
    92.8,
    92.5,
    93.0,
    93.2,
    92.0,
    93.4,
    93.6,
    94.0,
    93.8,
    93.0,
    94.2,
    94.4,
    94.1,
    94.6,
    80.0,
    94.8,
    95.0,
]
OUTLIER_BARS = [
    SRBar(date=f"2026-09-{i + 1:02d}", high=l + 6.0, low=l, close=l + 2.0) for i, l in enumerate(_STAIR_LOWS)
]


def test_default_config_matches_explicit_two_point() -> None:
    """默认输出必须与显式 two_point/greedy 逐字段相等（旧口径零漂移）。"""
    default = analyze_trend_sr(OUTLIER_BARS)
    explicit = analyze_trend_sr(
        OUTLIER_BARS,
        config=TrendSRConfig(trend_fit="two_point", cluster_method="greedy"),
    )
    assert asdict(default) == asdict(explicit)
    assert all(l.fit_method == "two_point" for l in default.trendlines)


def test_ransac_survives_outlier_low() -> None:
    """离群崩低下：两点上升线消失，RANSAC 上升线存活且斜率为正。"""
    out = analyze_trend_sr(OUTLIER_BARS, config=TrendSRConfig(trend_fit="ransac"))
    two_point_up = [l for l in out.trendlines if l.kind == "uptrend" and l.fit_method == "two_point"]
    ransac_up = [l for l in out.trendlines if l.kind == "uptrend" and l.fit_method == "ransac"]
    assert two_point_up == []  # 93→80 斜率转负，两点线不出（旧口径行为）
    assert len(ransac_up) == 1
    line = ransac_up[0]
    assert line.slope_per_bar > 0
    assert line.slope_per_bar == pytest.approx(0.2, abs=0.05)  # 真阶梯斜率 (93-90)/15


def test_ransac_insufficient_points_notes_only() -> None:
    """点数不足（<5 分形点）时 RANSAC 不出线只留 notes，不崩溃。"""
    bars = OUTLIER_BARS[:7]
    out = analyze_trend_sr(bars, config=TrendSRConfig(trend_fit="ransac"))
    assert all(l.fit_method == "two_point" for l in out.trendlines)
    assert any("RANSAC" in n for n in out.notes)


def test_agglomerative_matches_greedy_on_separated_clusters() -> None:
    """良分簇数据上 average 与 greedy 同簇（输出结构一致）。"""
    pts = [
        (0, 10.0, "d1"),
        (1, 10.1, "d2"),
        (2, 10.2, "d3"),
        (3, 20.0, "d4"),
        (4, 20.1, "d5"),
    ]
    greedy = _cluster_levels(pts, 1.5, "greedy")
    average = _cluster_levels(pts, 1.5, "average")
    assert len(greedy) == len(average) == 2
    for g, a in zip(sorted(greedy), sorted(average), strict=True):
        assert g[0] == pytest.approx(a[0])
        assert g[1] == a[1]


def test_agglomerative_small_input_falls_back_to_greedy() -> None:
    """点数 <5 时 average 回退 greedy（输出完全一致）。"""
    pts = [(0, 10.0, "d1"), (1, 10.1, "d2"), (2, 20.0, "d3")]
    assert _cluster_levels(pts, 1.5, "average") == _cluster_levels(pts, 1.5, "greedy")


def test_invalid_config_fail_closed() -> None:
    """trend_fit / cluster_method 非法值 ValueError（fail-closed）。"""
    with pytest.raises(ValueError, match="trend_fit"):
        analyze_trend_sr(OUTLIER_BARS, config=TrendSRConfig(trend_fit="bogus"))
    with pytest.raises(ValueError, match="cluster_method"):
        analyze_trend_sr(OUTLIER_BARS, config=TrendSRConfig(cluster_method="ward"))


def test_output_json_serializable_compat() -> None:
    """asdict JSON 可序列化且带 fit_method 字段（旧消费方兼容）。"""
    out = analyze_trend_sr(OUTLIER_BARS, config=TrendSRConfig(trend_fit="ransac"))
    payload = json.dumps(asdict(out), ensure_ascii=False)
    assert "fit_method" in payload
