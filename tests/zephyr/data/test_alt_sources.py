# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler) | §alt-data
# [TTL] permanent
"""AkshareAltProvider + alt_source_bootstrap 单测——纯函数/路由/治理闭环（不依赖网络/CH，FAIL-FAST）。

另类数据第 1 批免注册直连（2026-09-12，docs/_working/2026-09-12-alt-data-handoff.md §8-1）。
akshare 接口经 sys.modules stub 注入（fetcher 函数内 import akshare）。
"""
from __future__ import annotations

import datetime
import sys
import types

import pandas as pd
import pytest

from zephyr.data.implementations.akshare_alt_provider import (
    _AKSHARE_ALT_CAPABILITIES,
    AkshareAltProvider,
    _norm_date,
    _to_float,
    _to_int,
)
from zephyr.data.policy_registry import SourcePolicy
from zephyr.data.provider_base import FetchPayload


# ---------- 纯函数 ----------

def test_norm_date_variants():
    assert _norm_date(datetime.date(2026, 9, 11)) == "2026-09-11"
    assert _norm_date("2026-09-11 15:00:00") == "2026-09-11"
    assert _norm_date("NaT") is None
    assert _norm_date("") is None
    assert _norm_date(None) is None
    ts = pd.Timestamp("2026-09-11 00:00:00")
    assert _norm_date(ts) == "2026-09-11"


def test_to_float_nan_and_garbage():
    assert _to_float("3.14") == pytest.approx(3.14)
    assert _to_float(float("nan")) is None  # NaN 防穿透 -> None（Nullable 语义）
    assert _to_float("-") is None
    assert _to_float(None) is None


def test_to_int_variants():
    assert _to_int("640.0") == 640
    assert _to_int(None) is None
    assert _to_int("abc") is None


# ---------- provider 声明与路由 ----------

def test_provider_meta_capabilities():
    caps = {c.capability_id for c in AkshareAltProvider.meta.capabilities}
    required = {"alt_stock_comment", "alt_shipping_index", "cb_premium_median",
                "alt_typhoon_track", "alt_typhoon_landfall_history", "alt_typhoon_names",
                "alt_sz_stat_monthly", "alt_sz_port_monthly", "alt_sz_house_daily",
                "alt_sz_weather_warning", "alt_sz_marine_forecast", "alt_sz_visibility",
                "alt_sz_air_quality_daily", "alt_sz_air_quality_region",
                "alt_sz_reservoir_station", "alt_sz_reservoir_rain_day",
                "alt_sz_reservoir_rain_month", "alt_sz_house_area",
                "alt_sz_house_listing", "alt_sz_house_presale",
                "alt_sz_market_subject", "alt_sz_stat_analysis", "alt_sz_enterprise_year"}
    assert required <= caps  # 子集断言：他会话扩容不碎我方测试
    assert "cb_premium_median" in _AKSHARE_ALT_CAPABILITIES
    assert "alt_sz_visibility" in _AKSHARE_ALT_CAPABILITIES
    assert "alt_sz_stat_analysis" in _AKSHARE_ALT_CAPABILITIES
    assert _AKSHARE_ALT_CAPABILITIES == caps


def _make_payload(cap: str, **kw) -> FetchPayload:
    return FetchPayload(
        table=kw.pop("table", "c1_market.alt_stock_comment"),
        symbols=None,
        start=kw.pop("start", datetime.date(2026, 9, 1)),
        end=kw.pop("end", datetime.date(2026, 9, 12)),
        incremental=kw.pop("incremental", True),
        extra={"capability": cap},
    )


def test_fetch_unknown_capability_yields_error():
    p = AkshareAltProvider()
    results = list(p.fetch(_make_payload("nope"), SourcePolicy()))
    assert len(results) == 1
    assert results[0].error and "unsupported capability" in results[0].error


# ---------- akshare stub 注入 ----------

@pytest.fixture()
def stub_akshare(monkeypatch):
    """函数内 `import akshare as ak` 的 stub 注入载体。"""

    def _install(**fns):
        mod = types.ModuleType("akshare")
        for name, fn in fns.items():
            setattr(mod, name, fn)
        monkeypatch.setitem(sys.modules, "akshare", mod)
        return mod

    return _install


