# [MODULE] tests.nlp.test_sentiment_aggregator
# [DOMAIN] D_DATA
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/nlp/test_sentiment_aggregator.py -q
"""test_sentiment_aggregator.py — sentiment_aggregator 单元测试（NLP Phase 7）。

覆盖：
  1. vote_cross_source —— 空输入 / 单源弱信号 / ≥2源同向强信号 / 多源冲突 / 全中性
     / 源内多新闻均化 / polarity 越界裁剪 / 未知源归组 / 多数票压制少数
  2. aggregate_daily —— 分组计数 / 排序 / 空输入 / negative_count 对齐
  3. aggregate_daily_by_symbol —— (日,标的) 分组 / 空 symbol 归组
  4. to_negative_count_series —— 索引与值 / 空输入
  5. source_sentiment_from_result —— 对象/dict/缺失 polarity 鸭型适配

依据：26 号 §2.7 跨源一致性投票裁定（≥2 源同向=强，单源=弱，冲突=0）。
"""

from __future__ import annotations

import math

import pandas as pd

from zephyr.nlp.sentiment_aggregator import (
    STRENGTH_CONFLICT,
    STRENGTH_NONE,
    STRENGTH_STRONG,
    STRENGTH_WEAK,
    SourceSentiment,
    aggregate_daily,
    aggregate_daily_by_symbol,
    source_sentiment_from_result,
    to_negative_count_series,
    vote_cross_source,
)


def _mk(source: str, polarity: float, day: str = "2026-08-19", symbol: str = "", category: str = "") -> SourceSentiment:
    return SourceSentiment(source=source, polarity=polarity, publish_date=day, symbol=symbol, category=category)


# ============ 1. vote_cross_source ============


class TestVoteCrossSource:
    def test_empty_input_returns_none_vote(self):
        v = vote_cross_source([])
        assert v.direction == 0
        assert v.score == 0.0
        assert v.strength == STRENGTH_NONE
        assert v.n_sources == 0

    def test_two_sources_agree_positive_strong(self):
        v = vote_cross_source([_mk("eastmoney", 0.8), _mk("cls", 0.6)])
        assert v.direction == 1
        assert v.strength == STRENGTH_STRONG
        assert v.n_agree == 2
        # tanh 软投票：均值 0.7 → tanh(0.7)
        assert v.score == math.tanh(0.7)
        assert 0 < v.score < 1

    def test_two_sources_agree_negative_strong(self):
        v = vote_cross_source([_mk("eastmoney", -0.9), _mk("rss", -0.5)])
        assert v.direction == -1
        assert v.strength == STRENGTH_STRONG
        assert v.score == math.tanh(-0.7)

    def test_single_source_weak_degraded(self):
        """单源孤证 → 弱信号 ×0.5 增益降级。"""
        v = vote_cross_source([_mk("eastmoney", 0.8)])
        assert v.direction == 1
        assert v.strength == STRENGTH_WEAK
        assert v.score == math.tanh(0.8 * 0.5)
        # 弱信号分必须低于同均值强信号分
        assert abs(v.score) < abs(math.tanh(0.8))

    def test_conflicting_sources_zero_signal(self):
        """正负互搏无多数 → conflict，score=0。"""
        v = vote_cross_source([_mk("eastmoney", 0.9), _mk("cls", -0.9)])
        assert v.direction == 0
        assert v.score == 0.0
        assert v.strength == STRENGTH_CONFLICT

    def test_all_neutral_none(self):
        v = vote_cross_source([_mk("eastmoney", 0.0), _mk("cls", 0.0)])
        assert v.direction == 0
        assert v.strength == STRENGTH_NONE

    def test_majority_overrides_minority(self):
        """2 源正向 vs 1 源负向 → 多数胜出仍为强信号。"""
        v = vote_cross_source([_mk("eastmoney", 0.6), _mk("cls", 0.4), _mk("rss", -0.3)])
        assert v.direction == 1
        assert v.strength == STRENGTH_STRONG
        assert v.n_sources == 3
        assert v.n_agree == 2

    def test_source_internal_averaging(self):
        """同源多条新闻先均化（源内等权），防单源量级霸票。"""
        # eastmoney 3 条均 0.9（源均 0.9），cls 1 条 -0.2 → 源间均值 (0.9-0.2)/2=0.35
        items = [_mk("eastmoney", 0.9)] * 3 + [_mk("cls", -0.2)]
        v = vote_cross_source(items)
        assert v.source_polarities["eastmoney"] == 0.9
        assert v.source_polarities["cls"] == -0.2
        # 1 正 1 负互搏 → conflict
        assert v.strength == STRENGTH_CONFLICT

    def test_polarity_clipped_to_bounds(self):
        # 逐条裁剪 [-1,1]：5.0→1.0, 3.0→1.0，源间均值 1.0
        v = vote_cross_source([_mk("eastmoney", 5.0), _mk("cls", 3.0)])
        assert v.score == math.tanh(1.0)

    def test_nan_polarity_treated_as_zero(self):
        v = vote_cross_source([_mk("eastmoney", float("nan")), _mk("cls", 0.5)])
        # eastmoney 均值 NaN→0（中性），cls 正 → 单源弱信号
        assert v.strength == STRENGTH_WEAK
        assert v.direction == 1

    def test_blank_source_grouped_as_unknown(self):
        v = vote_cross_source([_mk("", 0.5), _mk("  ", 0.7)])
        assert v.n_sources == 1
        assert set(v.source_polarities) == {"unknown"}


