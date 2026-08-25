# [BLUEPRINT] MOD-ALT-001 | docs/03_modules/_domain_alt_data/social_sentiment_collector/blueprint.md | §test
# [A_test] module_id: MOD-ALT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""SocialSentimentCollector 单元测试 (MOD-ALT-001, MVP)。

覆盖: 聚合（均值/engagement加权/正压比/多标的/多来源去重）/ PIT（未来帖拒收）/
单帖 Fail-Closed（空id/空symbol/空文本/坏时间）/ scorer（越界/NaN/异常→unscored）/
fetcher 异常容错 / 配置 Fail-Closed / sink 委托与异常不阻断 / 确定性排序 / frozen。
"""

from __future__ import annotations

import dataclasses
import datetime

import pytest

from zephyr.alt_data.social_sentiment_collector import (
    CollectReport,
    InvalidCollectorConfigError,
    InvalidSocialPostError,
    SocialPost,
    SocialSentimentCollector,
    SocialSentimentDaily,
)

_DATE = "2026-08-25"
_TS = datetime.datetime(2026, 8, 25, 10, 30, 0)


def _post(
    post_id: str = "P-1",
    symbol: str = "600519",
    text: str = "利好茅台",
    publish_time: datetime.datetime = _TS,
    source: str = "guba",
    likes: int = 0,
    comments: int = 0,
    reads: int = 0,
) -> SocialPost:
    return SocialPost(
        post_id=post_id,
        symbol=symbol,
        publish_time=publish_time,
        text=text,
        source=source,
        likes=likes,
        comments=comments,
        reads=reads,
    )


def _collector(posts, scorer=None, sink=None) -> SocialSentimentCollector:
    return SocialSentimentCollector(
        fetcher=lambda trade_date, symbols: list(posts),
        scorer=scorer or (lambda text: 0.5),
        sink=sink,
    )


# ---------------------------------------------------------------------------
# 配置 Fail-Closed
# ---------------------------------------------------------------------------


class TestConfigFailClosed:
    def test_fetcher_none_rejected(self):
        with pytest.raises(InvalidCollectorConfigError):
            SocialSentimentCollector(fetcher=None, scorer=lambda t: 0.0)

    def test_fetcher_not_callable_rejected(self):
        with pytest.raises(InvalidCollectorConfigError):
            SocialSentimentCollector(fetcher="x", scorer=lambda t: 0.0)

    def test_scorer_none_rejected(self):
        with pytest.raises(InvalidCollectorConfigError):
            SocialSentimentCollector(fetcher=lambda d, s: [], scorer=None)

    def test_scorer_not_callable_rejected(self):
        with pytest.raises(InvalidCollectorConfigError):
            SocialSentimentCollector(fetcher=lambda d, s: [], scorer=1.0)

    def test_sink_not_callable_rejected(self):
        with pytest.raises(InvalidCollectorConfigError):
            SocialSentimentCollector(fetcher=lambda d, s: [], scorer=lambda t: 0.0, sink=42)


class TestInputValidation:
    def test_bad_trade_date(self):
        c = _collector([])
        with pytest.raises(ValueError):
            c.collect("2026/08/25", ["600519"])

    def test_empty_symbols(self):
        c = _collector([])
        with pytest.raises(ValueError):
            c.collect(_DATE, [])

    def test_blank_symbol(self):
        c = _collector([])
        with pytest.raises(ValueError):
            c.collect(_DATE, ["  "])


# ---------------------------------------------------------------------------
# 聚合
# ---------------------------------------------------------------------------


class TestAggregation:
    def test_mean_and_counts(self):
        posts = [_post("P-1"), _post("P-2"), _post("P-3")]
        scores = iter([0.6, -0.2, 0.4])
        c = _collector(posts, scorer=lambda t: next(scores))
        rep = c.collect(_DATE, ["600519"])
        assert rep.fetched == 3 and rep.accepted == 3 and rep.rejected == 0
        assert len(rep.dailies) == 1
        d = rep.dailies[0]
        assert d.symbol == "600519" and d.trade_date == _DATE
        assert d.post_count == 3 and d.scored_count == 3
        assert d.sentiment_mean == pytest.approx((0.6 - 0.2 + 0.4) / 3)
        assert d.positive_ratio == pytest.approx(2 / 3)

    def test_engagement_weighted_mean(self):
        posts = [
            _post("P-1", likes=9, comments=0, reads=0),   # w=10
            _post("P-2", likes=0, comments=0, reads=0),   # w=1
        ]
        scores = iter([1.0, -1.0])
        c = _collector(posts, scorer=lambda t: next(scores))
        d = c.collect(_DATE, ["600519"]).dailies[0]
        assert d.engagement_weighted_mean == pytest.approx((10 * 1.0 + 1 * -1.0) / 11)

    def test_multi_symbol_sorted(self):
        posts = [_post("P-1", symbol="600519"), _post("P-2", symbol="000001")]
        c = _collector(posts)
        rep = c.collect(_DATE, ["600519", "000001"])
        assert [d.symbol for d in rep.dailies] == ["000001", "600519"]

    def test_sources_dedup_sorted(self):
        posts = [
            _post("P-1", source="xueqiu"),
            _post("P-2", source="guba"),
            _post("P-3", source="xueqiu"),
        ]
        c = _collector(posts)
        d = c.collect(_DATE, ["600519"]).dailies[0]
        assert d.sources == ("guba", "xueqiu")

    def test_dict_posts_accepted(self):
        posts = [
            {
                "post_id": "P-9",
                "symbol": "600519",
                "publish_time": _TS,
                "text": "t",
                "source": "guba",
            }
        ]
        c = _collector(posts)
        rep = c.collect(_DATE, ["600519"])
        assert rep.accepted == 1

    def test_empty_batch(self):
        c = _collector([])
        rep = c.collect(_DATE, ["600519"])
        assert rep.fetched == 0 and rep.dailies == ()


# ---------------------------------------------------------------------------
# PIT 与单帖 Fail-Closed
# ---------------------------------------------------------------------------


class TestPostValidation:
    def test_future_post_rejected_pit(self):
        future = _post("P-F", publish_time=datetime.datetime(2026, 8, 26, 9, 0, 0))
        c = _collector([future])
        rep = c.collect(_DATE, ["600519"])
        assert rep.rejected == 1 and rep.accepted == 0 and rep.dailies == ()

    def test_late_same_day_accepted(self):
        late = _post("P-L", publish_time=datetime.datetime(2026, 8, 25, 23, 59, 59))
        c = _collector([late])
        assert c.collect(_DATE, ["600519"]).accepted == 1

    @pytest.mark.parametrize(
        "kw",
        [
            {"post_id": ""},
            {"post_id": "  "},
            {"symbol": ""},
            {"text": ""},
            {"text": "   "},
        ],
    )
    def test_blank_fields_rejected(self, kw):
        raw = {
            "post_id": "P-1",
            "symbol": "600519",
            "publish_time": _TS,
            "text": "t",
            "source": "guba",
        }
        raw.update(kw)
        c = _collector([raw])
        rep = c.collect(_DATE, ["600519"])
        assert rep.rejected == 1 and rep.dailies == ()

    def test_bad_publish_time_rejected(self):
        raw = {
            "post_id": "P-1",
            "symbol": "600519",
            "publish_time": "not-a-time",
            "text": "t",
            "source": "guba",
        }
        c = _collector([raw])
        rep = c.collect(_DATE, ["600519"])
        assert rep.rejected == 1

    def test_invalid_post_type_rejected(self):
        c = _collector([12345])
        rep = c.collect(_DATE, ["600519"])
        assert rep.rejected == 1

    def test_socialpost_blank_field_raises(self):
        with pytest.raises(InvalidSocialPostError):
            _post(post_id="")


# ---------------------------------------------------------------------------
# scorer
# ---------------------------------------------------------------------------


class TestScorer:
    def test_out_of_range_unscored(self):
        c = _collector([_post("P-1")], scorer=lambda t: 1.5)
        rep = c.collect(_DATE, ["600519"])
        assert rep.accepted == 1 and rep.unscored == 1
        assert rep.dailies[0].post_count == 1 and rep.dailies[0].scored_count == 0
        assert rep.dailies[0].sentiment_mean is None

    def test_nan_unscored(self):
        c = _collector([_post("P-1")], scorer=lambda t: float("nan"))
        rep = c.collect(_DATE, ["600519"])
        assert rep.unscored == 1

    def test_scorer_exception_unscored_not_blocking(self):
        def boom(text):
            raise RuntimeError("llm down")

        c = _collector([_post("P-1")], scorer=boom)
        rep = c.collect(_DATE, ["600519"])
        assert rep.unscored == 1 and rep.dailies[0].post_count == 1

    def test_boundary_scores_accepted(self):
        posts = [_post("P-1"), _post("P-2")]
        scores = iter([-1.0, 1.0])
        c = _collector(posts, scorer=lambda t: next(scores))
        d = c.collect(_DATE, ["600519"]).dailies[0]
        assert d.scored_count == 2 and d.sentiment_mean == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# fetcher / sink
# ---------------------------------------------------------------------------


class TestFetcherSink:
    def test_fetcher_exception_empty_batch(self):
        def boom(d, s):
            raise ConnectionError("net down")

        c = SocialSentimentCollector(fetcher=boom, scorer=lambda t: 0.1)
        rep = c.collect(_DATE, ["600519"])
        assert rep.fetched == 0 and rep.dailies == () and rep.errors

    def test_sink_called_with_dailies(self):
        seen = []
        c = _collector([_post("P-1")], sink=lambda dailies: seen.extend(dailies))
        rep = c.collect(_DATE, ["600519"])
        assert rep.sink_attempted and rep.sink_ok and len(seen) == 1

    def test_sink_exception_not_blocking(self):
        def boom(dailies):
            raise RuntimeError("ch down")

        c = _collector([_post("P-1")], sink=boom)
        rep = c.collect(_DATE, ["600519"])
        assert rep.sink_attempted and not rep.sink_ok and rep.errors
        assert len(rep.dailies) == 1

    def test_no_sink(self):
        c = _collector([_post("P-1")])
        rep = c.collect(_DATE, ["600519"])
        assert not rep.sink_attempted and rep.sink_ok


# ---------------------------------------------------------------------------
# 确定性与 frozen
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_input_same_output(self):
        posts = [_post("P-1", symbol="600519"), _post("P-2", symbol="000001")]
        c1, c2 = _collector(posts), _collector(posts)
        assert c1.collect(_DATE, ["600519", "000001"]) == c2.collect(_DATE, ["600519", "000001"])

    def test_frozen(self):
        d = SocialSentimentDaily(
            trade_date=_DATE,
            symbol="600519",
            post_count=1,
            scored_count=1,
            sentiment_mean=0.5,
            engagement_weighted_mean=0.5,
            positive_ratio=1.0,
            sources=("guba",),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.symbol = "000001"
        p = _post("P-1")
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.symbol = "000001"
