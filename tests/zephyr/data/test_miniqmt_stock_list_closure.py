# [ALGO_FLOW] #209④ stock_list 退市闭合测试：板块全量刷新→CH 有效快照对账→
# [ALGO_FLOW] 消失标的凭 ExpireDate 证据产出 list_status='退市'+valid_to 闭合批
# [ALGO_FLOW] 三重护栏：清单完整性下限/消失数阈值/逐标的证据，中止不影响主批
# [MODULE] tests.zephyr.data.test_miniqmt_stock_list_closure
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.miniqmt_provider
# [TESTS] 本文件
# [TTL] permanent
"""#209④ miniqmt stock_list 全量刷新退市闭合单元测试（xtquant/ch_reader 全 mock，不触网不触库）。

背景：get_stock_list_in_sector('沪深A股') 只返回在市标的，退市股从 universe
静默消失，原实现不闭合（stale '上市' 快照最长挂 1 个月等 akshare 月度任务）。
修复：刷新后对账 CH valid_to IS NULL 快照，消失标的凭 ExpireDate 证据闭合。
"""
from __future__ import annotations

import datetime
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.zephyr.data.implementations import miniqmt_provider as mq_mod
from src.zephyr.data.implementations.miniqmt_provider import MiniQmtIngestProvider
from src.zephyr.data.provider_base import FetchPayload

D = datetime.date

# 在市 2 只（板块返回）+ 退市候选 1 只（仅存在于 CH 有效快照）
_SECTOR = ["600000.SH", "000001.SZ"]
_ACTIVE_TSV = (
    "600000.SH\t600000\t浦发银行\t银行\t1999-11-10\t1970-01-01\n"
    "000001.SZ\t000001\t平安银行\t银行\t1991-04-03\t1970-01-01\n"
    "600001.SH\t600001\t邯郸钢铁\t钢铁\t1998-01-22\t1970-01-01\n"
)


def _wire(monkeypatch, sector=None, details=None, active_tsv=_ACTIVE_TSV,
          active_exc=None, full_min=2, closure_max_abs=None):
    """构造 provider + xtquant/ch_reader mock。

    sector: 板块接口返回的在市标的列表；details: {stock_code: dict|Exception}；
    active_tsv: CH stock_list 有效快照 TSV；active_exc: 查 CH 抛异常；
    full_min: 覆写 _STOCK_LIST_FULL_MIN 护栏（小样本测试用）。
    """
    mock_xtquant = MagicMock()
    mock_xtdata = mock_xtquant.xtdata
    for fn_name in ("get_stock_list_in_sector", "get_instrument_detail"):
        getattr(mock_xtdata, fn_name).__name__ = fn_name
    monkeypatch.setitem(sys.modules, "xtquant", mock_xtquant)
    monkeypatch.setitem(sys.modules, "xtquant.xtdata", mock_xtdata)

    monkeypatch.setattr(mq_mod, "_STOCK_LIST_FULL_MIN", full_min)
    if closure_max_abs is not None:
        monkeypatch.setattr(mq_mod, "_STOCK_LIST_CLOSURE_MAX_ABS", closure_max_abs)

    def fake_query(sql, timeout=None):
        if active_exc is not None:
            raise active_exc
        return active_tsv

    monkeypatch.setattr(mq_mod, "ch_reader", SimpleNamespace(query=fake_query))

    p = MiniQmtIngestProvider()
    details = details or {}

    def fake_call(fn, policy, *a, **kw):
        fn_name = getattr(fn, "__name__", "")
        if fn_name == "get_stock_list_in_sector":
            return list(sector if sector is not None else _SECTOR)
        if fn_name == "get_instrument_detail":
            d = details.get(a[0], {})
            if isinstance(d, Exception):
                raise d
            return d
        raise AssertionError(f"意外调用: {fn_name}")

    monkeypatch.setattr(p, "_call_with_policy", fake_call)
    return p


def _run(p):
    payload = FetchPayload(
        table="", symbols=None, start=D(2026, 8, 20), end=D(2026, 8, 20),
        incremental=False, extra={},
    )
    return list(p._fetch_stock_list(payload, MagicMock()))