def test_alt_stock_comment_snapshot(stub_akshare):
    df = pd.DataFrame(
        {
            "序号": [1, 2],
            "代码": ["000001", ""],  # 空代码行跳过
            "名称": ["平安银行", "垃圾行"],
            "主力成本": ["11.77", "3.07"],
            "机构参与度": [0.42, 0.35],
            "综合得分": [69.22, 56.72],
            "上升": [-341.0, 19.0],
            "目前排名": [640.0, 4181.0],
            "关注指数": ["90.8", "82.4"],
            "交易日": ["2026-09-11", "2026-09-11"],
        }
    )
    stub_akshare(stock_comment_em=lambda: df)
    p = AkshareAltProvider()
    results = list(p.fetch(_make_payload("alt_stock_comment", incremental=False), SourcePolicy()))
    assert len(results) == 1
    r = results[0]
    assert r.error is None
    assert r.last_key == "2026-09-11"
    assert len(r.rows) == 1  # 空代码行被滤
    row = r.rows[0]
    assert row[0] == "2026-09-11"  # trade_date 取接口列（PIT 锚）
    assert row[1] == "000001"
    assert row[6] == 640  # current_rank Int
    assert row[7] == pytest.approx(90.8)  # attention_index str->float
    assert r.columns[0] == "trade_date"


def test_alt_stock_comment_empty_df_yields_error(stub_akshare):
    stub_akshare(stock_comment_em=lambda: pd.DataFrame())
    p = AkshareAltProvider()
    r = list(p.fetch(_make_payload("alt_stock_comment"), SourcePolicy()))[0]
    assert r.error and "返回空" in r.error


def test_alt_shipping_merge_and_dedupe(stub_akshare):
    bdi = pd.DataFrame(
        {
            "日期": ["2026-09-10", "2026-09-11"],
            "最新值": ["3521", "3507"],
            "涨跌幅": [-2.73, -0.40],
        }
    )
    freight = pd.DataFrame(
        {
            "截止日期": ["2026-09-11", "2026-09-10"],
            "波罗的海好望角型船运价指数BCI": [2801.0, 2850.0],
            "灵便型船综合运价指数BHMI": [None, 900.0],  # None 值行跳过
            "波罗的海超级大灵便型船BSI指数": [1500.0, 1510.0],
            "波罗的海综合运价指数BDI": [9999.0, 9999.0],  # 双源重叠列弃用
            "HRCI国际集装箱租船指数": [1200.5, 1201.5],
            "油轮运价指数成品油运价指数BCTI": [1100.0, 1105.0],
            "油轮运价指数原油运价指数BDTI": [1300.0, 1302.0],
        }
    )
    stub_akshare(
        macro_shipping_bdi=lambda: bdi,
        macro_china_freight_index=lambda: freight,
    )
    p = AkshareAltProvider()
    payload = _make_payload(
        "alt_shipping_index",
        table="c1_market.alt_shipping_index",
        start=datetime.date(2026, 9, 10),
        end=datetime.date(2026, 9, 11),
    )
    r = list(p.fetch(payload, SourcePolicy()))[0]
    assert r.error is None
    codes = {row[1] for row in r.rows}
    assert codes == {"BDI", "BCI", "BHMI", "BSI", "HRCI", "BCTI", "BDTI"}
    # BDI 仅来自 macro_shipping_bdi（9999 弃用）
    bdi_rows = [row for row in r.rows if row[1] == "BDI"]
    assert {row[3] for row in bdi_rows} == {3521.0, 3507.0}
    assert bdi_rows[0][4] == pytest.approx(-2.73)  # change_pct 仅 BDI 源
    # 六指数行 change_pct=None、source 标记正确
    bci_rows = [row for row in r.rows if row[1] == "BCI"]
    assert bci_rows[0][4] is None
    assert bci_rows[0][5] == "macro_china_freight_index"
    # BHMI None 值行被滤（2026-09-11 无值、09-10 有值）
    assert {row[0] for row in r.rows if row[1] == "BHMI"} == {"2026-09-10"}
    # last_key = 全表最大日期
    assert r.last_key == "2026-09-11"


