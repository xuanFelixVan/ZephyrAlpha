# [BLUEPRINT] MOD-DATA-067 | 待统筹登记（真源=candidate_module_registry CAND-DAT-022 行） | §test
# [MODULE] tests.scripts.test_audit_news_publish_time
# [DOMAIN] D_DATA
# [DEPENDENCIES] scripts/audit_news_publish_time.py（importlib 文件加载）
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据纯内存：不触 ClickHouse、不触网、不落盘；query_fn 全 mock
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=publish_time 口径审计逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DATA-067_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-DATA-067 publish_time 口径审计脚本 单元测试（CAND-DAT-022，mock 不触库）。

覆盖：
  1. parse_ch_datetime —— 带时区/naive/垃圾/空串
  2. parse_sample_tsv —— 正常行/短行跳过
  3. compute_delay_stats —— 分布/负延迟/采集延迟/纪元哨兵剔除
  4. compute_fingerprint_ratio / compute_hourly_snap_ratio —— 假时间戳指纹
  5. compute_multi_source_spread —— 同标题多源极差
  6. assess_verdict —— TRUSTED/SUSPECT/DISTRUSTED/INSUFFICIENT_DATA 四档
  7. build_report + render_markdown —— 端到端装配与关键小节
  8. main —— 参数非法 exit 2
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from datetime import datetime, timedelta, timezone

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "audit_news_publish_time",
    _ROOT / "scripts" / "audit_news_publish_time.py",
)
anpt = importlib.util.module_from_spec(_spec)
sys.modules["audit_news_publish_time"] = anpt
_spec.loader.exec_module(anpt)

UTC = timezone.utc
_T0 = datetime(2026, 8, 30, 12, 0, 0, tzinfo=UTC)


def _rec(
    news_id: str = "id1",
    publish: datetime | None = _T0,
    crawl: datetime | None = None,
    ingest: datetime | None = None,
    source: str = "srcA",
    title: str = "标题",
) -> anpt.NewsTimeRecord:
    return anpt.NewsTimeRecord(
        news_id=news_id,
        publish_time=publish,
        crawl_time=crawl if crawl is not None else (publish + timedelta(minutes=5) if publish else None),
        ingest_ts=ingest if ingest is not None else (publish + timedelta(minutes=6) if publish else None),
        source=source,
        title=title,
    )


class TestParseChDatetime:
    def test_tz_aware_with_offset(self):
        dt = anpt.parse_ch_datetime("2026-08-30 19:36:14+08:00")
        assert dt is not None and dt.tzinfo is not None
        assert dt == datetime(2026, 8, 30, 11, 36, 14, tzinfo=UTC)

    def test_tz_aware_with_millis(self):
        dt = anpt.parse_ch_datetime("2026-08-30 11:36:15.123+00:00")
        assert dt is not None and dt.microsecond == 123000

    def test_naive_returns_none(self):
        assert anpt.parse_ch_datetime("2026-08-30 19:36:14") is None

    def test_garbage_and_empty(self):
        assert anpt.parse_ch_datetime("not-a-time") is None
        assert anpt.parse_ch_datetime("") is None
        assert anpt.parse_ch_datetime(None) is None


class TestParseSampleTsv:
    def test_normal_rows(self):
        tsv = (
            "id1\t2026-08-30 19:36:14+08:00\t2026-08-30 11:36:15+00:00\t2026-08-30 11:36:15+00:00\tsrcA\t标题甲\n"
            "id2\t2026-08-29 10:00:00+08:00\t2026-08-29 02:01:00+00:00\t2026-08-29 02:01:05+00:00\tsrcB\t标题乙\n"
        )
        recs = anpt.parse_sample_tsv(tsv)
        assert len(recs) == 2
        assert recs[0].news_id == "id1" and recs[0].source == "srcA"
        assert recs[1].publish_time == datetime(2026, 8, 29, 2, 0, 0, tzinfo=UTC)

    def test_short_lines_skipped(self):
        tsv = "id1\tonly-two\n\nid2\t2026-08-30 19:36:14+08:00\t2026-08-30 11:36:15+00:00\t2026-08-30 11:36:15+00:00\ts\t t\n"
        recs = anpt.parse_sample_tsv(tsv)
        assert len(recs) == 1 and recs[0].news_id == "id2"

    def test_empty(self):
        assert anpt.parse_sample_tsv("") == []


class TestDelayStats:
    def test_normal_positive_lag(self):
        recs = [_rec(news_id=f"id{i}", publish=_T0 + timedelta(minutes=i)) for i in range(10)]
        stats = anpt.compute_delay_stats(recs, "crawl_time")
        assert stats.n == 10
        assert stats.p50 == 300.0  # 5min
        assert stats.n_negative == 0 and stats.n_delayed == 0

    def test_negative_lag_counted(self):
        bad = _rec(news_id="bad", publish=_T0, crawl=_T0 - timedelta(minutes=10))
        stats = anpt.compute_delay_stats([bad], "crawl_time")
        assert stats.n_negative == 1

    def test_collection_delay_counted(self):
        old = _rec(news_id="old", publish=_T0 - timedelta(days=3), crawl=_T0, ingest=_T0)
        stats = anpt.compute_delay_stats([old], "crawl_time")
        assert stats.n_delayed == 1

    def test_epoch_sentinel_excluded(self):
        epoch = _rec(news_id="ep", publish=datetime(1970, 1, 1, 8, 0, 1, tzinfo=UTC))
        stats = anpt.compute_delay_stats([epoch], "crawl_time")
        assert stats.n == 0

    def test_missing_side_excluded(self):
        rec = _rec(news_id="x", publish=None)
        assert anpt.compute_delay_stats([rec], "crawl_time").n == 0