# ============ 2. aggregate_daily ============


class TestAggregateDaily:
    def test_groups_by_day_and_counts(self):
        items = [
            _mk("eastmoney", 0.8, "2026-08-18"),
            _mk("cls", -0.6, "2026-08-18"),
            _mk("rss", 0.0, "2026-08-19"),
            _mk("eastmoney", -0.4, "2026-08-19"),
        ]
        out = aggregate_daily(items)
        assert [d.day for d in out] == ["2026-08-18", "2026-08-19"]  # 升序
        d0, d1 = out
        assert d0.n_news == 2 and d0.n_positive == 1 and d0.n_negative == 1 and d0.n_neutral == 0
        assert d1.n_news == 2 and d1.n_negative == 1 and d1.n_neutral == 1
        # negative_count 与 n_negative 对齐（S2 bad_news_flat 入参）
        assert d0.negative_count == 1
        assert d1.negative_count == 1

    def test_empty_input_returns_empty_list(self):
        assert aggregate_daily([]) == []

    def test_vote_fields_propagated(self):
        items = [_mk("eastmoney", 0.8), _mk("cls", 0.6)]
        (d,) = aggregate_daily(items)
        assert d.vote_strength == STRENGTH_STRONG
        assert d.vote_direction == 1
        assert d.vote_score > 0

    def test_mean_polarity(self):
        items = [_mk("eastmoney", 1.0), _mk("cls", -1.0)]
        (d,) = aggregate_daily(items)
        assert d.mean_polarity == 0.0

    def test_per_category_split(self):
        """CAND-DAT-024：四类分桶统计——媒体/研报情绪分开，空 category 归 unknown。"""
        items = [
            _mk("eastmoney", -0.8, "2026-08-18", category="news"),
            _mk("cls", -0.6, "2026-08-18", category="news"),
            _mk("akshare_research_report", 0.9, "2026-08-18", category="research_report"),
            _mk("rss", 0.5, "2026-08-18"),
        ]
        (d,) = aggregate_daily(items)
        pc = d.per_category
        assert pc["news"]["n_news"] == 2 and pc["news"]["n_negative"] == 2
        assert pc["research_report"]["n_news"] == 1 and pc["research_report"]["n_negative"] == 0
        assert pc["unknown"]["n_news"] == 1  # 空 category 兜底
        assert pc["news"]["mean_polarity"] < 0 < pc["research_report"]["mean_polarity"]


# ============ 3. aggregate_daily_by_symbol ============


class TestAggregateDailyBySymbol:
    def test_groups_by_day_and_symbol(self):
        items = [
            _mk("eastmoney", 0.8, "2026-08-19", "600000.SH"),
            _mk("cls", 0.6, "2026-08-19", "600000.SH"),
            _mk("rss", -0.5, "2026-08-19", "000001.SZ"),
        ]
        out = aggregate_daily_by_symbol(items)
        assert len(out) == 2
        assert out[0].symbol == "000001.SZ"
        assert out[1].symbol == "600000.SH"
        assert out[1].n_news == 2
        assert out[1].vote_strength == STRENGTH_STRONG

    def test_blank_symbol_grouped(self):
        items = [_mk("eastmoney", 0.5)]
        out = aggregate_daily_by_symbol(items)
        assert len(out) == 1
        assert out[0].symbol == ""

    def test_empty_input(self):
        assert aggregate_daily_by_symbol([]) == []


# ============ 4. to_negative_count_series ============


class TestToNegativeCountSeries:
    def test_series_index_and_values(self):
        items = [
            _mk("eastmoney", -0.8, "2026-08-18"),
            _mk("cls", -0.6, "2026-08-18"),
            _mk("rss", 0.3, "2026-08-19"),
        ]
        s = to_negative_count_series(aggregate_daily(items))
        assert isinstance(s.index, pd.DatetimeIndex)
        assert list(s.values) == [2.0, 0.0]
        assert s.name == "negative_count"

    def test_empty_returns_empty_series(self):
        s = to_negative_count_series([])
        assert len(s) == 0


# ============ 5. source_sentiment_from_result ============


class _FakeResult:
    def __init__(self, polarity: float) -> None:
        self.polarity = polarity


class TestSourceSentimentFromResult:
    def test_from_object(self):
        ss = source_sentiment_from_result(_FakeResult(0.7), source="cls", publish_date="2026-08-19")
        assert ss.polarity == 0.7
        assert ss.source == "cls"

    def test_from_dict(self):
        ss = source_sentiment_from_result({"polarity": -0.4}, source="rss", publish_date="2026-08-19")
        assert ss.polarity == -0.4

    def test_missing_polarity_defaults_zero(self):
        ss = source_sentiment_from_result(object(), source="rss", publish_date="2026-08-19")
        assert ss.polarity == 0.0

    def test_out_of_range_clipped(self):
        ss = source_sentiment_from_result(_FakeResult(2.5), source="cls", publish_date="2026-08-19")
        assert ss.polarity == 1.0