def test_alt_shipping_incremental_start_filter(stub_akshare):
    bdi = pd.DataFrame({"日期": ["2026-08-01", "2026-09-11"], "最新值": [3000, 3507], "涨跌幅": [1.0, -0.4]})
    stub_akshare(macro_shipping_bdi=lambda: bdi, macro_china_freight_index=lambda: pd.DataFrame())
    p = AkshareAltProvider()
    payload = _make_payload(
        "alt_shipping_index",
        table="c1_market.alt_shipping_index",
        start=datetime.date(2026, 9, 1),
        end=datetime.date(2026, 9, 12),
    )
    r = list(p.fetch(payload, SourcePolicy()))[0]
    assert [row[0] for row in r.rows] == ["2026-09-11"]  # start 之前被滤


def test_alt_shipping_full_refresh_ignores_start(stub_akshare):
    """全量模式（incremental=False）真全量：scheduler 传 start=月初也须拉全史。"""
    bdi = pd.DataFrame({"日期": ["1988-10-19", "2026-08-01", "2026-09-11"], "最新值": [1317, 3000, 3507], "涨跌幅": [None, 1.0, -0.4]})
    stub_akshare(macro_shipping_bdi=lambda: bdi, macro_china_freight_index=lambda: pd.DataFrame())
    p = AkshareAltProvider()
    payload = _make_payload(
        "alt_shipping_index",
        table="c1_market.alt_shipping_index",
        start=datetime.date(2026, 9, 1),
        end=datetime.date(2026, 9, 12),
        incremental=False,
    )
    r = list(p.fetch(payload, SourcePolicy()))[0]
    assert len(r.rows) == 3  # 1988 年行不被 start 滤掉
    assert r.rows[0][0] == "1988-10-19"


def test_alt_shipping_source_exception_yields_error(stub_akshare):
    def _boom():
        raise RuntimeError("connection reset")

    stub_akshare(macro_shipping_bdi=_boom, macro_china_freight_index=lambda: pd.DataFrame())
    p = AkshareAltProvider()
    r = list(
        p.fetch(
            _make_payload("alt_shipping_index", table="c1_market.alt_shipping_index"),
            SourcePolicy(),
        )
    )[0]
    assert r.error and "connection reset" in r.error


# ---------- 治理三件闭环（bootstrap） ----------

def test_bootstrap_triple_full_loop():
    from zephyr.alt_data.alt_data_catalog import CatalogLifecycle
    from zephyr.alt_data.alt_data_compliance_reviewer import SourceStatus
    from zephyr.alt_data.alt_source_bootstrap import ALT_SOURCES, build_governance_triple
    from zephyr.alt_data.alt_source_health_manager import HealthState

    catalog, reviewer, health = build_governance_triple()
    ids = {s.source_id for s in ALT_SOURCES}
    # 目录：全登记 + APPROVED
    assert {r.entry.source_id for r in catalog.list_by_state(CatalogLifecycle.APPROVED)} == ids
    assert all(catalog.get(sid).state is CatalogLifecycle.APPROVED for sid in ids)
    # 合规：全 APPROVED
    assert set(reviewer.sources()) == ids
    assert all(reviewer.status_of(sid) is SourceStatus.APPROVED for sid in ids)
    # 健康：全注册且初始 NORMAL
    assert set(health.sources()) == ids
    assert all(health.state_of(sid) is HealthState.NORMAL for sid in ids)


def test_bootstrap_record_outcome_and_evaluate():
    from zephyr.alt_data.alt_source_bootstrap import build_governance_triple, record_fetch_outcome
    from zephyr.alt_data.alt_source_health_manager import HealthState

    _, _, health = build_governance_triple()
    record_fetch_outcome(
        health,
        "alt_stock_comment",
        success=True,
        latency_seconds=2.5,
        data_ts=datetime.datetime.now(),  # 相对真实时钟取新鲜样本（避免硬编码时间戳随日期衰减）
    )
    report = health.evaluate("alt_stock_comment")
    assert health.state_of("alt_stock_comment") is HealthState.NORMAL
    assert report.score > 0.8