class TestFingerprints:
    def test_publish_eq_crawl_fingerprint(self):
        fake = _rec(news_id="f", publish=_T0, crawl=_T0 + timedelta(seconds=1))
        real = _rec(news_id="r", publish=_T0, crawl=_T0 + timedelta(hours=2))
        assert anpt.compute_fingerprint_ratio([fake, real]) == 0.5

    def test_fingerprint_empty(self):
        assert anpt.compute_fingerprint_ratio([]) == 0.0

    def test_hourly_snap(self):
        snapped = _rec(news_id="s", publish=datetime(2026, 8, 30, 9, 0, 0, tzinfo=UTC))
        normal = _rec(news_id="n", publish=datetime(2026, 8, 30, 9, 3, 21, tzinfo=UTC))
        assert anpt.compute_hourly_snap_ratio([snapped, normal]) == 0.5

    def test_epoch_missing_count(self):
        epoch = _rec(news_id="e", publish=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC))
        assert anpt.count_epoch_missing([epoch, _rec()]) == 1


class TestMultiSourceSpread:
    def test_spread_stats_and_suspect(self):
        tsv = (
            "同标题\tcls\t2026-08-28 10:00:00+08:00\n"
            "同标题\teastmoney\t2026-08-30 11:00:00+08:00\n"
            "另一标题\tcls\t2026-08-29 09:30:00+08:00\n"
            "另一标题\trss\t2026-08-29 09:35:00+08:00\n"
            "单源标题\tcls\t2026-08-29 09:40:00+08:00\n"
        )
        spread = anpt.compute_multi_source_spread(tsv)
        assert spread.n_groups == 2
        assert spread.n_suspect == 1  # 同标题跨源差 49h
        assert spread.max_hours >= 49.0
        assert spread.samples[0][1] == "cls/eastmoney"

    def test_empty(self):
        spread = anpt.compute_multi_source_spread("")
        assert spread.n_groups == 0 and spread.samples == ()


class TestAssessVerdict:
    def test_trusted(self):
        verdict, _ = anpt.assess_verdict(0.01, 0.001, 600.0, 0.01, 100)
        assert verdict == anpt.VERDICT_TRUSTED

    def test_suspect(self):
        verdict, _ = anpt.assess_verdict(0.10, 0.02, 7200.0, 0.10, 100)
        assert verdict == anpt.VERDICT_SUSPECT

    def test_distrusted_on_fingerprint(self):
        verdict, reasons = anpt.assess_verdict(0.80, 0.0, 60.0, 0.0, 100)
        assert verdict == anpt.VERDICT_DISTRUSTED
        assert any("publish≈crawl" in r for r in reasons)

    def test_insufficient_data(self):
        verdict, _ = anpt.assess_verdict(0.0, 0.0, 0.0, 0.0, 0)
        assert verdict == anpt.VERDICT_INSUFFICIENT


class TestBuildAndRender:
    def test_build_report_end_to_end(self):
        recs = [
            _rec(news_id="ok1"),
            _rec(news_id="fake1", publish=_T0, crawl=_T0 + timedelta(seconds=1)),
            _rec(news_id="neg1", publish=_T0, crawl=_T0 - timedelta(hours=1), ingest=_T0 - timedelta(hours=1)),
        ]
        multi_tsv = "同标题\ta\t2026-08-28 10:00:00+08:00\n同标题\tb\t2026-08-29 10:00:00+08:00\n"
        report = anpt.build_report(recs, multi_tsv, table="db.tbl", window_days=30)
        assert report.sample_size == 3
        assert report.crawl_delay.n_negative == 1
        assert 0.0 < report.fingerprint_ratio < 1.0
        assert report.multi_source.n_groups == 1
        assert report.suspect_samples  # fake1/neg1 入清单
        md = anpt.render_markdown(report)
        assert "口径 A" in md and "口径 C" in md and "口径结论" in md
        assert report.verdict in md
        assert "fake1" in md

    def test_empty_records_insufficient(self):
        report = anpt.build_report([], "", table="db.tbl", window_days=30)
        assert report.verdict == anpt.VERDICT_INSUFFICIENT
        assert "样本为空" in report.verdict_reasons[0]


class TestFetchSqlForm:
    def test_fetch_sample_sql(self):
        seen: list[str] = []
        anpt.fetch_sample(lambda sql: seen.append(sql) or "", 30, 5000)
        assert "INTERVAL 30 DAY" in seen[0] and "LIMIT 5000" in seen[0]
        assert "publish_time" in seen[0] and "crawl_time" in seen[0] and "ingest_ts" in seen[0]

    def test_fetch_multi_source_sql(self):
        seen: list[str] = []
        anpt.fetch_multi_source(lambda sql: seen.append(sql) or "", 30, 100)
        assert "uniqExact(source) > 1" in seen[0] and "LIMIT 100" in seen[0]


class TestMain:
    def test_invalid_args_exit_2(self):
        assert anpt.main(["--days", "0"]) == 2
        assert anpt.main(["--sample", "-5"]) == 2
