# [BLUEPRINT] MOD-ALT-002 | docs/03_modules/_domain_alt_data/web_scraper_engine/blueprint.md | §test
# [A_test] module_id: MOD-ALT-002 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""WebScraperEngine 单元测试 (MOD-ALT-002, MVP)。

覆盖: 登记校验（非法/重复/未知提取器/域外）/ 限速（首抓恒通/间隔内跳过/失败
不更新台账/按域名独立）/ 抓取异常容错 / 提取（内置 html_text/自定义注入/单条
非法/截断）/ 去重（批内/seen命中/seen异常 fail-open）/ sink 委托与异常不阻断 /
确定性排序 / frozen。
"""

from __future__ import annotations

import dataclasses
import datetime

import pytest

from zephyr.alt_data.web_scraper_engine import (
    InvalidScrapeTargetError,
    InvalidScraperConfigError,
    ScrapeTarget,
    ScrapedRecord,
    UnknownExtractorError,
    WebScraperEngine,
)

_T0 = datetime.datetime(2026, 8, 25, 10, 0, 0)
_T1 = datetime.datetime(2026, 8, 25, 10, 30, 0)
_T2 = datetime.datetime(2026, 8, 25, 11, 30, 0)


def _target(
    target_id: str = "T-1",
    url: str = "https://xueqiu.com/hot/post",
    domain: str = "xueqiu.com",
    extractor: str = "html_text",
    min_interval_seconds: int = 3600,
) -> ScrapeTarget:
    return ScrapeTarget(
        target_id=target_id,
        url=url,
        domain=domain,
        extractor=extractor,
        min_interval_seconds=min_interval_seconds,
    )


def _engine(html: str = "<p>hello</p>", **kw) -> WebScraperEngine:
    return WebScraperEngine(fetcher=lambda url: html, **kw)


# ---------------------------------------------------------------------------
# 登记校验
# ---------------------------------------------------------------------------


class TestRegister:
    def test_register_ok(self):
        e = _engine()
        e.register_target(_target())
        assert e.can_fetch("T-1", _T0) is True

    @pytest.mark.parametrize(
        "kw",
        [
            {"target_id": ""},
            {"url": ""},
            {"domain": "  "},
            {"min_interval_seconds": -1},
        ],
    )
    def test_invalid_target(self, kw):
        e = _engine()
        with pytest.raises(InvalidScrapeTargetError):
            e.register_target(_target(**kw))

    def test_duplicate_target_id(self):
        e = _engine()
        e.register_target(_target())
        with pytest.raises(InvalidScrapeTargetError):
            e.register_target(_target(url="https://xueqiu.com/other"))

    def test_unknown_extractor(self):
        e = _engine()
        with pytest.raises(UnknownExtractorError):
            e.register_target(_target(extractor="nope"))

    def test_domain_not_allowed(self):
        e = _engine(allowed_domains=("guba.eastmoney.com",))
        with pytest.raises(InvalidScrapeTargetError):
            e.register_target(_target(domain="xueqiu.com"))

    def test_domain_allowed(self):
        e = _engine(allowed_domains=("xueqiu.com",))
        e.register_target(_target())
        assert e.can_fetch("T-1", _T0) is True


class TestConfig:
    def test_fetcher_not_callable(self):
        with pytest.raises(InvalidScraperConfigError):
            WebScraperEngine(fetcher=None)

    def test_extractor_not_callable(self):
        with pytest.raises(InvalidScraperConfigError):
            WebScraperEngine(fetcher=lambda u: "", extractors={"bad": 1})

    def test_seen_not_callable(self):
        with pytest.raises(InvalidScraperConfigError):
            WebScraperEngine(fetcher=lambda u: "", seen=1)

    def test_sink_not_callable(self):
        with pytest.raises(InvalidScraperConfigError):
            WebScraperEngine(fetcher=lambda u: "", sink="x")

    def test_max_records_invalid(self):
        with pytest.raises(InvalidScraperConfigError):
            WebScraperEngine(fetcher=lambda u: "", max_records_per_target=0)


# ---------------------------------------------------------------------------
# 限速
# ---------------------------------------------------------------------------


class TestThrottle:
    def test_first_fetch_always_allowed(self):
        e = _engine()
        e.register_target(_target())
        assert e.can_fetch("T-1", _T0) is True

    def test_within_interval_skipped(self):
        e = _engine()
        e.register_target(_target())
        rep1 = e.scrape(_T0)
        assert rep1.fetched == 1
        assert e.can_fetch("T-1", _T1) is False
        rep2 = e.scrape(_T1)
        assert rep2.fetched == 0 and rep2.skipped_throttle == 1

    def test_after_interval_allowed(self):
        e = _engine()
        e.register_target(_target())
        e.scrape(_T0)
        assert e.can_fetch("T-1", _T2) is True
        assert e.scrape(_T2).fetched == 1

    def test_failed_fetch_not_update_ledger(self):
        calls = []

        def flaky(url):
            calls.append(url)
            if len(calls) == 1:
                raise ConnectionError("boom")
            return "<p>ok</p>"

        e = WebScraperEngine(fetcher=flaky)
        e.register_target(_target())
        rep1 = e.scrape(_T0)
        assert rep1.fetched == 0 and rep1.errors
        assert e.can_fetch("T-1", _T1) is True
        assert e.scrape(_T1).fetched == 1

    def test_throttle_per_domain(self):
        e = _engine()
        e.register_target(_target("T-1", domain="a.com", url="https://a.com/1"))
        e.register_target(_target("T-2", domain="b.com", url="https://b.com/1"))
        e.scrape(_T0, target_ids=["T-1"])
        assert e.can_fetch("T-1", _T1) is False
        assert e.can_fetch("T-2", _T1) is True

    def test_unknown_target_scrape_raises(self):
        e = _engine()
        with pytest.raises(InvalidScrapeTargetError):
            e.scrape(_T0, target_ids=["ghost"])

    def test_can_fetch_unknown_raises(self):
        e = _engine()
        with pytest.raises(InvalidScrapeTargetError):
            e.can_fetch("ghost", _T0)


# ---------------------------------------------------------------------------
# 提取
# ---------------------------------------------------------------------------


class TestExtract:
    def test_builtin_html_text(self):
        e = _engine(html="<html><body><p>利好  白酒</p></body></html>")
        e.register_target(_target())
        rep = e.scrape(_T0)
        assert rep.fetched == 1 and rep.extracted == 1
        rec = rep.records[0]
        assert rec.target_id == "T-1" and "利好" in rec.content and "<p>" not in rec.content
        assert rec.title and rec.content_hash

    def test_empty_content_no_record(self):
        e = _engine(html="<p>   </p>")
        e.register_target(_target())
        rep = e.scrape(_T0)
        assert rep.extracted == 0 and rep.records == ()

    def test_custom_extractor_injected(self):
        def posts_extractor(content):
            for i, line in enumerate(content.splitlines()):
                if line.strip():
                    yield {"record_id": f"r{i}", "title": line.strip(), "content": line.strip()}

        e = _engine(html="甲\n乙\n", extractors={"lines": posts_extractor})
        e.register_target(_target(extractor="lines"))
        rep = e.scrape(_T0)
        assert rep.extracted == 2
        assert [r.record_id for r in rep.records] == ["r0", "r1"]

    def test_invalid_record_dropped(self):
        def bad_extractor(content):
            yield {"record_id": "", "title": "x", "content": "x"}
            yield {"record_id": "r1", "title": "", "content": "x"}
            yield {"record_id": "r2", "title": "ok", "content": "x"}

        e = _engine(html="x", extractors={"bad": bad_extractor})
        e.register_target(_target(extractor="bad"))
        rep = e.scrape(_T0)
        assert rep.extracted == 1 and rep.invalid == 2
        assert rep.records[0].record_id == "r2"

    def test_max_records_truncated(self):
        def many(content):
            for i in range(10):
                yield {"record_id": f"r{i}", "title": f"t{i}", "content": "x"}

        e = _engine(html="x", extractors={"many": many}, max_records_per_target=3)
        e.register_target(_target(extractor="many"))
        rep = e.scrape(_T0)
        assert rep.extracted == 3

    def test_fetch_exception_not_blocking(self):
        def boom(url):
            raise ConnectionError("down")

        e = WebScraperEngine(fetcher=boom)
        e.register_target(_target())
        rep = e.scrape(_T0)
        assert rep.fetched == 0 and rep.errors and rep.records == ()


# ---------------------------------------------------------------------------
# 去重
# ---------------------------------------------------------------------------


class TestDedup:
    def test_in_batch_dedup(self):
        def dup(content):
            yield {"record_id": "r1", "title": "same", "content": "c"}
            yield {"record_id": "r2", "title": "same", "content": "c"}

        e = _engine(html="x", extractors={"dup": dup})
        e.register_target(_target(extractor="dup"))
        rep = e.scrape(_T0)
        assert rep.extracted == 2 and rep.dedup_dropped == 1 and len(rep.records) == 1

    def test_seen_drops(self):
        e = _engine(seen=lambda h: True)
        e.register_target(_target())
        rep = e.scrape(_T0)
        assert rep.records == () and rep.dedup_dropped == 1

    def test_seen_exception_fail_open(self):
        def boom(h):
            raise RuntimeError("ch down")

        e = _engine(seen=boom)
        e.register_target(_target())
        rep = e.scrape(_T0)
        assert rep.extracted == 1 and rep.errors  # 保留记录 + 留痕


# ---------------------------------------------------------------------------
# sink / 确定性 / frozen
# ---------------------------------------------------------------------------


class TestSinkDeterminismFrozen:
    def test_sink_called(self):
        seen = []
        e = _engine(sink=lambda recs: seen.extend(recs))
        e.register_target(_target())
        rep = e.scrape(_T0)
        assert rep.sink_attempted and rep.sink_ok and len(seen) == 1

    def test_sink_exception_not_blocking(self):
        def boom(recs):
            raise RuntimeError("ch down")

        e = _engine(sink=boom)
        e.register_target(_target())
        rep = e.scrape(_T0)
        assert rep.sink_attempted and not rep.sink_ok and rep.records

    def test_records_sorted(self):
        def many(content):
            yield {"record_id": "r2", "title": "b", "content": "x2"}
            yield {"record_id": "r1", "title": "a", "content": "x1"}

        e = _engine(html="x", extractors={"many": many})
        e.register_target(_target(extractor="many"))
        rep = e.scrape(_T0)
        assert [r.record_id for r in rep.records] == ["r1", "r2"]

    def test_frozen(self):
        t = _target()
        with pytest.raises(dataclasses.FrozenInstanceError):
            t.domain = "evil.com"
        r = ScrapedRecord(
            target_id="T-1",
            record_id="r1",
            title="t",
            content="c",
            publish_time=None,
            url="u",
            content_hash="h",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.title = "x"