def test_bootstrap_fail_closed_on_bad_evidence(monkeypatch):
    """审查证据不齐 -> AltComplianceError（fail-closed，不放行半审状态）。"""
    from dataclasses import replace

    from zephyr.alt_data.alt_data_compliance_reviewer import AltComplianceError
    from zephyr.alt_data.alt_source_bootstrap import ALT_SOURCES, COMPLIANCE_CHECKLIST, build_governance_triple

    bad = replace(ALT_SOURCES[0], review_evidence={COMPLIANCE_CHECKLIST[0]: (True, "仅一项")})
    monkeypatch.setattr(
        "zephyr.alt_data.alt_source_bootstrap.ALT_SOURCES", (bad, ALT_SOURCES[1])
    )
    with pytest.raises(AltComplianceError):
        build_governance_triple()


# ---------- 台风路径（深圳开放数据平台 appKey 通道） ----------

def _typhoon_stub_row(keyid: int, crt: str = "2026-09-13 17:00:00") -> dict:
    return {
        "KEYID": str(keyid), "TCIDX": "2845", "TCNO": "0000", "CNAME": "南海低压",
        "ENAME": "(nameless)", "TCLEVEL": "TD", "ISSUEDATE": crt, "FORECASTDATE": crt,
        "INTERVALTIME": "0", "LONGITUDE": "106.9", "LATITUDE": "17.2",
        "AIRPRESSURE": "1006", "WIND": "12", "GUST": "0", "MOVESPEED": "12",
        "MOVEDIR": "W", "SIXRADII": "0", "SEVENRADII": "0", "EIGHTRADII": "0",
        "TENRADII": "0", "ISSUETYPE": "BABJ", "CRTTIME": crt,
    }


def test_typhoon_row_parse():
    from zephyr.data.implementations.akshare_alt_provider import AkshareAltProvider

    row = AkshareAltProvider._typhoon_row(_typhoon_stub_row(1371860533))
    assert row[0] == 1371860533          # keyid int
    assert row[3] == "南海低压"
    assert row[7] == "2026-09-13 17:00:00"  # forecast_ts 原文
    assert row[9] == pytest.approx(106.9)   # longitude
    assert row[22] == "2026-09-13"          # crt_date 派生
    assert AkshareAltProvider._typhoon_row({"FOO": 1}) is None  # 缺 KEYID 跳过


def test_typhoon_unwrap_defensive():
    from zephyr.data.implementations.akshare_alt_provider import AkshareAltProvider

    u = AkshareAltProvider._unwrap_sz_api
    assert u([{"KEYID": 1}]) == [{"KEYID": 1}]
    assert u({"result": [{"KEYID": 1}]}) == [{"KEYID": 1}]
    assert u({"result": {"rows": [{"KEYID": 1}]}}) == [{"KEYID": 1}]
    assert u({"errorCode": 1, "message": "x"}) == []


def test_typhoon_fetch_full_pagination(monkeypatch):
    """分页循环：满页继续、缺页即止；增量带 startDate；KEYID 幂等排序。"""
    from zephyr.data.implementations import akshare_alt_provider as mod

    calls = []

    def fake_get(self, url, params):
        calls.append(dict(params))
        if params["page"] == 1:
            return {"result": [_typhoon_stub_row(i) for i in range(10000)]}
        return {"result": [_typhoon_stub_row(10000)]}

    monkeypatch.setattr(mod, "get_secret_or_default", lambda *a, **k: "stub-key")
    monkeypatch.setattr(mod.AkshareAltProvider, "_sz_api_get", fake_get)
    p = mod.AkshareAltProvider()
    payload = _make_payload(
        "alt_typhoon_track",
        table="c1_market.alt_typhoon_track",
        start=datetime.date(2026, 9, 1),
        end=datetime.date(2026, 9, 14),
    )
    r = list(p.fetch(payload, SourcePolicy()))[0]
    assert r.error is None
    assert len(calls) == 2
    assert calls[0]["appKey"] == "stub-key"
    assert calls[0]["startDate"] == "20260901"   # 增量按入库日期
    assert calls[0]["rows"] == 10000
    keyids = [row[0] for row in r.rows]
    assert keyids == sorted(keyids)               # 排序确定性
    assert r.last_key == "2026-09-13"


