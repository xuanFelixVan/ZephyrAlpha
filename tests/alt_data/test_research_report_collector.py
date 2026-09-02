# [BLUEPRINT] MOD-ALT-009 | docs/03_modules/_domain_alt_data/research_report_collector/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ALT-009 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.alt_data.test_research_report_collector
# [TESTS] src/zephyr/alt_data/research_report_collector.py
"""MOD-ALT-009 单元测试：research_report_collector 研报采集器。

蓝图验收（B1-00628/CAND-TESTA-012，C2 72）：
研报元数据采集（标题/评级/目标价/机构/日期校验）+ 标的强制映射（未注入
Fail-Closed/未映射跳过）+ (symbol, org) 快照 diff 评级变动事件（乱序旧文
不撼动快照）+ 事件入总线回调（异常不阻断内部留痕）+ body_ref 引用接口。
fetch_api/linker/事件总线/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.alt_data.research_report_collector",
    reason="research_report_collector not importable",
)

from zephyr.alt_data.research_report_collector import (  # noqa: E402
    ResearchReport,
    ResearchReportCollector,
    ResearchReportError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_D0 = datetime.date(2026, 8, 26)

_SYMBOL_MAP = {"浦发银行": "600000", "贵州茅台": "600519"}


def _linker(raw: str):
    return _SYMBOL_MAP.get(raw)


def _report(
    report_id: str = "r1",
    rating: str = "买入",
    org: str = "中信",
    raw_symbol: str = "浦发银行",
    publish_date: datetime.date = _D0,
    target_price: float | None = 12.5,
    title: str = "深度报告",
    body_ref: str | None = None,
) -> ResearchReport:
    return ResearchReport(
        report_id=report_id,
        title=title,
        rating=rating,
        target_price=target_price,
        org=org,
        publish_date=publish_date,
        raw_symbol=raw_symbol,
        body_ref=body_ref if body_ref is not None else f"body://{report_id}",
    )


def _collector(batch=(), **kw) -> ResearchReportCollector:
    kw.setdefault("clock", lambda: _T0)
    kw.setdefault("fetch_api", lambda: list(batch))
    kw.setdefault("symbol_linker", _linker)
    return ResearchReportCollector(**kw)


# ──────────────────────────────────────────────────────────────────────────────
# 采集
# ──────────────────────────────────────────────────────────────────────────────


class TestCollect:
    def test_collect_ok(self) -> None:
        col = _collector(
            [
                _report("r2", publish_date=_D0 + datetime.timedelta(days=1)),
                _report("r1", publish_date=_D0),
            ]
        )
        assert col.collect() == 2
        reports = col.reports()
        assert [c.report.report_id for c in reports] == ["r1", "r2"]  # 确定性排序
        assert reports[0].symbol == "600000"  # 标的映射后落库
        assert reports[0].collected_at == _T0
        assert col.body_ref_of("r1") == "body://r1"

    def test_collect_missing_injections_fail_closed(self) -> None:
        with pytest.raises(ResearchReportError):
            _collector(fetch_api=None).collect()  # fetch_api 未注入
        with pytest.raises(ResearchReportError):
            _collector(symbol_linker=None).collect()  # symbol_linker 未注入

    def test_fetch_errors_raise(self) -> None:
        def _boom():
            raise RuntimeError("api down")

        with pytest.raises(ResearchReportError):
            _collector(fetch_api=_boom).collect()  # 抓取异常包装
        with pytest.raises(ResearchReportError):
            _collector(fetch_api=lambda: {"not": "list"}).collect()  # 返回类型非法

    def test_bad_item_type_raises(self) -> None:
        col = _collector([{"report_id": "r1"}])
        with pytest.raises(ResearchReportError):
            col.collect()

    def test_invalid_fields_raise(self) -> None:
        base = dict(report_id="r1", rating="买入", org="中信", raw_symbol="浦发银行")
        bad_cases = [
            dict(base, report_id=""),
            dict(base, title=""),
            dict(base, rating=""),
            dict(base, org=""),
            dict(base, raw_symbol=""),
            dict(base, body_ref=""),
            dict(base, publish_date="2026-08-26"),
            dict(base, target_price=float("nan")),
            dict(base, target_price=-3.0),
            dict(base, target_price=0.0),
            dict(base, target_price=True),
        ]
        for kw in bad_cases:
            col = _collector([_report(**{k: v for k, v in kw.items() if v is not None or k == "target_price"})])
            with pytest.raises(ResearchReportError):
                col.collect()

    def test_dedup_idempotent(self) -> None:
        col = _collector([_report("r1"), _report("r1")])
        assert col.collect() == 1  # 批内去重
        assert col.collect() == 0  # 跨批幂等
        assert len(col.reports()) == 1

    def test_unmapped_symbol_skipped(self) -> None:
        col = _collector([_report("r1", raw_symbol="未知公司"), _report("r2")])
        assert col.collect() == 1  # 未映射跳过留痕不落库
        assert [c.report.report_id for c in col.reports()] == ["r2"]

    def test_linker_exception_wrapped(self) -> None:
        def _boom(raw):
            raise ValueError("linker down")

        col = _collector([_report()], symbol_linker=_boom)
        with pytest.raises(ResearchReportError):
            col.collect()


# ──────────────────────────────────────────────────────────────────────────────
# 评级变动快照 diff
# ──────────────────────────────────────────────────────────────────────────────


class TestRatingDiff:
    def test_first_report_no_event(self) -> None:
        bus: list = []
        col = _collector([_report()], event_bus=bus.append)
        col.collect()
        assert col.events() == ()
        assert bus == []
        assert col.latest_rating("600000", "中信") == "买入"

    def test_rating_change_event_to_bus(self) -> None:
        bus: list = []
        col = _collector(event_bus=bus.append)
        col._fetch_api = lambda: [_report("r1", rating="买入", publish_date=_D0)]
        col.collect()
        col._fetch_api = lambda: [
            _report("r2", rating="减持", publish_date=_D0 + datetime.timedelta(days=7)),
        ]
        col.collect()
        events = col.events()
        assert len(events) == 1
        ev = events[0]
        assert ev.symbol == "600000" and ev.org == "中信"
        assert (ev.previous_rating, ev.current_rating) == ("买入", "减持")
        assert (ev.previous_report_id, ev.current_report_id) == ("r1", "r2")
        assert ev.detected_at == _T0
        assert bus == [ev]  # 入事件总线回调
        assert col.latest_rating("600000", "中信") == "减持"

    def test_same_rating_no_event(self) -> None:
        col = _collector()
        col._fetch_api = lambda: [_report("r1", publish_date=_D0)]
        col.collect()
        col._fetch_api = lambda: [
            _report("r2", publish_date=_D0 + datetime.timedelta(days=1)),
        ]
        col.collect()
        assert col.events() == ()

    def test_out_of_order_report_ignored(self) -> None:
        col = _collector()
        col._fetch_api = lambda: [_report("r_new", rating="买入", publish_date=_D0)]
        col.collect()
        col._fetch_api = lambda: [
            _report("r_old", rating="卖出", publish_date=_D0 - datetime.timedelta(days=30)),
        ]
        col.collect()
        assert col.events() == ()  # 乱序旧文不出事件
        assert col.latest_rating("600000", "中信") == "买入"  # 快照不被撼动
        assert len(col.reports()) == 2  # 旧文仍落库可查

    def test_event_ordering_deterministic(self) -> None:
        # 乱序投喂：d3 卖出 / d1 中性 / d2 买入 → 事件按 (date, id) 序检出
        col = _collector(
            [
                _report("r3", rating="卖出", publish_date=_D0 + datetime.timedelta(days=2)),
                _report("r1", rating="中性", publish_date=_D0),
                _report("r2", rating="买入", publish_date=_D0 + datetime.timedelta(days=1)),
            ]
        )
        col.collect()
        transitions = [(e.previous_rating, e.current_rating) for e in col.events()]
        assert transitions == [("中性", "买入"), ("买入", "卖出")]

    def test_event_bus_exception_not_blocking(self) -> None:
        def _boom(_ev):
            raise RuntimeError("bus down")

        col = _collector(event_bus=_boom)
        col._fetch_api = lambda: [_report("r1", publish_date=_D0)]
        col.collect()
        col._fetch_api = lambda: [
            _report("r2", rating="减持", publish_date=_D0 + datetime.timedelta(days=1)),
        ]
        assert col.collect() == 1  # 总线异常不阻断
        assert len(col.events()) == 1  # 内部留痕不丢

    def test_latest_rating_none_when_empty(self) -> None:
        col = _collector()
        assert col.latest_rating("600000", "中信") is None


# ──────────────────────────────────────────────────────────────────────────────
# 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_reports_symbol_filter_sorted(self) -> None:
        col = _collector(
            [
                _report("r2", raw_symbol="贵州茅台", publish_date=_D0 + datetime.timedelta(days=1)),
                _report("r1", publish_date=_D0),
                _report("r3", raw_symbol="贵州茅台", publish_date=_D0),
            ]
        )
        col.collect()
        maotai = col.reports(symbol="600519")
        assert [c.report.report_id for c in maotai] == ["r3", "r2"]
        assert [c.report.report_id for c in col.reports()] == ["r1", "r3", "r2"]

    def test_body_ref_unknown_raises(self) -> None:
        col = _collector()
        with pytest.raises(ResearchReportError):
            col.body_ref_of("ghost")

    def test_cross_batch_event_only_once(self) -> None:
        col = _collector()
        col._fetch_api = lambda: [_report("r1", publish_date=_D0)]
        col.collect()
        col._fetch_api = lambda: [
            _report("r1"),
            _report("r2", rating="增持", publish_date=_D0 + datetime.timedelta(days=1)),
        ]
        assert col.collect() == 1  # r1 跨批幂等
        assert len(col.events()) == 1  # 变动事件不重复出
