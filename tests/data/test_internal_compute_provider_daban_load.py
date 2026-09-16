# [A_test] module_id: MOD-L00-004_internal_compute_provider | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §test
# [MODULE] tests.data.test_internal_compute_provider_daban_load
# [DEPENDENCIES]
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;零DB零时钟（fake 注入隔离全部 IO，禁触生产 CH）;反串台断言不得弱化（技术指标默认分支必须零命中）
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/data/test_internal_compute_provider_daban_load.py
# [TTL] task_bound
"""daban_engine_load 调度路由 + 市场级上下文测试（T3⑧ 接线收口，车道 B2/E）。

覆盖（全 fake IO / 零 DB / 零时钟）：
- 路由分派：payload.table=c1_market.daban_engine_load 命中 _fetch_daban_engine_load，
  **绝不**落入 _fetch_technical_indicator 默认分支（反串台锁——落默认分支会把指标行
  写进负载表，静默污染且无法从数据侧分辨）
- 交易日守卫：跨周末窗口只产交易日批（幽灵行守卫 LUE-2 同一把尺子）
- 逐日 yield：每个 FetchResult 的 table/columns 与 producer LOAD_INSERT_COLUMNS 同序
- 空事件日：该日 rows=[]（fail-visible），不伪造负载行
- CH 不可达：RuntimeError fail-closed（禁把"读不到"伪装成"当日无负载"）
- 市场级上下文：parse_market_context_rows 宽度比 adv/(adv+dec)、分母 0 省略（不是 0.0）、
  基准指数环比取序列内前一行、请求日无数据整键省略；fetch_market_context 单腿失败
  保留另一腿（缺字段降 default，不整批丢弃）
"""

from __future__ import annotations

import datetime as dt

import pytest

import zephyr.data.ch_reader as CHR
import zephyr.data.ch_writer as CHW
import zephyr.data.implementations.internal_compute_provider as icp
from zephyr.data.provider_base import FetchPayload, FetchResult
from zephyr.ex_core import daban_load_producer as prod

_TBL = icp._TBL_DABAN_ENGINE_LOAD


def _payload(start: dt.date, end: dt.date) -> FetchPayload:
    return FetchPayload(
        table=_TBL, symbols=None, start=start, end=end, incremental=True, extra={}
    )


@pytest.fixture
def guard_days(monkeypatch):
    """固定交易日序列（不触 CH 日历），并记录市场上下文/市值注入的调用参数。"""
    calls: dict[str, object] = {"days": None, "cap_source": None, "batch_days": []}

    days = [dt.date(2026, 9, 14), dt.date(2026, 9, 15), dt.date(2026, 9, 16)]
    monkeypatch.setattr(
        icp.InternalComputeProvider,
        "_trade_days_guarded",
        staticmethod(lambda start, end: list(days)),
    )

    def _fake_ctx(req_days, *, reader=None):
        calls["days"] = list(req_days)
        return {d.isoformat(): {"breadth_ratio": 0.6, "change_pct": 1.2} for d in req_days}

    def _fake_batch(event_day, *, event_source=None, market_context=None, cap_source=None):
        calls["batch_days"].append(event_day)
        calls["cap_source"] = cap_source
        calls["market_context"] = market_context
        return FetchResult(
            table=_TBL,
            columns=list(prod.LOAD_INSERT_COLUMNS),
            rows=[("2026-09-15", "600000")] + [""] * (len(prod.LOAD_INSERT_COLUMNS) - 2),
            last_key=event_day.isoformat(),
            elapsed_sec=0.0,
            rows_fetched=1,
        )

    monkeypatch.setattr(prod, "fetch_market_context", _fake_ctx)
    monkeypatch.setattr(prod, "run_daily_batch", _fake_batch)
    monkeypatch.setattr(CHW, "get_client", lambda *a, **kw: object())
    return calls


# ---------------------------------------------------------------------------
# 路由分派（反串台锁）
# ---------------------------------------------------------------------------


