"""pead_assembly 装配批测试（st-infoaxis P2 财报首刀）——假 reader 注入全离线。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.signal_fundamental.pead_assembly import (  # noqa: E402
    assemble,
    maybe_emit_pead_assembly,
    run_assembly,
)


def _fake_query_factory(income_tsv: str, consensus_map: dict[str, str] | None = None, fail_income: bool = False):
    def q(sql: str) -> str:
        if "income_statement" in sql:
            if fail_income:
                raise RuntimeError("CH down")
            return income_tsv
        if "consensus_daily" in sql:
            for sym, val in (consensus_map or {}).items():
                if f"symbol = '{sym}'" in sql:
                    return val
            return ""
        raise AssertionError(f"unexpected sql {sql[:60]}")

    return q


INCOME = "920003.BJ\t2026-10-12\t1.60\n600519.SH\t2026-10-11\t45.00\n"


def test_assemble_sue_and_band():
    q = _fake_query_factory(INCOME, {"920003.BJ": "1.00\n", "600519.SH": "50.00\n"})
    res = assemble("2026-10-13", ch_query=q)
    assert res["stats"]["assembled"] == 2
    by = {r["symbol"]: r for r in res["rows"]}
    assert abs(by["920003.BJ"]["sue"] - 0.6) < 1e-9
    assert by["920003.BJ"]["sue_band"] in ("positive", "strong_positive")
    assert by["600519.SH"]["sue"] < 0


def test_assemble_no_consensus_counted_not_failed():
    q = _fake_query_factory(INCOME, {"920003.BJ": "1.00\n"})
    res = assemble("2026-10-13", ch_query=q)
    assert res["stats"]["assembled"] == 1 and res["stats"]["no_consensus"] == 1


def test_assemble_near_zero_consensus_skipped():
    q = _fake_query_factory("600519.SH\t2026-10-11\t45.00\n", {"600519.SH": "0.0000001\n"})
    res = assemble("2026-10-13", ch_query=q)
    assert res["stats"]["sue_skip"] == 1 and res["stats"]["assembled"] == 0


def test_assemble_fail_open_on_income_error():
    q = _fake_query_factory("", fail_income=True)
    res = assemble("2026-10-13", ch_query=q)
    assert res["rows"] == [] and "income_statement 不可达" in res["stats"]["error"]


def test_run_assembly_dry_run_and_write():
    q = _fake_query_factory(INCOME, {"920003.BJ": "1.00\n", "600519.SH": "50.00\n"})
    res = run_assembly("2026-10-13", dry_run=True, ch_query=q)
    assert res["action"] == "dry_run" and res["tsv"].count("\n") == 1
    wrote = []
    res2 = run_assembly("2026-10-13", ch_query=q, writer=lambda t, c, tsv: (wrote.append((t, tsv)), True)[1])
    assert res2["action"] == "emitted" and wrote and "pead_earnings_event" in wrote[0][0]


def test_hook_five_states():
    assert maybe_emit_pead_assembly(task_id="daily_kline", success=True)["action"] == "skipped_wake_point"
    assert maybe_emit_pead_assembly(task_id="financial_batch", success=False)["action"] == "skipped_wake_point"
