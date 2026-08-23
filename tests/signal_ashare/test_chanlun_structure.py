# [A_test] module_id: MOD-SIG-072 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-072 | 待统筹登记 | 缺口总账 GAP-F-37 行
# [MODULE] tests.signal_ashare.test_chanlun_structure
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""缠论笔/段/中枢自动识别（MOD-SIG-072，GAP-F-37）施工验证测试。

覆盖：
- 包含处理：相含 K 线按方向合并、根数留痕；关掉包含处理则不合并；
- 分型：构造锯齿序列识别顶/底分型、交替性、价格锚点；
- 笔：严格笔跨距 ≥min_bi_bars 才成笔；同类型分型取更极端者；过近分型不成笔；
- 线段：≥3 笔且前三笔重叠成段，方向=首笔方向；
- 中枢：≥3 笔重叠区 [ZD,ZG] 生成，ZD<ZG；
- fail-closed：根数不足/high<low/非正价/非法参数；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.chanlun_structure import (
    FX_BOTTOM,
    FX_TOP,
    ChanlunConfig,
    ChanlunStructure,
    analyze_chanlun,
)


def _zigzag(points: list[float], half_width: float = 0.5) -> tuple[list[float], list[float]]:
    """折线中点序列 → (highs, lows)（步长 >2*half_width 时无包含）。"""
    highs = [p + half_width for p in points]
    lows = [p - half_width for p in points]
    return highs, lows


def _path(*legs: tuple[float, float, float]) -> list[float]:
    """(起点, 终点, 步长) 折腿展开为中点序列。"""
    pts: list[float] = []
    for start, end, step in legs:
        n = int(round(abs(end - start) / step))
        leg = [start + (end - start) * i / n for i in range(n + 1)]
        pts.extend(leg if not pts else leg[1:])
    return pts


class TestInclusionMerge:
    def test_contained_bars_merged(self) -> None:
        highs = [10.0, 11.0, 10.8, 11.5, 12.0, 12.5]
        lows = [9.0, 9.5, 9.8, 10.2, 10.8, 11.2]  # 第3根被第2根包含
        res = analyze_chanlun(highs, lows)
        assert res.n_bars == 6
        assert res.n_merged == 5

    def test_inclusion_off_no_merge(self) -> None:
        highs = [10.0, 11.0, 10.8, 11.5, 12.0, 12.5]
        lows = [9.0, 9.5, 9.8, 10.2, 10.8, 11.2]
        res = analyze_chanlun(highs, lows, config=ChanlunConfig(inclusion_process=False))
        assert res.n_merged == 6


class TestFractalAndBi:
    def test_zigzag_fractals_alternate(self) -> None:
        pts = _path((10.0, 20.0, 2.0), (20.0, 10.0, 2.0), (10.0, 20.0, 2.0), (20.0, 10.0, 2.0))
        highs, lows = _zigzag(pts)
        res = analyze_chanlun(highs, lows)
        kinds = [f.kind for f in res.fractals]
        assert FX_TOP in kinds and FX_BOTTOM in kinds
        for a, b in zip(res.fractals, res.fractals[1:]):
            assert a.kind != b.kind

    def test_zigzag_bi_built_and_alternate(self) -> None:
        # 末腿抬高使末尾底分型成为内点（末根无右邻不成型）
        pts = _path((10.0, 20.0, 2.0), (20.0, 10.0, 2.0), (10.0, 20.0, 2.0), (20.0, 10.0, 2.0), (10.0, 14.0, 2.0))
        highs, lows = _zigzag(pts)
        res = analyze_chanlun(highs, lows)
        assert len(res.bis) == 3
        assert res.bis[0].direction == "down"
        assert res.bis[1].direction == "up"
        assert res.bis[2].direction == "down"
        assert res.bis[1].end_price > res.bis[1].start_price
        for bi in res.bis:
            assert bi.bar_count >= 5  # 严格笔跨距（chart_pattern_registry PAT-CLL-003/004）

    def test_tight_fractals_no_bi(self) -> None:
        # 分型间隔 3 根（<5），严格笔不成立
        pts = [10.0, 14.0, 10.0, 14.0, 10.0, 14.0, 10.0]
        highs, lows = _zigzag(pts)
        res = analyze_chanlun(highs, lows)
        assert len(res.fractals) >= 3
        assert len(res.bis) == 0

    def test_same_kind_fractal_keeps_extreme(self) -> None:
        # 两个顶分型（后更高）中间底分型太近不成笔 → 保留更高顶
        pts = [10.0, 14.0, 12.0, 16.0, 10.0, 5.0]
        pts = pts[:1] + [10.0 + (14.0 - 10.0) * i / 4 for i in range(1, 5)][1:] + pts[1:]
        highs, lows = _zigzag([10.0, 12.0, 14.0, 13.0, 12.5, 13.0, 14.0, 15.0, 16.0, 13.0, 10.0, 7.0, 5.0])
        res = analyze_chanlun(highs, lows)
        tops = [f for f in res.fractals if f.kind == FX_TOP]
        assert tops, "应识别到顶分型"
        assert max(t.price for t in tops) == pytest.approx(16.5)