def test_typhoon_fetch_error_code(monkeypatch):
    from zephyr.data.implementations import akshare_alt_provider as mod

    monkeypatch.setattr(mod, "get_secret_or_default", lambda *a, **k: "stub-key")
    monkeypatch.setattr(
        mod.AkshareAltProvider, "_sz_api_get",
        lambda self, url, params: {"errorCode": "10001", "message": "未经许可的证书，请先订阅接口"},
    )
    p = mod.AkshareAltProvider()
    r = list(p.fetch(_make_payload("alt_typhoon_track", table="c1_market.alt_typhoon_track"), SourcePolicy()))[0]
    assert r.error and "10001" in r.error and "订阅" in r.error


def test_sz_stat_monthly_fetch(monkeypatch):
    """统计月报 7 系列并拉：解析/归一化/series 标记。"""
    from zephyr.data.implementations import akshare_alt_provider as mod

    def fake_get(self, url, params):
        ctx = url.rsplit("/", 2)[0].rsplit("/", 1)[-1]
        return [{"NY": "201907", "ZBMC": "地区生产总值", "DW": "亿元",
                 "BENYUE": 2418.32, "BYZLJ": 15787.53, "LJTB": 7.4, "XH": "1"}]

    monkeypatch.setattr(mod, "get_secret_or_default", lambda *a, **k: "stub-key")
    monkeypatch.setattr(mod.AkshareAltProvider, "_sz_api_get", fake_get)
    p = mod.AkshareAltProvider()
    r = list(p.fetch(_make_payload("alt_sz_stat_monthly", table="c1_market.alt_sz_stat_monthly",
                                   incremental=False), SourcePolicy()))[0]
    assert r.error is None
    assert len(r.rows) == 18  # 18 系列各 1 行（7 首批 + 11 批2，批2 走新钥匙）
    series_set = {row[0] for row in r.rows}
    assert series_set == {s for s, _ in mod._SZ_STAT_SERIES_ALL}
    row = [x for x in r.rows if x[0] == "stat_gdp"][0]
    assert row[1] == "201907"
    assert row[3] == "地区生产总值"
    assert row[6] == pytest.approx(2418.32)  # BENYUE -> val_month
    assert row[7] == pytest.approx(15787.53)  # BYZLJ -> val_cum
    assert row[8] == pytest.approx(7.4)  # LJTB -> yoy_cum


def test_sz_warning_fetch_incremental(monkeypatch):
    from zephyr.data.implementations import akshare_alt_provider as mod

    captured = {}

    def fake_get(self, url, params):
        captured["startDate"] = params.get("startDate")
        return [{"RECID": 19148, "KEYID": 1921, "TNUMBER": 577, "SIGNALTYPE": "大风",
                 "SIGNALLEVEL": "蓝色", "ISSUESTATE": "发布", "DISTRICT": "南山区",
                 "ISSUECONTENT": "【深圳市大风蓝色预警】...", "ISSUETIME": "2012-12-23 03:50:00",
                 "CRTTIME": "2012-12-23 03:49:51", "UNDERWRITER": "", "AUTOSENTFLAG": 1,
                 "AUTOSENTCOUNT": 0, "TRACEFLAG": 0, "TRACOUNT": 0, "SYNC_ROWNUM": "AA"}]

    monkeypatch.setattr(mod, "get_secret_or_default", lambda *a, **k: "stub-key")
    monkeypatch.setattr(mod.AkshareAltProvider, "_sz_api_get", fake_get)
    p = mod.AkshareAltProvider()
    r = list(p.fetch(_make_payload("alt_sz_weather_warning", table="c1_market.alt_sz_weather_warning",
                                   start=datetime.date(2026, 9, 1)), SourcePolicy()))[0]
    assert r.error is None
    assert captured["startDate"] == "20260901"
    assert r.rows[0][0] == 19148
    assert r.rows[0][3] == "大风"
    assert r.rows[0][10] == "2012-12-23"


def test_sz_error_passthrough(monkeypatch):
    from zephyr.data.implementations import akshare_alt_provider as mod

    monkeypatch.setattr(mod, "get_secret_or_default", lambda *a, **k: "stub-key")
    monkeypatch.setattr(
        mod.AkshareAltProvider, "_sz_api_get",
        lambda self, url, params: {"errorCode": "10001", "message": "未经许可的证书，请先订阅接口"},
    )
    p = mod.AkshareAltProvider()
    r = list(p.fetch(_make_payload("alt_sz_marine_forecast", table="c1_market.alt_sz_marine_forecast",
                                   incremental=False), SourcePolicy()))[0]
    assert r.error and "10001" in r.error