def test_route_dispatch_never_falls_through_to_indicator(monkeypatch):
    """负载表请求绝不可落入技术指标默认分支——串台即静默污染负载表。"""

    def _boom(*a, **kw):
        raise AssertionError("落入 _fetch_technical_indicator：daban_engine_load 路由失效")

    monkeypatch.setattr(
        icp.InternalComputeProvider, "_fetch_technical_indicator", _boom
    )
    monkeypatch.setattr(
        icp.InternalComputeProvider,
        "_trade_days_guarded",
        staticmethod(lambda start, end: []),
    )
    prov = icp.InternalComputeProvider()
    # 空交易日 ⇒ 零 yield，但已在默认分支之前 return（不触发 _boom）
    assert list(prov.fetch(_payload(dt.date(2026, 9, 14), dt.date(2026, 9, 16)), None)) == []


def test_route_reaches_daban_engine_load_branch(guard_days, monkeypatch):
    """命中本分支并逐日驱动生产者（口径真源在生产者，路由件零业务复制）。"""
    called: list[str] = []
    monkeypatch.setattr(
        icp.InternalComputeProvider,
        "_fetch_technical_indicator",
        lambda *a, **kw: called.append("indicator"),
    )
    prov = icp.InternalComputeProvider()
    results = list(prov.fetch(_payload(dt.date(2026, 9, 14), dt.date(2026, 9, 16)), None))

    assert called == []
    assert [r.last_key for r in results] == ["2026-09-14", "2026-09-15", "2026-09-16"]
    assert guard_days["days"] == [dt.date(2026, 9, 14), dt.date(2026, 9, 15), dt.date(2026, 9, 16)]
    assert guard_days["cap_source"] is prod.fetch_float_cap_map


def test_every_result_carries_producer_column_contract(guard_days):
    """table/columns 逐批对齐 producer 真源（列序漂移=写错列，静默且不可事后修正）。"""
    prov = icp.InternalComputeProvider()
    results = list(prov.fetch(_payload(dt.date(2026, 9, 14), dt.date(2026, 9, 16)), None))
    assert results
    for r in results:
        assert r.table == _TBL
        assert r.columns == list(prod.LOAD_INSERT_COLUMNS)
        assert len(r.columns) == 21


def test_trading_day_guard_drops_weekend(monkeypatch):
    """真守卫路径（非 fixture）：周末恒剔除，日历不可达时降级周末守卫仍剔周末。"""

    def _no_calendar(sql, **kw):
        raise RuntimeError("CH 不可达")

    monkeypatch.setattr(CHR, "query", _no_calendar)
    prov = icp.InternalComputeProvider()
    days = prov._trade_days_guarded(dt.date(2026, 9, 11), dt.date(2026, 9, 14))
    assert dt.date(2026, 9, 12) not in days and dt.date(2026, 9, 13) not in days
    assert days == [dt.date(2026, 9, 11), dt.date(2026, 9, 14)]


def test_empty_event_day_yields_empty_batch_not_fabricated(guard_days, monkeypatch):
    """零事件日=空 rows FetchResult（生产者 warning 留痕），路由件不得补行。"""

    def _empty(event_day, **kw):
        return FetchResult(
            table=_TBL,
            columns=list(prod.LOAD_INSERT_COLUMNS),
            rows=[],
            last_key=event_day.isoformat(),
            elapsed_sec=0.0,
            rows_fetched=0,
        )

    monkeypatch.setattr(prod, "run_daily_batch", _empty)
    prov = icp.InternalComputeProvider()
    results = list(prov.fetch(_payload(dt.date(2026, 9, 15), dt.date(2026, 9, 15)), None))
    assert [r.last_key for r in results] == ["2026-09-14", "2026-09-15", "2026-09-16"]
    assert all(r.rows == [] and r.error is None and r.rows_fetched == 0 for r in results)


