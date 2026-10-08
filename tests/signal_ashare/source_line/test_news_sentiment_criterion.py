# [BLUEPRINT] MOD-SIG-160 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SIG-160 news_sentiment_criterion 单元测试（st-fullflow2-20261008）。

红蓝对抗手法覆盖：
- 红-边界：快讯族空/情感分越界/未来时戳 fail-closed（A09 PIT 右闭纪律）；空窗=静默 NONE
- 红-前视：纯函数确定性（同输入必同输出）+ ts>as_of 泄露必红
- 红-契约：半衰加权手算对拍、右闭窗边界（恰 as_of 入窗/恰 as_of-w 出窗）、密度双条件、四档边界
- 红-故障：build_from_news_rows 缺陷行硬失败（打分契约破裂禁静默偏置）
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest

from zephyr.signal_ashare.source_line.news_sentiment_criterion import (
    DEFAULT_HALF_LIFE_MINUTES,
    DEFAULT_WINDOW_MINUTES,
    DENSITY_BURST_FLOOR,
    DENSITY_BURST_RATIO,
    SPIKE_ABS_MIN,
    NewsSentimentInputError,
    NewsSentimentSnapshot,
    SentimentTier,
    build_from_news_rows,
    build_news_sentiment_snapshot,
    classify_sentiment_tier,
)

AS_OF = datetime(2026, 10, 8, 10, 0)


def _ts_before(minutes: float) -> datetime:
    return AS_OF - timedelta(minutes=minutes)


# ── 单元：classify_sentiment_tier ──────────────────────────────────────────


class TestClassifySentimentTier:
    def test_spike_boundaries(self):
        assert classify_sentiment_tier(SPIKE_ABS_MIN, False) == SentimentTier.POSITIVE_SPIKE
        assert classify_sentiment_tier(-SPIKE_ABS_MIN, True) == SentimentTier.NEGATIVE_SPIKE
        assert classify_sentiment_tier(SPIKE_ABS_MIN - 0.01, False) == SentimentTier.WATCH

    def test_watch_and_none(self):
        assert classify_sentiment_tier(0.2, False) == SentimentTier.WATCH
        assert classify_sentiment_tier(-0.2, True) == SentimentTier.WATCH
        assert classify_sentiment_tier(-0.19, True) == SentimentTier.NONE
        assert classify_sentiment_tier(0.0, False) == SentimentTier.NONE


# ── 快照主入口 ─────────────────────────────────────────────────────────────


class TestBuildSnapshot:
    def test_positive_spike(self):
        items = [(_ts_before(10), 0.9), (_ts_before(30), 0.8)]
        snap = build_news_sentiment_snapshot(items, AS_OF)
        assert snap.sentiment_tier == SentimentTier.POSITIVE_SPIKE
        assert snap.window_count == 2
        assert 0.8 < snap.sentiment_index <= 1.0  # 新讯权重高 → 偏向 0.9

    def test_half_life_weighting_manual_check(self):
        """半衰加权手算对拍：age=0 分 w=1，age=half_life 分 w=0.5。"""
        items = [(AS_OF, 1.0), (_ts_before(DEFAULT_HALF_LIFE_MINUTES), -1.0)]
        snap = build_news_sentiment_snapshot(items, AS_OF, window_minutes=180)
        expected = (1.0 * 1.0 + 0.5 * -1.0) / 1.5
        assert snap.sentiment_index == pytest.approx(expected)

    def test_right_closed_window_boundary(self):
        """恰 as_of 入窗、恰 as_of-window 出窗（右闭纪律）。"""
        items = [
            (AS_OF, 0.9),  # 恰上沿 → 入窗
            (_ts_before(DEFAULT_WINDOW_MINUTES), -0.9),  # 恰下沿 → 出窗
        ]
        snap = build_news_sentiment_snapshot(items, AS_OF)
        assert snap.window_count == 1
        assert snap.sentiment_index == pytest.approx(0.9)
        assert snap.prev_window_count == 1

    def test_empty_current_window_is_none_with_note(self):
        items = [(_ts_before(DEFAULT_WINDOW_MINUTES * 3), 0.9)]
        snap = build_news_sentiment_snapshot(items, AS_OF)
        assert snap.sentiment_index is None
        assert snap.sentiment_tier == SentimentTier.NONE
        assert any("静默" in s for s in snap.notes)

    def test_density_burst_ratio_gate(self):
        now_items = [(_ts_before(i + 1), 0.3) for i in range(6)]
        prev_items = [(_ts_before(DEFAULT_WINDOW_MINUTES + i + 1), 0.1) for i in range(2)]
        snap = build_news_sentiment_snapshot(now_items + prev_items, AS_OF)
        assert snap.window_count == 6
        assert snap.prev_window_count == 2
        assert snap.density_burst is True  # 6/2 >= RATIO
        assert snap.sentiment_tier == SentimentTier.WATCH  # 0.3 达 WATCH 未达尖峰

    def test_density_floor_gate_when_prev_zero(self):
        """前窗零基准 → 绝对地板门（≥FLOOR 条）。"""
        items = [(_ts_before(i + 1), 0.3) for i in range(DENSITY_BURST_FLOOR)]
        snap = build_news_sentiment_snapshot(items, AS_OF)
        assert snap.density_burst is True
        assert any("地板门" in s for s in snap.notes)

    def test_no_burst_below_floor(self):
        items = [(_ts_before(i + 1), 0.1) for i in range(DENSITY_BURST_FLOOR - 1)]
        snap = build_news_sentiment_snapshot(items, AS_OF)
        assert snap.density_burst is False

    def test_negative_spike(self):
        items = [(_ts_before(5), -0.9), (_ts_before(40), -0.7)]
        snap = build_news_sentiment_snapshot(items, AS_OF)
        assert snap.sentiment_tier == SentimentTier.NEGATIVE_SPIKE

    def test_determinism_and_json(self):
        items = [(_ts_before(10), 0.9), (_ts_before(30), -0.2)]
        a = build_news_sentiment_snapshot(items, AS_OF).to_dict()
        b = build_news_sentiment_snapshot(items, AS_OF).to_dict()
        assert a == b
        json.dumps(a, ensure_ascii=False, default=str)

    def test_shape(self):
        items = [(_ts_before(10), 0.9)]
        d = build_news_sentiment_snapshot(items, AS_OF).to_dict()
        assert set(d) == set(NewsSentimentSnapshot.__dataclass_fields__) - {"as_of"} | {"as_of"}


