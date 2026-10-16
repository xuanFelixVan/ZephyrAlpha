"""equity_link_signals 三信号族测试（st-infoaxis P2 股权首刀）——注入全离线。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.signal_ashare.equity_link_signals import (  # noqa: E402
    PLEDGE_RISK_PCT,
    assemble_signals,
    maybe_emit_equity_link,
    run_assembly,
)

PG_NIUSAN = [("徐开东", 92, "CO:600001,CO:600002,CO:600003")]
PG_SAME = [("PE:x1", "某控股集团", 3, "CO:600001,CO:600004,CO:600005")]


def _pg(q: str):
    if "PE:%" in q and "2,4" in q:
        return PG_NIUSAN
    if "stake_pct" in q:
        return PG_SAME
    return []


@pytest.fixture(autouse=True)
def _ch_rows_isolated(monkeypatch):
    """生产隔离红线（宪法 §9.6）：query_rows 全量 mock，禁碰生产 CH。"""
    from zephyr.data import ch_reader

    monkeypatch.setattr(
        ch_reader,
        "query_rows",
        lambda sql: [("600999.SH", "张某", 95.5)] if "equity_pledge_detail" in sql else [],
        raising=True,
    )


def test_three_families_assembled():
    res = assemble_signals("2026-10-14", pg_query=_pg, ch_query=None)
    fams = {r["family"]: r for r in res["rows"]}
    assert fams["nium_san_cross"]["subject"] == "徐开东"
    assert fams["nium_san_cross"]["targets"] == "CO:600001|CO:600002|CO:600003"
    assert fams["nium_san_cross"]["strength"] == 92
    assert fams["same_holder_link"]["subject"] == "某控股集团"
    assert fams["pledge_chain"]["direction"] == -1 and fams["pledge_chain"]["targets"] == "600999.SH"
    assert abs(fams["pledge_chain"]["strength"] - 0.955) < 1e-9


def test_fail_open_per_family():
    def bad(q):
        raise RuntimeError("pg down")

    from zephyr.data import ch_reader

    orig = ch_reader.query_rows
    ch_reader.query_rows = lambda sql: []
    try:
        res = assemble_signals("2026-10-14", pg_query=bad, ch_query=None)
    finally:
        ch_reader.query_rows = orig
    assert res["rows"] == []
    assert "nium_san_error" in res["stats"] and "same_holder_error" in res["stats"]


def test_run_assembly_write():
    from zephyr.data import ch_reader

    orig = ch_reader.query_rows
    ch_reader.query_rows = lambda sql: [("600999.SH", "张某", 95.5)] if "equity_pledge" in sql else []
    try:
        wrote = []
        res = run_assembly(
            "2026-10-14",
            pg_query=_pg,
            ch_query=None,
            writer=lambda t, c, tsv: (wrote.append(t), True)[1],
        )
    finally:
        ch_reader.query_rows = orig
    assert res["action"] == "emitted" and res["rows"] == 3
    assert wrote == ["c3_fundamental.equity_link_signal"]


def test_pledge_threshold_in_sql():
    from zephyr.signal_ashare.equity_link_signals import SQL_PLEDGE_RISK

    assert "{min_pct}" in SQL_PLEDGE_RISK


def test_hook_wake_filter():
    assert maybe_emit_equity_link(task_id="daily_kline", success=True)["action"] == "skipped_wake_point"
    assert maybe_emit_equity_link(task_id="top10_refresh", success=False)["action"] == "skipped_wake_point"