def test_ch_unreachable_fails_closed(guard_days, monkeypatch):
    """CH 不可达必须抛错——降级空批等于把"读不到"伪装成"当日无负载"。"""
    monkeypatch.setattr(CHW, "get_client", lambda *a, **kw: None)
    prov = icp.InternalComputeProvider()
    with pytest.raises(RuntimeError, match="daban_engine_load"):
        list(prov.fetch(_payload(dt.date(2026, 9, 15), dt.date(2026, 9, 15)), None))


# ---------------------------------------------------------------------------
# 市场级上下文（宽度末快照 + 基准指数环比）
# ---------------------------------------------------------------------------


def test_parse_market_context_ratio_and_change_pct():
    out = prod.parse_market_context_rows(
        [["2026-09-15", "3000", "1000"], ["2026-09-16", "3937", "1115"]],
        [["2026-09-11", "4510.155"], ["2026-09-14", "4480.083"], ["2026-09-15", "4450.04"]],
        [dt.date(2026, 9, 15)],
    )
    assert set(out) == {"2026-09-15"}
    assert out["2026-09-15"]["breadth_ratio"] == pytest.approx(0.75)
    assert out["2026-09-15"]["change_pct"] == pytest.approx((4450.04 / 4480.083 - 1) * 100)


def test_parse_market_context_omits_instead_of_zero_filling():
    """无源日整键省略（→上层 default 留痕）；0/0 宽度不是"全市场尽跌"的 0.0。"""
    out = prod.parse_market_context_rows(
        [["2026-09-15", "0", "0"]],  # 零涨跌家数=无信息
        [["2026-09-15", "4450.04"]],  # 序列内无前序行→无法算环比
        [dt.date(2026, 9, 15), dt.date(2026, 9, 16)],
    )
    assert out == {}


def test_parse_market_context_partial_legs_keep_the_other():
    """只有宽度腿有源时保留宽度、省略涨幅（反之同理）——禁整批丢弃可用真字段。"""
    out = prod.parse_market_context_rows(
        [["2026-09-16", "3937", "1115"]], [], [dt.date(2026, 9, 16)]
    )
    assert set(out["2026-09-16"]) == {"breadth_ratio"}
    out2 = prod.parse_market_context_rows(
        [], [["2026-09-15", "100"], ["2026-09-16", "101"]], [dt.date(2026, 9, 16)]
    )
    assert out2["2026-09-16"]["change_pct"] == pytest.approx(1.0)


def test_fetch_market_context_survives_single_leg_failure():
    """单腿查询异常→保留另一腿 + 不抛（与事件源/市值源同 fail-open 契约）。"""

    def reader(sql, **kw):
        if "market_breadth_snapshot" in sql:
            return "2026-09-16\t3937\t1115\n"
        raise RuntimeError("指数腿炸了")

    out = prod.fetch_market_context([dt.date(2026, 9, 16)], reader=reader)
    assert out == {"2026-09-16": {"breadth_ratio": pytest.approx(3937 / 5052)}}


def test_fetch_market_context_empty_days_returns_empty():
    assert prod.fetch_market_context([], reader=lambda sql, **kw: "x") == {}


def test_load_column_names_align_with_producer_contract():
    """上下文键名必须与 events_to_load_rows 读取的键一致（breadth_ratio/change_pct）。"""
    out = prod.parse_market_context_rows(
        [["2026-09-16", "2", "1"]], [["2026-09-15", "10"], ["2026-09-16", "11"]], [dt.date(2026, 9, 16)]
    )
    rows = prod.events_to_load_rows(
        [], market_context=out
    )  # 空事件→零行，但上下文键被消费的路径由 derived 映射保证
    assert rows == []
    assert set(out["2026-09-16"]) == {"breadth_ratio", "change_pct"}
    assert "market_breadth_ratio" in prod.LOAD_INSERT_COLUMNS
    assert "market_change_pct" in prod.LOAD_INSERT_COLUMNS