# ---------- 能见度探测（服务 1580458478，无过滤参数大表） ----------

def _visibility_stub(i: int) -> dict:
    """能见度行构造器：i 递增对应时间递增（分钟级）。"""
    day = 10 + i // 1440
    minute = i % 1440
    return {"OBTID": f"G{i % 8:04d}", "OBTNAME": f"站{i % 8}",
            "DDATETIME": f"2026-09-{day:02d} {minute // 60:02d}:{minute % 60:02d}:00",
            "V": 20000.0 + i, "V10M": 19000.0 + i, "MINV": 18000.0 + i, "MINVTIME": minute % 60}


def test_visibility_row_parse():
    row = AkshareAltProvider._visibility_row(_visibility_stub(0))
    assert row[0] == "G0000"          # obtid
    assert row[3] == "2026-09-10"     # ddate 派生
    assert row[4] == pytest.approx(20000.0)
    assert row[7] == 0                # minvtime int
    assert AkshareAltProvider._visibility_row({"FOO": 1}) is None  # 缺 OBTID/DDATETIME 跳过


def test_visibility_incremental_binary_search(monkeypatch):
    """无过滤大表增量：二分定位起始页→从定位页翻到尾→越窗边界剔除。"""
    from zephyr.data.implementations import akshare_alt_provider as mod

    total = 25000  # 3 页（页大小 10000）
    pages = {
        1: [_visibility_stub(i) for i in range(0, 10000)],
        2: [_visibility_stub(i) for i in range(10000, 20000)],
        3: [_visibility_stub(i) for i in range(20000, 25000)],
    }
    calls = []

    def fake_get(self, url, params):
        calls.append(dict(params))
        if "page" in params and params.get("rows") == 1:
            # _sz_get_total 探测页
            return {"total": total, "data": [_visibility_stub(0)]}
        return {"data": pages[params["page"]]}

    monkeypatch.setattr(mod, "get_secret_or_default", lambda *a, **k: "stub-key")
    monkeypatch.setattr(mod.AkshareAltProvider, "_sz_api_get", fake_get)
    # 二分只探首页/尾页即退出：首页首行 2026-09-10 < 目标 09-11，尾页首行 09-24 >= 目标
    monkeypatch.setattr(mod.AkshareAltProvider, "_sz_find_start_page",
                        lambda self, policy, ctx, tot, target: 2)
    p = mod.AkshareAltProvider()
    r = list(p.fetch(_make_payload("alt_sz_visibility", table="c1_market.alt_sz_visibility",
                                   start=datetime.date(2026, 9, 11)), SourcePolicy()))[0]
    assert r.error is None
    assert r.last_key == "2026-09-27"          # 显式取日期列最大值
    ddates = [row[3] for row in r.rows]
    assert all(d >= "2026-09-11" for d in ddates)  # 越窗边界剔除
    assert len(r.rows) == 15000               # 页 2 全部 + 页 3 全部（桩日期均 ≥ 09-11）


def test_visibility_full_refresh_over_limit(monkeypatch):
    """全量模式超页数天花板：fail-visible 拒绝盲扫（回补纪律入码）。"""
    from zephyr.data.implementations import akshare_alt_provider as mod

    monkeypatch.setattr(mod, "get_secret_or_default", lambda *a, **k: "stub-key")
    monkeypatch.setattr(
        mod.AkshareAltProvider, "_sz_api_get",
        lambda self, url, params: {"total": mod._SZ_VISIBILITY_FULL_PAGE_LIMIT * mod._SZ_OPEN_PAGE_SIZE + 1,
                                   "data": [_visibility_stub(0)]},
    )
    p = mod.AkshareAltProvider()
    r = list(p.fetch(_make_payload("alt_sz_visibility", table="c1_market.alt_sz_visibility",
                                   incremental=False), SourcePolicy()))[0]
    assert r.error and "报批" in r.error
