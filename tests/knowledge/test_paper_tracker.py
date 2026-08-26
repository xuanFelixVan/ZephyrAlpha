# [BLUEPRINT] MOD-KNW-013 | docs/03_modules/_domain_knowledge/paper_tracker/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-013 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_paper_tracker
# [TESTS] src/zephyr/knowledge/paper_tracker.py
"""MOD-KNW-013 单元测试：paper_tracker 论文追踪器。

蓝图验收（B6-08549/CAND-KNW-016，B6 D-RESEARCH-07）：
主题订阅注册表 + arXiv API 注入抓取（不真发）+ 标题/DOI 规范化指纹去重 +
本地 LLM 摘要注入 + 关键词频次滚动窗趋势 + 假设对接注入 sink。
抓取器/摘要器/sink 全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.knowledge.paper_tracker",
    reason="paper_tracker not importable",
)

from zephyr.knowledge.paper_tracker import (  # noqa: E402
    KeywordTrend,
    PaperTracker,
    PaperTrackerError,
    Subscription,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _tracker(*, fetcher=None, summarizer=None, sink=None, **kw) -> PaperTracker:
    kwargs = dict(trend_window=10, trend_recent=3, trend_min_count=2, trend_growth=1.0)
    kwargs.update(kw)
    return PaperTracker(
        arxiv_fetcher=fetcher,
        summarizer=summarizer,
        hypothesis_sink=sink,
        clock=lambda: _T0,
        **kwargs,
    )


def _sub(topic_id: str = "alpha", *, active: bool = True) -> Subscription:
    return Subscription(topic_id=topic_id, query=f"cat:{topic_id}", active=active)


def _raw(title: str, *, doi=None, arxiv_id=None, authors=("Alice", "Bob"), abstract=""):
    raw: dict = {"title": title, "authors": authors, "abstract": abstract}
    if doi is not None:
        raw["doi"] = doi
    if arxiv_id is not None:
        raw["arxiv_id"] = arxiv_id
    return raw


# ──────────────────────────────────────────────────────────────────────────────
# 主题订阅注册表
# ──────────────────────────────────────────────────────────────────────────────


class TestSubscription:
    def test_subscribe_and_list_sorted(self) -> None:
        tracker = _tracker()
        tracker.subscribe(_sub("beta"))
        tracker.subscribe(_sub("alpha"))
        subs = tracker.list_subscriptions()
        assert [s.topic_id for s in subs] == ["alpha", "beta"]  # 确定性排序

    def test_duplicate_topic_raises(self) -> None:
        tracker = _tracker()
        tracker.subscribe(_sub("alpha"))
        with pytest.raises(PaperTrackerError):
            tracker.subscribe(_sub("alpha"))

    def test_empty_topic_id_raises(self) -> None:
        tracker = _tracker()
        with pytest.raises(PaperTrackerError):
            tracker.subscribe(Subscription(topic_id="", query="cat:cs.AI"))

    def test_empty_query_raises(self) -> None:
        tracker = _tracker()
        with pytest.raises(PaperTrackerError):
            tracker.subscribe(Subscription(topic_id="alpha", query=""))

    def test_unsubscribe_ok(self) -> None:
        tracker = _tracker()
        tracker.subscribe(_sub("alpha"))
        tracker.unsubscribe("alpha")
        assert tracker.list_subscriptions() == ()

    def test_unsubscribe_unknown_raises(self) -> None:
        tracker = _tracker()
        with pytest.raises(PaperTrackerError):
            tracker.unsubscribe("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 注入抓取与指纹去重
# ──────────────────────────────────────────────────────────────────────────────


class TestFetch:
    def test_fetch_unknown_topic_raises(self) -> None:
        tracker = _tracker(fetcher=lambda sub: [])
        with pytest.raises(PaperTrackerError):
            tracker.fetch_topic("ghost")

    def test_fetcher_not_injected_fail_closed(self) -> None:
        tracker = _tracker()
        tracker.subscribe(_sub("alpha"))
        with pytest.raises(PaperTrackerError):
            tracker.fetch_topic("alpha")

    def test_fetch_ingests_new_papers_with_summary(self) -> None:
        data = [_raw(
            "Momentum Factor Timing",
            doi="10.1000/XYZ123",
            arxiv_id="2401.00001",
            abstract="momentum abstract",
        )]
        tracker = _tracker(
            fetcher=lambda sub: list(data),
            summarizer=lambda title, abstract: f"摘要:{title[:5]}",
        )
        tracker.subscribe(_sub("alpha"))
        report = tracker.fetch_topic("alpha")
        assert (report.new_count, report.duplicate_count, report.skipped_count) == (1, 0, 0)
        record = tracker.get_paper("doi:10.1000/xyz123")  # DOI 规范化小写
        assert record.summary == "摘要:Momen"
        assert record.authors == ("Alice", "Bob")
        assert record.arxiv_id == "2401.00001"
        assert record.fetched_at == _T0
        assert record.topic_id == "alpha"

    def test_fetcher_exception_wrapped_fail_closed(self) -> None:
        def _boom(sub):
            raise RuntimeError("network down")

        tracker = _tracker(fetcher=_boom)
        tracker.subscribe(_sub("alpha"))
        with pytest.raises(PaperTrackerError):
            tracker.fetch_topic("alpha")

    def test_dedup_by_doi_normalization(self) -> None:
        data = [
            _raw("Paper One Title", doi="10.1000/XYZ123"),
            _raw("Paper Two Title", doi="https://doi.org/10.1000/xyz123"),
        ]
        tracker = _tracker(fetcher=lambda sub: list(data))
        tracker.subscribe(_sub("alpha"))
        report = tracker.fetch_topic("alpha")
        assert (report.new_count, report.duplicate_count) == (1, 1)

    def test_dedup_by_title_fingerprint(self) -> None:
        data = [
            _raw("Deep Learning for Alpha"),
            _raw("deep-learning  FOR  alpha!!!"),
        ]
        tracker = _tracker(fetcher=lambda sub: list(data))
        tracker.subscribe(_sub("alpha"))
        report = tracker.fetch_topic("alpha")
        assert (report.new_count, report.duplicate_count) == (1, 1)

    def test_dedup_by_arxiv_id(self) -> None:
        data = [
            _raw("First Version Title", arxiv_id="2401.00001"),
            _raw("Renamed Second Version", arxiv_id="2401.00001"),
        ]
        tracker = _tracker(fetcher=lambda sub: list(data))
        tracker.subscribe(_sub("alpha"))
        report = tracker.fetch_topic("alpha")
        assert (report.new_count, report.duplicate_count) == (1, 1)
        assert tracker.get_paper("arxiv:2401.00001").title == "First Version Title"

    def test_dedup_across_topics(self) -> None:
        same = _raw("Cross Topic Paper", doi="10.1000/DUP1")
        tracker = _tracker(fetcher=lambda sub: [same])
        tracker.subscribe(_sub("alpha"))
        tracker.subscribe(_sub("beta"))
        first = tracker.fetch_topic("alpha")
        second = tracker.fetch_topic("beta")
        assert first.new_count == 1
        assert (second.new_count, second.duplicate_count) == (0, 1)

    def test_invalid_raw_entry_skipped(self) -> None:
        data = [
            {},
            _raw("   "),
            "not-a-mapping",
            _raw("Valid Paper Title"),
        ]
        tracker = _tracker(fetcher=lambda sub: list(data))
        tracker.subscribe(_sub("alpha"))
        report = tracker.fetch_topic("alpha")
        assert report.fetched_count == 4
        assert (report.new_count, report.skipped_count) == (1, 3)

    def test_summarizer_exception_tolerated(self) -> None:
        def _boom(title, abstract):
            raise RuntimeError("llm down")

        tracker = _tracker(fetcher=lambda sub: [_raw("Some Paper Title")], summarizer=_boom)
        tracker.subscribe(_sub("alpha"))
        report = tracker.fetch_topic("alpha")
        assert report.new_count == 1
        assert tracker.list_papers()[0].summary == ""

    def test_fetch_all_skips_inactive(self) -> None:
        tracker = _tracker(fetcher=lambda sub: [_raw(f"Paper of {sub.topic_id}")])
        tracker.subscribe(_sub("alpha"))
        tracker.subscribe(_sub("beta", active=False))
        reports = tracker.fetch_all()
        assert [r.topic_id for r in reports] == ["alpha"]


# ──────────────────────────────────────────────────────────────────────────────
# 关键词趋势（滚动窗）
# ──────────────────────────────────────────────────────────────────────────────


class TestTrends:
    def test_rising_keyword_detected(self) -> None:
        data = [
            _raw("Value investing signals"),
            _raw("Momentum crash signals"),
            _raw("Momentum factor timing"),
            _raw("Momentum premium research"),
        ]
        tracker = _tracker(fetcher=lambda sub: list(data))
        tracker.subscribe(_sub("alpha"))
        tracker.fetch_topic("alpha")
        trends = {t.keyword: t for t in tracker.keyword_trends()}
        assert trends["momentum"].recent_count == 3
        assert trends["momentum"].older_count == 0
        assert trends["momentum"].rising is True
        assert trends["value"].rising is False  # 仅在 older 段
        assert list(trends) == sorted(trends)  # 确定性排序

    def test_rolling_window_evicts_older(self) -> None:
        data = [
            _raw("Alpha signals research"),
            _raw("Gamma signals research"),
            _raw("Delta signals research"),
            _raw("Theta signals research"),
        ]
        tracker = _tracker(
            fetcher=lambda sub: list(data),
            trend_window=3, trend_recent=2, trend_min_count=1, trend_growth=1.0,
        )
        tracker.subscribe(_sub("alpha"))
        tracker.fetch_topic("alpha")
        trends = {t.keyword: t for t in tracker.keyword_trends()}
        assert "alpha" not in trends  # 窗口 maxlen=3 已逐出首篇
        assert trends["gamma"].older_count == 1
        assert trends["delta"].recent_count == 1
        assert trends["delta"].rising is True


# ──────────────────────────────────────────────────────────────────────────────
# 假设对接（注入 sink）
# ──────────────────────────────────────────────────────────────────────────────


class TestHypothesisSink:
    def test_sink_receives_rising_terms(self) -> None:
        received: list[tuple[str, tuple[str, ...]]] = []
        data = [
            _raw("Momentum crash signals"),
            _raw("Momentum factor timing"),
            _raw("Momentum premium research"),
        ]
        tracker = _tracker(
            fetcher=lambda sub: list(data),
            sink=lambda paper_id, terms: received.append((paper_id, terms)),
        )
        tracker.subscribe(_sub("alpha"))
        tracker.fetch_topic("alpha")
        assert received  # 第三篇入库时 momentum 已 rising
        assert any("momentum" in terms for _, terms in received)

    def test_sink_exception_swallowed(self) -> None:
        def _boom(paper_id, terms):
            raise RuntimeError("sink down")

        tracker = _tracker(
            fetcher=lambda sub: [_raw("Momentum Paper Title")],
            sink=_boom,
            trend_min_count=1,
        )
        tracker.subscribe(_sub("alpha"))
        report = tracker.fetch_topic("alpha")  # sink 异常不阻断入库
        assert report.new_count == 1


# ──────────────────────────────────────────────────────────────────────────────
# 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_get_paper_unknown_raises(self) -> None:
        tracker = _tracker()
        with pytest.raises(PaperTrackerError):
            tracker.get_paper("doi:ghost")

    def test_list_papers_sorted_and_filtered(self) -> None:
        data = [
            _raw("Paper B", doi="10.1000/B"),
            _raw("Paper A", doi="10.1000/A"),
        ]
        tracker = _tracker(fetcher=lambda sub: list(data))
        tracker.subscribe(_sub("alpha"))
        tracker.subscribe(_sub("beta"))
        tracker.fetch_topic("alpha")
        tracker.fetch_topic("beta")  # 同指纹跨主题去重 → 2 篇均重复，归属 alpha
        papers = tracker.list_papers()
        assert [p.paper_id for p in papers] == ["doi:10.1000/a", "doi:10.1000/b"]  # 同刻按 id 排序
        assert len(tracker.list_papers("alpha")) == 2
        assert tracker.list_papers("beta") == ()


# ──────────────────────────────────────────────────────────────────────────────
# 确定性与参数护栏
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_inputs_same_outputs(self) -> None:
        data = [
            _raw("Momentum crash signals", doi="10.1000/M1"),
            _raw("Momentum factor timing", doi="10.1000/M2"),
            _raw("Momentum crash signals", doi="https://doi.org/10.1000/m1"),
        ]

        def _run_once():
            tracker = _tracker(fetcher=lambda sub: list(data))
            tracker.subscribe(_sub("alpha"))
            report = tracker.fetch_topic("alpha")
            return report, tracker.list_papers(), tracker.keyword_trends()

        first = _run_once()
        second = _run_once()
        assert first == second  # 同输入必同输出（dataclass 值相等）


class TestConfig:
    def test_invalid_trend_params_raise(self) -> None:
        with pytest.raises(PaperTrackerError):
            _tracker(trend_window=0)
        with pytest.raises(PaperTrackerError):
            _tracker(trend_recent=11)  # recent > window
        with pytest.raises(PaperTrackerError):
            _tracker(trend_min_count=0)
        with pytest.raises(PaperTrackerError):
            _tracker(trend_growth=0.0)
