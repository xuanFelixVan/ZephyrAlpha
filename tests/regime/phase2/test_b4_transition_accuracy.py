# -*- coding: utf-8 -*-
"""B4 转换触发准确性验证器单元测试（12_regime_phase2_validation §2.2）."""

from __future__ import annotations

import unittest
from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd

from zephyr.regime.validation.phase2.b4_transition_accuracy import (
    MATCH_WINDOW_DAYS,
    PASS_RATIO,
    B4EventMatch,
    B4Report,
    B4TransitionAccuracy,
    B4Verdict,
    HistoricalEvent,
)


def _make_transition(tid: str, stage: str, total: float = 100.0, triggered: bool = True):
    """构造 mock TransitionTriggered."""
    trig = MagicMock()
    trig.transition_type = tid
    trig.stage = stage
    trig.total_score = total
    trig.triggered = triggered
    trig.confirmed = stage in ("confirm", "strong_confirm")
    trig.timestamp = datetime.now()
    return trig


class TestB4TransitionAccuracy(unittest.TestCase):
    """B4 验证器核心逻辑测试。"""

    def setUp(self):
        self.b4 = B4TransitionAccuracy()
        # 构造 2015-01-05 起的 100 个交易日（足够间距避免 ±5 窗口交叉匹配）
        self.dates = list(pd.bdate_range("2015-01-05", periods=100))
        # 事件日选第 15 个交易日（中间）
        self.event_date = self.dates[14]

    def _make_events(self, transition_type: str = "S1", in_range: bool = True) -> list[HistoricalEvent]:
        return [
            HistoricalEvent(
                id="EVT-TEST",
                date=self.event_date,
                transition_type=transition_type,
                expected_stage=["trigger", "confirm"],
                desc="test",
                in_data_range=in_range,
            )
        ]

    def test_exact_day_match(self):
        """触发日 == 事件日 → 命中（delta=0）。"""
        daily = {self.event_date: [_make_transition("S1", "trigger")]}
        report = self.b4.validate(daily, events=self._make_events(), trading_dates=self.dates)
        self.assertEqual(report.verdict, B4Verdict.PASS)
        self.assertEqual(report.hit_count, 1)
        self.assertEqual(report.total_evaluated, 1)
        m = report.matches[0]
        self.assertTrue(m.hit)
        self.assertEqual(m.delta_days, 0)
        self.assertEqual(m.matched_stage, "trigger")

    def test_within_5_days_match(self):
        """触发日 ±5 交易日内 → 命中。"""
        # 事件日 +3 交易日触发
        trig_date = self.dates[17]
        daily = {trig_date: [_make_transition("S1", "confirm")]}
        report = self.b4.validate(daily, events=self._make_events(), trading_dates=self.dates)
        self.assertEqual(report.hit_count, 1)
        m = report.matches[0]
        self.assertEqual(m.delta_days, 3)

    def test_outside_5_days_no_match(self):
        """触发日 >5 交易日外 → 未命中。"""
        trig_date = self.dates[20]  # +6 交易日
        daily = {trig_date: [_make_transition("S1", "trigger")]}
        report = self.b4.validate(daily, events=self._make_events(), trading_dates=self.dates)
        self.assertEqual(report.hit_count, 0)
        self.assertEqual(report.verdict, B4Verdict.FAIL)
        m = report.matches[0]
        self.assertFalse(m.hit)
        self.assertIsNone(m.triggered_at)

    def test_wrong_transition_type_no_match(self):
        """触发的是 S2 但事件要 S1 → 未命中。"""
        daily = {self.event_date: [_make_transition("S2", "trigger")]}
        report = self.b4.validate(daily, events=self._make_events(), trading_dates=self.dates)
        self.assertEqual(report.hit_count, 0)

    def test_wrong_stage_no_match(self):
        """触发的是 fail 阶段但事件要 trigger/confirm → 未命中。"""
        daily = {self.event_date: [_make_transition("S1", "fail", triggered=False)]}
        report = self.b4.validate(daily, events=self._make_events(), trading_dates=self.dates)
        self.assertEqual(report.hit_count, 0)

    def test_nearest_match_selected(self):
        """多日触发取 |delta| 最小的。"""
        daily = {
            self.dates[10]: [_make_transition("S1", "trigger")],  # -4
            self.dates[16]: [_make_transition("S1", "confirm")],  # +2 ← 最近
            self.dates[19]: [_make_transition("S1", "trigger")],  # +5
        }
        report = self.b4.validate(daily, events=self._make_events(), trading_dates=self.dates)
        self.assertEqual(report.hit_count, 1)
        self.assertEqual(report.matches[0].delta_days, 2)
        self.assertEqual(report.matches[0].matched_stage, "confirm")

    def test_six_of_eight_pass(self):
        """8 事件中 6 命中（≥75%）→ PASS。事件间距 11 天避免 ±5 窗口交叉。"""
        # 间距 11 个交易日：0, 11, 22, 33, 44, 55, 66, 77（共需 78 个交易日）
        offsets = [i * 11 for i in range(8)]
        events = [
            HistoricalEvent(
                id=f"EVT-{i}",
                date=self.dates[off],
                transition_type="S1",
                expected_stage=["trigger", "confirm"],
                desc=f"evt{i}",
                in_data_range=True,
            )
            for i, off in enumerate(offsets)
        ]
        daily = {}
        # 前 6 个事件日触发，后 2 个不触发
        for i, off in enumerate(offsets):
            if i < 6:
                daily[self.dates[off]] = [_make_transition("S1", "trigger")]
            else:
                daily[self.dates[off]] = []
        report = self.b4.validate(daily, events=events, trading_dates=self.dates)
        self.assertEqual(report.hit_count, 6)
        self.assertEqual(report.total_evaluated, 8)
        self.assertEqual(report.verdict, B4Verdict.PASS)

    def test_five_of_eight_fail(self):
        """8 事件中 5 命中（<75%）→ FAIL。事件间距 11 天避免交叉。"""
        offsets = [i * 11 for i in range(8)]
        events = [
            HistoricalEvent(
                id=f"EVT-{i}",
                date=self.dates[off],
                transition_type="S1",
                expected_stage=["trigger", "confirm"],
                desc=f"evt{i}",
                in_data_range=True,
            )
            for i, off in enumerate(offsets)
        ]
        daily = {}
        for i, off in enumerate(offsets):
            if i < 5:
                daily[self.dates[off]] = [_make_transition("S1", "trigger")]
            else:
                daily[self.dates[off]] = []
        report = self.b4.validate(daily, events=events, trading_dates=self.dates)
        self.assertEqual(report.hit_count, 5)
        self.assertEqual(report.verdict, B4Verdict.FAIL)

    def test_out_of_range_event_not_counted(self):
        """in_data_range=False 的事件不计入分母 → INSUFFICIENT_DATA。"""
        events = self._make_events(in_range=False)
        daily = {self.event_date: [_make_transition("S1", "trigger")]}
        report = self.b4.validate(daily, events=events, trading_dates=self.dates)
        self.assertEqual(report.total_evaluated, 0)
        self.assertEqual(report.verdict, B4Verdict.INSUFFICIENT_DATA)

    def test_empty_events_insufficient_data(self):
        """空事件列表 → INSUFFICIENT_DATA。"""
        report = self.b4.validate({}, events=[], trading_dates=self.dates)
        self.assertEqual(report.verdict, B4Verdict.INSUFFICIENT_DATA)

    def test_empty_daily_transitions_insufficient_data(self):
        """无交易日历 → INSUFFICIENT_DATA。"""
        report = self.b4.validate({}, events=self._make_events(), trading_dates=[])
        self.assertEqual(report.verdict, B4Verdict.INSUFFICIENT_DATA)

    def test_per_transition_stats(self):
        """按转换类型统计命中（间距 11 天避免交叉）。"""
        events = [
            HistoricalEvent(
                id="E1",
                date=self.dates[0],
                transition_type="S1",
                expected_stage=["trigger"],
                desc="",
                in_data_range=True,
            ),
            HistoricalEvent(
                id="E2",
                date=self.dates[11],
                transition_type="S1",
                expected_stage=["trigger"],
                desc="",
                in_data_range=True,
            ),
            HistoricalEvent(
                id="E3",
                date=self.dates[22],
                transition_type="S2",
                expected_stage=["trigger"],
                desc="",
                in_data_range=True,
            ),
        ]
        daily = {
            self.dates[0]: [_make_transition("S1", "trigger")],  # hit
            self.dates[11]: [],  # miss
            self.dates[22]: [_make_transition("S2", "trigger")],  # hit
        }
        report = self.b4.validate(daily, events=events, trading_dates=self.dates)
        self.assertEqual(report.per_transition_hits["S1"], {"hit": 1, "total": 2})
        self.assertEqual(report.per_transition_hits["S2"], {"hit": 1, "total": 1})

    def test_data_ready_false_not_counted(self):
        """data_ready=False 的事件不计入分母（S2 需 NLP+high/low 未就绪）。

        回归测试：HistoricalEvent.data_ready docstring + historical_events.yaml
        L59-61 注释一致——data_ready=False 的事件不计入 B4 分母。此前
        total_evaluated 和 _per_transition_stats 只检查 in_data_range 漏检
        data_ready，致 data_ready=False 事件被计入分母但必然 miss，拉低命中率
        （B4 FAIL 3/6）。修复后 S2 data_ready=False 不计入 → B4 PASS 3/3。
        """
        events = [
            HistoricalEvent(
                id="E1",
                date=self.dates[0],
                transition_type="S1",
                expected_stage=["trigger"],
                desc="",
                in_data_range=True,
            ),
            HistoricalEvent(
                id="E2",
                date=self.dates[11],
                transition_type="S2",
                expected_stage=["trigger"],
                desc="",
                in_data_range=True,
                data_ready=False,
            ),  # S2 数据未就绪，不计入分母
        ]
        daily = {
            self.dates[0]: [_make_transition("S1", "trigger")],  # S1 hit
            self.dates[11]: [_make_transition("S2", "trigger")],  # S2 触发但不计入
        }
        report = self.b4.validate(daily, events=events, trading_dates=self.dates)
        # data_ready=False 的 S2 不计入分母
        self.assertEqual(report.total_evaluated, 1)
        self.assertEqual(report.hit_count, 1)
        # per_transition: S2 total=0（data_ready=False 不计入）
        self.assertEqual(report.per_transition_hits["S1"], {"hit": 1, "total": 1})
        self.assertEqual(report.per_transition_hits["S2"], {"hit": 0, "total": 0})
        # S1 1/1 → PASS
        self.assertEqual(report.verdict, B4Verdict.PASS)

    def test_to_dict_serializable(self):
        """to_dict 可 JSON 序列化。"""
        daily = {self.event_date: [_make_transition("S1", "trigger")]}
        report = self.b4.validate(daily, events=self._make_events(), trading_dates=self.dates)
        d = report.to_dict()
        import json

        json.dumps(d)
        self.assertEqual(d["hit_count"], 1)
        self.assertEqual(d["verdict"], "PASS")

    def test_load_events_yaml(self):
        """从默认 YAML 加载事件库（若存在）。"""
        from zephyr.regime.validation.phase2.b4_transition_accuracy import DEFAULT_EVENTS_PATH

        if not DEFAULT_EVENTS_PATH.exists():
            self.skipTest(f"事件库 YAML 不存在: {DEFAULT_EVENTS_PATH}")
        events = self.b4.load_events()
        self.assertGreater(len(events), 0)
        # 验证至少有 S1 和 S2 事件
        types = {e.transition_type for e in events}
        self.assertIn("S1", types)
        self.assertIn("S2", types)
        # 验证字段
        e = events[0]
        self.assertTrue(e.id)
        self.assertIsInstance(e.date, pd.Timestamp)
        self.assertIn(e.transition_type, ["T1", "T2", "T3", "T4", "T5", "T6", "S1", "S2"])

    def test_window_boundary_5_days(self):
        """±5 交易日边界（第 5 天命中，第 6 天不命中）。"""
        # 事件日 +5 交易日 → 命中
        daily_hit = {self.dates[19]: [_make_transition("S1", "trigger")]}
        report = self.b4.validate(daily_hit, events=self._make_events(), trading_dates=self.dates)
        self.assertTrue(report.matches[0].hit)
        # 事件日 +6 交易日 → 未命中
        daily_miss = {self.dates[20]: [_make_transition("S1", "trigger")]}
        report2 = self.b4.validate(daily_miss, events=self._make_events(), trading_dates=self.dates)
        self.assertFalse(report2.matches[0].hit)


if __name__ == "__main__":
    unittest.main()