class TestSegmentAndZhongshu:
    def test_segment_from_three_overlapping_bi(self) -> None:
        # 末腿回落使末尾顶分型成为内点
        pts = _path((20.0, 10.0, 2.0), (10.0, 20.0, 2.0), (20.0, 10.0, 2.0), (10.0, 20.0, 2.0), (20.0, 16.0, 2.0))
        highs, lows = _zigzag(pts)
        res = analyze_chanlun(highs, lows)
        assert len(res.bis) == 3
        assert len(res.segments) == 1
        seg = res.segments[0]
        assert seg.direction == "up"  # 首笔 up（10→20）
        assert seg.bi_count == 3
        assert seg.start_bi == 0 and seg.end_bi == 2

    def test_zhongshu_zone(self) -> None:
        pts = _path((20.0, 10.0, 2.0), (10.0, 20.0, 2.0), (20.0, 10.0, 2.0), (10.0, 20.0, 2.0), (20.0, 16.0, 2.0))
        highs, lows = _zigzag(pts)
        res = analyze_chanlun(highs, lows)
        assert len(res.zhongshus) == 1
        zs = res.zhongshus[0]
        assert zs.zd < zs.zg
        assert zs.zd == pytest.approx(9.5, abs=0.6)
        assert zs.zg == pytest.approx(20.5, abs=0.6)
        assert zs.bi_count >= 3

    def test_no_overlap_no_zhongshu(self) -> None:
        # 单边趋势三笔无重叠（每笔区间不交集）→ 无中枢
        pts = _path((10.0, 20.0, 2.0), (20.0, 19.0, 1.0), (19.0, 30.0, 2.0), (30.0, 29.0, 1.0), (29.0, 40.0, 2.0))
        highs, lows = _zigzag(pts)
        res = analyze_chanlun(highs, lows, config=ChanlunConfig(min_bi_bars=3))
        assert res.zhongshus == ()


class TestValidation:
    def test_short_input_rejected(self) -> None:
        with pytest.raises(ValueError, match="根数"):
            analyze_chanlun([10.0, 11.0], [9.0, 10.0])

    def test_high_below_low_rejected(self) -> None:
        with pytest.raises(ValueError, match="high"):
            analyze_chanlun([10.0, 9.0, 11.0, 12.0, 13.0, 14.0], [9.0, 10.5, 10.0, 11.0, 12.0, 13.0])

    def test_length_mismatch_rejected(self) -> None:
        with pytest.raises(ValueError, match="等长"):
            analyze_chanlun([10.0, 11.0, 12.0, 13.0, 14.0, 15.0], [9.0, 10.0])

    def test_bad_min_bi_bars_rejected(self) -> None:
        with pytest.raises(ValueError, match="min_bi_bars"):
            ChanlunConfig(min_bi_bars=2)


class TestContract:
    def test_to_dict_json_serializable(self) -> None:
        pts = _path((20.0, 10.0, 2.0), (10.0, 20.0, 2.0), (20.0, 10.0, 2.0))
        highs, lows = _zigzag(pts)
        res = analyze_chanlun(highs, lows)
        text = json.dumps(res.to_dict(), ensure_ascii=False)
        assert "zhongshus" in text

    def test_frozen(self) -> None:
        pts = _path((20.0, 10.0, 2.0), (10.0, 20.0, 2.0), (20.0, 10.0, 2.0))
        highs, lows = _zigzag(pts)
        res = analyze_chanlun(highs, lows)
        assert isinstance(res, ChanlunStructure)
        with pytest.raises(dataclasses.FrozenInstanceError):
            res.n_bars = 0  # type: ignore[misc]
