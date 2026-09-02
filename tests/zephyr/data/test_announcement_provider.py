# [BLUEPRINT] MOD-L00-004 | tests/zephyr/data/test_announcement_provider.py
# [MODULE] tests.zephyr.data.test_announcement_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.announcement_provider
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L00-004 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AnnouncementProvider 单元测试——巨潮/交易所公告采集器（CAND-DAT-013 / B10-01344）。

覆盖：
    1. 巨潮 HTTP API 报文 → fund_news_data 标准行（NEWS_DATA_COLUMNS 列序）
    2. epoch 毫秒时间戳转换 + static.cninfo.com.cn 链接拼接
    3. news_dedup 去重接线：批内重复标题剔除 + 已库标题剔除
    4. 交易所 RSS 路径：注入 feed_parse 假解析器
    5. 容错：cninfo 异常跳过不抛；不支持 capability → FetchResult.error
"""

from __future__ import annotations

import datetime
from types import SimpleNamespace

import pytest

from zephyr.data import news_dedup
from zephyr.data.implementations.announcement_provider import AnnouncementProvider
from zephyr.data.news_dedup import NEWS_DATA_COLUMNS
from zephyr.data.provider_base import FetchPayload

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

_TS_MS = 1787642400000  # 2026-08-25 10:00:00 +08:00
_EXPECTED_PUB = datetime.datetime.fromtimestamp(
    _TS_MS / 1000, tz=datetime.timezone(datetime.timedelta(hours=8))
).strftime("%Y-%m-%d %H:%M:%S")

_CNINFO_RESPONSE = {
    "announcements": [
        {
            "secCode": "600000",
            "secName": "浦发银行",
            "announcementTitle": "浦发银行关于召开临时股东大会的公告",
            "announcementTime": _TS_MS,
            "adjunctUrl": "finalpage/2026-08-25/123456.PDF",
        },
        {
            "secCode": "000001",
            "secName": "平安银行",
            "announcementTitle": "平安银行2026年半年度报告摘要",
            "announcementTime": _TS_MS,
            "adjunctUrl": "finalpage/2026-08-25/123457.PDF",
        },
    ],
    "totalAnnouncement": 2,
}


def _payload(capability: str = "announcement_news") -> FetchPayload:
    return FetchPayload(
        table="",
        symbols=None,
        start=datetime.date(2026, 8, 25),
        end=datetime.date(2026, 8, 25),
        extra={"capability": capability},
    )


def _provider(**kw) -> AnnouncementProvider:
    kw.setdefault("http_post", lambda url, data=None: _CNINFO_RESPONSE)
    p = AnnouncementProvider(**kw)
    p.connect()
    return p


@pytest.fixture(autouse=True)
def _no_ch_dedup(monkeypatch):
    """单测不触 CH：已库标题哈希集合置空。"""
    monkeypatch.setattr(news_dedup, "_get_existing_hashes", lambda days=7: set())


def _collect(p: AnnouncementProvider, payload: FetchPayload):
    return list(p.fetch(payload, policy=None))


# ---------------------------------------------------------------------------
# 1. 巨潮 HTTP → 标准行
# ---------------------------------------------------------------------------


class TestCninfoFetch:
    def test_rows_aligned_with_news_columns(self):
        results = _collect(_provider(), _payload())
        assert len(results) == 1
        res = results[0]
        assert res.error is None
        assert res.columns == NEWS_DATA_COLUMNS
        assert len(res.rows) == 2
        row = res.rows[0]
        rec = dict(zip(res.columns, row))
        assert rec["title"] == "浦发银行关于召开临时股东大会的公告"
        assert rec["data_source"] == "announcement"
        assert rec["source"] == "cninfo"
        assert rec["region"] == "CN"
        assert rec["language"] == "zh"
        assert rec["news_id"]  # md5 非空

    def test_epoch_ms_converted_and_url_joined(self):
        res = _collect(_provider(), _payload())[0]
        rec = dict(zip(res.columns, res.rows[0]))
        assert rec["publish_time"] == _EXPECTED_PUB
        assert rec["source_url"] == ("http://static.cninfo.com.cn/finalpage/2026-08-25/123456.PDF")

    def test_default_table_is_fund_news(self):
        res = _collect(_provider(), _payload())[0]
        # 逻辑表名 fund_news_data 经 table_registry 真源解析为物理表
        assert res.table == news_dedup._TBL_NEWS_DATA


# ---------------------------------------------------------------------------
# 2. news_dedup 接线
# ---------------------------------------------------------------------------


class TestDedupWiring:
    def test_in_batch_duplicate_titles_removed(self):
        dup = {
            "announcements": [
                _CNINFO_RESPONSE["announcements"][0],
                dict(_CNINFO_RESPONSE["announcements"][0]),  # 同标题重复
            ]
        }
        p = _provider(http_post=lambda url, data=None: dup)
        res = _collect(p, _payload())[0]
        assert len(res.rows) == 1

    def test_existing_db_titles_removed(self, monkeypatch):
        existing = {
            news_dedup._title_hash("浦发银行关于召开临时股东大会的公告"),
        }
        monkeypatch.setattr(news_dedup, "_get_existing_hashes", lambda days=7: existing)
        res = _collect(_provider(), _payload())[0]
        titles = [r[NEWS_DATA_COLUMNS.index("title")] for r in res.rows]
        assert "浦发银行关于召开临时股东大会的公告" not in titles
        assert len(res.rows) == 1


# ---------------------------------------------------------------------------
# 3. 交易所 RSS 路径
# ---------------------------------------------------------------------------


class TestExchangeRss:
    def test_rss_feed_rows(self):
        entry = SimpleNamespace(
            get=lambda k, d="": {
                "published": "Tue, 25 Aug 2026 02:00:00 GMT",
                "title": "上交所：关于某公司停牌公告",
                "link": "http://www.sse.com.cn/disclosure/x.pdf",
                "summary": "停牌公告",
            }.get(k, d)
        )
        fake_parsed = SimpleNamespace(entries=[entry])
        p = _provider(
            http_post=lambda url, data=None: {"announcements": []},
            feeds=("http://fake-rsshub/sse/announcement",),
            http_get=lambda url: "<rss/>",
            feed_parse=lambda content: fake_parsed,
        )
        res = _collect(p, _payload())[0]
        titles = [r[NEWS_DATA_COLUMNS.index("title")] for r in res.rows]
        assert "上交所：关于某公司停牌公告" in titles


# ---------------------------------------------------------------------------
# 4. 容错
# ---------------------------------------------------------------------------


class TestFaultTolerance:
    def test_cninfo_failure_skipped_not_raised(self):
        def http_post(url, data=None):
            raise TimeoutError("cninfo down")

        res = _collect(_provider(http_post=http_post), _payload())
        assert res == []  # 无行则不出批，不抛错

    def test_unsupported_capability_error_result(self):
        res = _collect(_provider(), _payload(capability="kline_daily"))[0]
        assert res.error
        assert "unsupported" in res.error

    def test_health_check(self):
        assert _provider().health_check() is True
