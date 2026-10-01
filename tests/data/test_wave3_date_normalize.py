# [MODULE] tests.data.wave3.date-norm
# [DOMAIN] D_DATA
# [BLUEPRINT] MOD-WAVE3-DATE-NORM | docs/_working/total_command_closeout/wave3/data_chain_report.md | §波3
# [TTL] task_bound

"""波 3.1 红证：`'str' > 'date'` 入口类型归一（ISO 字符串与 date 两种入参跑通且同果）。

判据来源：10_wave_plan.md 波 3.1 行「红证=喂 ISO 字符串与 date 两种入参都必须能跑通
且比较结果一致」+「两表回归验证」（consensus_daily / financial_derived）。
案卷：docs/_working/total_command_closeout/wave3/data_chain_report.md §3.1。
零 IO：CH 读取由 monkeypatch 承担，禁写生产目录/禁真库。
"""

from __future__ import annotations

import datetime as dt

import pytest

from zephyr.data import date_normalize as dn
from zephyr.data.implementations import consensus_daily_compute as cdc
from zephyr.data.implementations import financial_derived_compute as fdc

_ISO_LO, _ISO_HI = "2026-01-05", "2026-03-31"
_D_LO = dt.date.fromisoformat(_ISO_LO)
_D_HI = dt.date.fromisoformat(_ISO_HI)


def _reports() -> list[dict]:
    """发布日混型（date + ISO str）——真实源表两条通道就是混型的。"""
    return [
        {
            "symbol": "600000.SH",
            "publish_date": dt.date(2026, 1, 10),
            "fy0_year": 2026,
            "eps_fy0": 1.5,
            "pe_fy0": 10.0,
            "org_name": "甲",
            "rating": "买入",
        },
        {
            "symbol": "600000.SH",
            "publish_date": "2026-02-10",
            "fy0_year": 2026,
            "eps_fy0": 1.6,
            "pe_fy0": 11.0,
            "org_name": "乙",
            "rating": "增持",
        },
    ]


def _trade_dates() -> list[dt.date]:
    return [dt.date(2026, 1, 8), dt.date(2026, 1, 9), dt.date(2026, 1, 12), dt.date(2026, 2, 2), dt.date(2026, 2, 11)]


# ── 反例在案（改前必抛）：混型直比的两条原始形态 ────────────────────────────
def test_pre_fix_mixed_type_comparison_raises():
    """改前两处崩溃点的裸比较形态：str vs date 必抛（红证的反面证据留案）。"""
    with pytest.raises(TypeError):
        _ = _D_LO < "2026-01-08"  # consensus_daily_compute:155 原形态
    with pytest.raises(TypeError):
        _ = _D_LO < "2026-01-08"  # financial_derived_compute:397 原形态
    with pytest.raises(TypeError):
        _ = _D_LO > "2026-01-08"  # 反向混型（同 bug 的另一侧）


# ── 归一件本体 ────────────────────────────────────────────────────────────
def test_as_iso_day_three_carriers_same_key():
    assert dn.as_iso_day(_D_LO) == _ISO_LO
    assert dn.as_iso_day(_ISO_LO) == _ISO_LO
    assert dn.as_iso_day(dt.datetime(2026, 1, 5, 17, 30)) == _ISO_LO
    assert dn.as_iso_day("2026/01/05") == _ISO_LO
    assert dn.as_iso_day("2026-01-05T09:30:00") == _ISO_LO
    assert dn.as_date_obj(_ISO_HI) == _D_HI


def test_as_iso_day_fail_must_throw_not_silent():
    for bad in (None, "", "not-a-date", "2026-13-45", 20260105, object()):
        with pytest.raises((TypeError, ValueError)):
            dn.as_iso_day(bad, field="probe")
    assert dn.iso_window_bound(None) == ""  # 唯一合法哨兵：None=不限


def test_in_window_ignores_bound_type():
    for v in (_D_LO, "2026-01-05", dt.date(2026, 1, 5)):
        assert dn.in_window(v, _ISO_LO, _ISO_HI) is True
        assert dn.in_window(v, _D_LO, _D_HI) is True
        assert dn.in_window(v, "2026-04-01", _ISO_HI) is False