# ── fail-closed 面（A09 PIT 纪律）──────────────────────────────────────────


class TestFailClosed:
    def test_empty_family(self):
        with pytest.raises(NewsSentimentInputError, match="快讯族为空"):
            build_news_sentiment_snapshot([], AS_OF)

    def test_future_timestamp_is_pit_violation(self):
        """ts > as_of = 未来泄露，fail-closed 禁吞。"""
        items = [(AS_OF + timedelta(minutes=1), 0.9)]
        with pytest.raises(NewsSentimentInputError, match="未来时戳泄露"):
            build_news_sentiment_snapshot(items, AS_OF)

    def test_score_out_of_range(self):
        items = [(_ts_before(10), 1.5)]
        with pytest.raises(NewsSentimentInputError, match="情感分越界"):
            build_news_sentiment_snapshot(items, AS_OF)

    def test_nan_score(self):
        items = [(_ts_before(10), float("nan"))]
        with pytest.raises(NewsSentimentInputError, match="情感分越界"):
            build_news_sentiment_snapshot(items, AS_OF)

    def test_bad_half_life(self):
        items = [(_ts_before(10), 0.5)]
        with pytest.raises(NewsSentimentInputError, match="半衰非法"):
            build_news_sentiment_snapshot(items, AS_OF, half_life_minutes=0.0)

    def test_epoch_numeric_ts_supported(self):
        """数值 epoch 口径：age 分钟按秒差/60。"""
        as_of = 1_000_000.0
        items = [(as_of - 60.0, 0.9)]  # 1 分钟前
        snap = build_news_sentiment_snapshot(items, as_of, window_minutes=10)
        assert snap.window_count == 1
        assert snap.sentiment_index == pytest.approx(0.9)


# ── DS 读入形态 ────────────────────────────────────────────────────────────


class TestBuildFromNewsRows:
    def test_rows_passthrough(self):
        rows = [
            {"timestamp": _ts_before(10), "sentiment": 0.9},
            {"timestamp": _ts_before(20), "sentiment": 0.8},
        ]
        snap = build_from_news_rows(rows, AS_OF)
        assert snap.sentiment_tier == SentimentTier.POSITIVE_SPIKE

    def test_defect_row_fails_hard(self):
        """缺情感分=打分契约破裂 → 逐行硬失败（禁静默偏置指数）。"""
        rows = [{"timestamp": _ts_before(10)}]
        with pytest.raises(NewsSentimentInputError, match="新闻行缺陷"):
            build_from_news_rows(rows, AS_OF)
