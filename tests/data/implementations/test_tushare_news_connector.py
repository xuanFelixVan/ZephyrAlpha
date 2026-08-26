# [BLUEPRINT] MOD-DATA-065 | docs/03_modules/_domain_data/tushare_news_connector/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATA-065 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data.implementations.test_tushare_news_connector
# [TESTS] src/zephyr/data/implementations/tushare_news_connector.py
"""MOD-DATA-065 单元测试：tushare_news_connector tushare 新闻源接入器。

蓝图验收（B13-04043/CAND-DAT-019，A3数据架构）：
news 快讯接入 news_collector 管道语义（API 全注入不真发请求）+
标题+时间窗指纹去重 + 回补区间完整性校验 + 质量门控挂接（注入 gate）。
API/时钟/门控全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data.implementations.tushare_news_connector",
    reason="tushare_news_connector not importable",
)

from zephyr.data.implementations.tushare_news_connector import (  # noqa: E402
    NewsItem,
    TushareNewsConnector,
    TushareNewsError,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)          # 窗对齐起点（窗宽 300s）
_T1 = datetime.datetime(2026, 8, 25, 9, 35, 0)
_T2 = datetime.datetime(2026, 8, 25, 9, 40, 0)
_END = datetime.datetime(2026, 8, 25, 10, 0, 0)


def _raw(title: str, ts: datetime.datetime, news_id: str = "", content: str = "正文") -> dict:
    return {"title": title, "content": content, "published_at": ts, "news_id": news_id}


def _connector(
    items: list[dict] | None = None,
    *,
    gate=None,
    window: int = 300,
) -> TushareNewsConnector:
    return TushareNewsConnector(
        api=(lambda s, e: list(items or [])),
        clock=lambda: _T0,
        gate=gate,
        dedup_window_seconds=window,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 去重指纹
# ──────────────────────────────────────────────────────────────────────────────


class TestFingerprint:
    def test_fingerprint_deterministic(self) -> None:
        fp1 = TushareNewsConnector.fingerprint("央行降准", _T0)
        fp2 = TushareNewsConnector.fingerprint("央行降准", _T0)
        assert fp1 == fp2 and len(fp1) == 64  # sha256 hex

    def test_title_normalized(self) -> None:
        fp1 = TushareNewsConnector.fingerprint("央行  降准 ", _T0)
        fp2 = TushareNewsConnector.fingerprint("央行 降准", _T0)
        assert fp1 == fp2  # 空白折叠后同指纹

    def test_same_window_same_fingerprint(self) -> None:
        fp1 = TushareNewsConnector.fingerprint("t", datetime.datetime(2026, 8, 25, 9, 30, 10))
        fp2 = TushareNewsConnector.fingerprint("t", datetime.datetime(2026, 8, 25, 9, 34, 59))
        assert fp1 == fp2  # 同 300s 窗桶

    def test_cross_window_differs(self) -> None:
        fp1 = TushareNewsConnector.fingerprint("t", _T0)
        fp2 = TushareNewsConnector.fingerprint("t", _T1)
        assert fp1 != fp2

    def test_different_title_differs(self) -> None:
        fp1 = TushareNewsConnector.fingerprint("甲", _T0)
        fp2 = TushareNewsConnector.fingerprint("乙", _T0)
        assert fp1 != fp2


# ──────────────────────────────────────────────────────────────────────────────
# 抓取（管道语义 + 去重 + 门控）
# ──────────────────────────────────────────────────────────────────────────────


class TestFetch:
    def test_fetch_ok_sorted(self) -> None:
        conn = _connector([
            _raw("晚新闻", _T2, "n3"),
            _raw("早新闻", _T0, "n1"),
            _raw("中新闻", _T1, "n2"),
        ])
        report = conn.fetch_latest(_T0, _END)
        assert [i.title for i in report.accepted] == ["早新闻", "中新闻", "晚新闻"]
        assert report.dedup_dropped == 0
        assert report.gate_dropped == 0
        assert all(i.source == "tushare" for i in report.accepted)

    def test_dedup_within_batch(self) -> None:
        conn = _connector([
            _raw("同一新闻", _T0, "n1"),
            _raw(" 同一新闻 ", datetime.datetime(2026, 8, 25, 9, 32, 0), "n2"),  # 同窗同题
        ])
        report = conn.fetch_latest(_T0, _END)
        assert len(report.accepted) == 1
        assert report.dedup_dropped == 1

    def test_dedup_across_fetches(self) -> None:
        items = [_raw("旧闻", _T0, "n1")]
        conn = _connector(items)
        conn.fetch_latest(_T0, _END)
        assert conn.seen_count() == 1
        report = conn.fetch_latest(_T0, _END)  # 重抓同条
        assert report.accepted == ()
        assert report.dedup_dropped == 1

    def test_gate_drops(self) -> None:
        conn = _connector(
            [_raw("合格", _T0, "n1"), _raw("广告", _T1, "n2")],
            gate=lambda item: "广告" not in item.title,
        )
        report = conn.fetch_latest(_T0, _END)
        assert [i.title for i in report.accepted] == ["合格"]
        assert report.gate_dropped == 1

    def test_derived_news_id_deterministic(self) -> None:
        conn = _connector([_raw("无id新闻", _T0)])  # 缺 news_id
        report = conn.fetch_latest(_T0, _END)
        news_id = report.accepted[0].news_id
        assert news_id.startswith("tushare-") and len(news_id) == len("tushare-") + 12
        conn2 = _connector([_raw("无id新闻", _T0)])
        assert conn2.fetch_latest(_T0, _END).accepted[0].news_id == news_id

    def test_iso_string_timestamp_parsed(self) -> None:
        conn = _connector([{
            "title": "字符串时间", "content": "",
            "published_at": "2026-08-25T09:30:00", "news_id": "n1",
        }])
        report = conn.fetch_latest(_T0, _END)
        assert report.accepted[0].published_at == _T0

    def test_fetch_invalid_args_raise(self) -> None:
        conn = _connector([])
        with pytest.raises(TushareNewsError):
            conn.fetch_latest(_END, _T0)  # start >= end
        with pytest.raises(TushareNewsError):
            _connector([_raw("", _T0)]).fetch_latest(_T0, _END)          # 空标题
        with pytest.raises(TushareNewsError):
            _connector([_raw("越界", datetime.datetime(2026, 8, 26))]).fetch_latest(_T0, _END)
        with pytest.raises(TushareNewsError):
            _connector([{"title": "无时间", "content": ""}]).fetch_latest(_T0, _END)
        with pytest.raises(TushareNewsError):
            _connector([_raw("坏内容", _T0, content=123)]).fetch_latest(_T0, _END)  # type: ignore[arg-type]

    def test_api_not_injected_fail_closed(self) -> None:
        conn = TushareNewsConnector(clock=lambda: _T0)
        with pytest.raises(TushareNewsError):
            conn.fetch_latest(_T0, _END)

    def test_ctor_invalid_args_raise(self) -> None:
        with pytest.raises(TushareNewsError):
            TushareNewsConnector(dedup_window_seconds=0)
        with pytest.raises(TushareNewsError):
            TushareNewsConnector(source="")


# ──────────────────────────────────────────────────────────────────────────────
# 回补区间完整性校验
# ──────────────────────────────────────────────────────────────────────────────


class TestBackfill:
    def test_backfill_complete(self) -> None:
        conn = _connector([_raw(f"新闻{i}", ts, f"n{i}")
                           for i, ts in enumerate((_T0, _T1, _T2))])
        report = conn.backfill(_T0, _T2 + datetime.timedelta(seconds=300))
        assert report.complete is True
        assert report.windows_expected == 3
        assert report.windows_covered == 3
        assert report.missing_windows == ()
        assert len(report.accepted) == 3

    def test_backfill_missing_windows_listed(self) -> None:
        conn = _connector([_raw("仅首尾", _T0, "n1")])
        end = _T2 + datetime.timedelta(seconds=300)
        report = conn.backfill(_T0, end)
        assert report.complete is False
        assert report.windows_expected == 3
        assert report.windows_covered == 1
        assert report.missing_windows == (_T1, _T2)  # 确定性升序

    def test_backfill_invalid_range_raises(self) -> None:
        conn = _connector([])
        with pytest.raises(TushareNewsError):
            conn.backfill(_END, _T0)


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_inputs_same_outputs(self) -> None:
        def _run() -> tuple:
            conn = _connector(
                [_raw("乙", _T1, "n2"), _raw("甲", _T0, "n1"), _raw("甲", _T0, "n1-dup")],
                gate=lambda item: item.title != "弃",
            )
            report = conn.fetch_latest(_T0, _END)
            backfill = conn.backfill(_T0, _T1 + datetime.timedelta(seconds=300))
            return (report, backfill, conn.seen_count())

        assert _run() == _run()