class TestDelistedClosure:
    def test_closure_rows_emitted(self, monkeypatch):
        """消失标的 600001.SH 凭 ExpireDate=20260801 闭合为退市批（第二批）。"""
        p = _wire(
            monkeypatch,
            details={
                "600000.SH": {"InstrumentName": "浦发银行", "ExchangeID": "SH", "OpenDate": "19991110"},
                "000001.SZ": {"InstrumentName": "平安银行", "ExchangeID": "SZ", "OpenDate": "19910403"},
                "600001.SH": {"InstrumentName": "邯郸钢铁", "ExchangeID": "SH",
                              "OpenDate": "19980122", "ExpireDate": "20260801"},
            },
        )
        results = _run(p)
        assert len(results) == 2, "主批 + 退市闭合批"
        main, closure = results
        assert main.error is None
        assert len(main.rows) == 2  # 在市 2 只正常主批
        assert closure.columns == mq_mod._STOCK_LIST_CLOSURE_COLUMNS
        assert len(closure.rows) == 1
        row = closure.rows[0]
        assert row[0] == "600001.SH"
        assert row[1] == "600001"
        assert row[2] == "邯郸钢铁"  # name 从 CH 快照结转
        assert row[4] == "钢铁"     # industry 结转
        assert row[10] == "退市"    # list_status
        assert row[11] == "1998-01-22"  # list_date 结转
        assert row[12] == "2026-08-01"  # delist_date=ExpireDate
        assert row[16] == "2026-08-01"  # valid_to=delist_date（SCD-2 终止）

    def test_no_expire_evidence_no_closure(self, monkeypatch):
        """消失标的无 ExpireDate（detail 无该键）→ 不闭合，仅主批。"""
        p = _wire(monkeypatch, details={"600001.SH": {"InstrumentName": "邯郸钢铁"}})
        results = _run(p)
        assert len(results) == 1

    def test_detail_exception_no_closure(self, monkeypatch):
        """消失标的 detail 查询异常 → 无证据不闭合。"""
        p = _wire(monkeypatch, details={"600001.SH": ConnectionError("qmt lost")})
        results = _run(p)
        assert len(results) == 1

    def test_expiredate_malformed_skipped(self, monkeypatch):
        """ExpireDate 脏值（长度不足/非数字）→ 不闭合。"""
        p = _wire(monkeypatch, details={"600001.SH": {"ExpireDate": "2026"}})
        results = _run(p)
        assert len(results) == 1

    def test_no_missing_no_closure(self, monkeypatch):
        """CH 有效快照与板块清单一致 → 无闭合批。"""
        p = _wire(
            monkeypatch,
            active_tsv=(
                "600000.SH\t600000\t浦发银行\t银行\t1999-11-10\t1970-01-01\n"
                "000001.SZ\t000001\t平安银行\t银行\t1991-04-03\t1970-01-01\n"
            ),
        )
        results = _run(p)
        assert len(results) == 1

    def test_sector_list_incomplete_aborts(self, monkeypatch):
        """护栏1：板块清单 < _STOCK_LIST_FULL_MIN（默认 3000）→ 中止闭合，主批照常。"""
        p = _wire(monkeypatch, full_min=3000)
        results = _run(p)
        assert len(results) == 1
        assert results[0].error is None
        assert len(results[0].rows) == 2

    def test_disappeared_over_threshold_aborts(self, monkeypatch):
        """护栏2：消失数超 max(绝对上限, 5%×快照) → 中止闭合（疑似板块数据异常）。"""
        active = _ACTIVE_TSV + "600002.SH\t600002\t齐鲁石化\t石化\t1998-04-08\t1970-01-01\n"
        p = _wire(monkeypatch, active_tsv=active, closure_max_abs=1)
        # 消失 2 只 > max(1, int(4*0.05)=0) = 1 → 中止
        results = _run(p)
        assert len(results) == 1

    def test_active_query_failure_aborts(self, monkeypatch):
        """CH 基线查询失败 → 无基线中止闭合（fail-closed），主批不受影响。"""
        p = _wire(monkeypatch, active_exc=ConnectionError("CH unreachable"))
        results = _run(p)
        assert len(results) == 1
        assert results[0].error is None

    def test_sector_fetch_failure_no_closure(self, monkeypatch):
        """板块接口失败 → 原 error 路径，不触发闭合。"""
        mock_xtquant = MagicMock()
        mock_xtdata = mock_xtquant.xtdata
        mock_xtdata.get_stock_list_in_sector.__name__ = "get_stock_list_in_sector"
        monkeypatch.setitem(sys.modules, "xtquant", mock_xtquant)
        monkeypatch.setitem(sys.modules, "xtquant.xtdata", mock_xtdata)
        p = MiniQmtIngestProvider()

        def fake_call(fn, policy, *a, **kw):
            raise ConnectionError("qmt lost")

        monkeypatch.setattr(p, "_call_with_policy", fake_call)
        results = _run(p)
        assert len(results) == 1
        assert results[0].error is not None