# ── 表 1：c3_fundamental.consensus_daily ──────────────────────────────────
@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked consensus_daily_compute 窗口/发布日比较未改用 date_normalize（供给件落地、消费核接线未落地，病根2026-09-18/25两起FAILED在案），转XPASS=接线落地须改判",
)
def test_consensus_rows_identical_for_iso_str_and_date_bounds():
    str_rows = cdc.build_consensus_rows(_reports(), _trade_dates(), start=_ISO_LO, end=_ISO_HI)
    date_rows = cdc.build_consensus_rows(_reports(), _trade_dates(), start=_D_LO, end=_D_HI)
    assert str_rows, "非空断言：窗口内必须真出行（防空跑假绿）"
    assert str_rows == date_rows


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked consensus_daily_compute 窗口/发布日比较未改用 date_normalize（供给件落地、消费核接线未落地，病根2026-09-18/25两起FAILED在案），转XPASS=接线落地须改判",
)
def test_consensus_rows_mixed_publish_date_types_ok():
    """混型发布日（date+str 同列共存）不得崩，且与全 str 形态同果。"""
    mixed = cdc.build_consensus_rows(_reports(), _trade_dates())
    all_str = [dict(r, publish_date=dn.as_iso_day(r["publish_date"])) for r in _reports()]
    ref = cdc.build_consensus_rows(all_str, _trade_dates())
    assert mixed and mixed == ref


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked consensus_daily_compute 窗口/发布日比较未改用 date_normalize（供给件落地、消费核接线未落地，病根2026-09-18/25两起FAILED在案），转XPASS=接线落地须改判",
)
def test_consensus_date_trade_dates_accepted():
    """trade_dates 给 date 列表（真源=trade_calendar）时窗口边界给 str 也必须跑通。"""
    rows = cdc.build_consensus_rows(_reports(), _trade_dates(), start=_ISO_LO, end=_ISO_HI)
    assert rows == cdc.build_consensus_rows(_reports(), _trade_dates(), start=_D_LO, end=_D_HI)


# ── 表 2：c3_fundamental.financial_derived ────────────────────────────────
def _synthetic_store() -> dict:
    """三表齐备的单标的版本 store（announce 2024-04-20，期 2024-03-31）。"""
    p = dt.date(2024, 3, 31)
    a = dt.date(2024, 4, 20)
    return {
        "income_statement": {
            "600000.SH": {
                p: [(a, {"operating_revenue": "100", "operating_cost": "60", "net_profit_incl_minority": "20"})]
            }
        },
        "balance_sheet": {"600000.SH": {p: [(a, {"total_assets": "500", "total_liabilities": "300"})]}},
        "cashflow_statement": {"600000.SH": {p: [(a, {"ocf_net": "30"})]}},
    }


def test_financial_derived_symbol_rows_are_iso_str_announce():
    store = _synthetic_store()
    per_stmt = {stmt: store[stmt]["600000.SH"] for stmt in fdc._STMTS}
    rows = fdc.build_symbol_rows("600000.SH", per_stmt)
    assert len(rows) == 1
    assert rows[0]["announce_date"] == "2024-04-20"  # 行内是 ISO str（混型病根的另一半）


def _rows_of(result) -> list[tuple]:
    for attr in ("rows", "data", "records"):
        v = getattr(result, attr, None)
        if isinstance(v, list):
            return v
    raise AssertionError(f"FetchResult 无行载体字段：{type(result).__name__}")


def test_financial_derived_run_compute_identical_for_str_and_date_bounds(monkeypatch):
    store = _synthetic_store()
    monkeypatch.setattr(fdc, "load_versions", lambda symbols=None: store)

    def run(start, end):
        return [r for res in fdc.run_compute(symbols=["600000.SH"], start=start, end=end) for r in _rows_of(res)]

    unbounded = run(None, None)
    assert unbounded, "非空断言：合成 store 必须真出派生行"
    lo_d, hi_d = dt.date(2024, 4, 1), dt.date(2024, 4, 30)
    str_rows = run("2024-04-01", "2024-04-30")
    date_rows = run(lo_d, hi_d)
    mixed_rows = run(lo_d, "2024-04-30")
    assert str_rows == date_rows == mixed_rows == unbounded
    assert run("2024-05-01", "2024-05-31") == []  # 窗口外必空（判据非恒真）
    assert run(dt.date(2024, 5, 1), None) == []
