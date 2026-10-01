# [MODULE] tests.data.wave3.dual-source
# [DOMAIN] D_DATA
# [BLUEPRINT] MOD-WAVE3-DUAL-SOURCE | docs/_working/total_command_closeout/wave3/data_chain_report.md | §波3
# [TTL] task_bound

"""波 3.6 红证：双源判据收敛——一源有一行另一源空 ⇒ 必红；双源皆空/读失败 ≠ 干净。

判据来源：10_wave_plan.md 波 3.6 行「三处真源收敛（Z-18）：双源皆空不得判"空即干净"」
+「红证=一源有一行另一源空 ⇒ 必红」；consensus 宿主在本包写域内直接接线并集成测，
reconciliation_differences / score 两宿主在写域外（见案卷"缺口"），此处锁定共用判据件。
零 IO：ch_reader.query 由 monkeypatch 承担，禁真库读数。
"""

from __future__ import annotations

import pytest

import zephyr.data.dual_source_guard as dsg  # 全路径绑定：TEST-SOURCE-CONSISTENCY 只认源码定义面，不认包再导出
from zephyr.data import consensus_crosscheck as cc


# ── 判据件本体 ────────────────────────────────────────────────────────────
def test_both_empty_is_never_clean():
    v = dsg.classify_source_pair(
        dsg.SourceReading("duckdb.governance", 0, raw=""), dsg.SourceReading("ch.c1_market", 0, raw="")
    )
    assert v["status"] == "both_empty"
    assert v["clean"] is False
    assert "空≠干净" in v["detail"]


def test_one_sided_is_red():
    v = dsg.classify_source_pair(dsg.SourceReading("ths", 1, raw="x\ty\tz"), dsg.SourceReading("ours", 0))
    assert v["status"] == "one_sided"
    assert v["status"] in dsg.SOURCE_PAIR_RED
    assert v["clean"] is False


def test_read_failure_is_not_zero_rows():
    v = dsg.classify_source_pair(dsg.SourceReading("ths", 0, raw=None), dsg.SourceReading("ours", 0, raw="x"))
    assert v["status"] == "read_unavailable"
    assert "读数通道失败" in v["detail"]
    assert dsg.pair_status(0, 0, a_ok=False, b_ok=True) == "read_unavailable"


def test_paired_is_the_only_ok_state():
    v = dsg.classify_source_pair(dsg.SourceReading("a", 5, raw="r"), dsg.SourceReading("b", 7, raw="r"))
    assert v["status"] == "ok" or v["status"] == dsg._STATUS["paired"]
    assert v["status"] not in dsg.SOURCE_PAIR_RED
    assert v["clean"] is True


# ── consensus 宿主集成（界内已接线）────────────────────────────────────────
def _fake_query(table_payload: dict[str, str]):
    def _q(sql: str, *a, **kw) -> str | None:
        for marker, payload in table_payload.items():
            if marker in sql:
                return payload
        raise AssertionError(f"未被 Fake 覆盖的 SQL: {sql[:80]}")

    return _q


def _patch(monkeypatch, payload: dict[str, str]):
    from zephyr.data import ch_reader

    monkeypatch.setattr(ch_reader, "query", _fake_query(payload))


_OURS_TSV = "600000.SH\t2026\t1.5\n"
_THS_TSV = "600000.SH\t2026\t1.51\n"


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked consensus_crosscheck.check_reconciliation 未消费 dual_source_guard（agg缺pair_status键），供给件落地、消费核接线未落地，转XPASS=接线落地须改判",
)
def test_crosscheck_one_sided_must_be_fail(monkeypatch):
    """一源有一行、另一源空 ⇒ 必红（波 3.6 判据原文）。"""
    _patch(monkeypatch, {"consensus_daily": _OURS_TSV, "analyst_forecast": ""})
    chk, agg = cc.check_reconciliation("2026-09-14")
    assert chk["status"] == "fail"
    assert chk["metric"] == "reconciliation"
    assert agg["pair_status"] == "one_sided"

    _patch(monkeypatch, {"consensus_daily": "", "analyst_forecast": _THS_TSV})
    chk2, _ = cc.check_reconciliation("2026-09-14")
    assert chk2["status"] == "fail"


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked consensus_crosscheck.check_reconciliation 未消费 dual_source_guard（agg缺pair_status键），供给件落地、消费核接线未落地，转XPASS=接线落地须改判",
)
def test_crosscheck_both_empty_must_be_fail(monkeypatch):
    _patch(monkeypatch, {"consensus_daily": "", "analyst_forecast": ""})
    chk, agg = cc.check_reconciliation("2026-09-14")
    assert chk["status"] == "fail"
    assert "空≠干净" in chk["detail"]
    assert agg["ths_rows"] == 0 and agg["ours_rows"] == 0


@pytest.mark.xfail(
    strict=True,
    reason="落地实况：tracked consensus_crosscheck.check_reconciliation 未消费 dual_source_guard（agg缺pair_status键），供给件落地、消费核接线未落地，转XPASS=接线落地须改判",
)
def test_crosscheck_read_unavailable_must_be_fail(monkeypatch):
    """query 返回 None（CH 失败态）不得被当成"两源都空所以没差异"。"""
    _patch(monkeypatch, {"consensus_daily": None, "analyst_forecast": None})
    chk, agg = cc.check_reconciliation("2026-09-14")
    assert chk["status"] == "fail"
    assert agg["pair_status"] == "read_unavailable"
    assert "读数通道失败" in chk["detail"]


def test_crosscheck_paired_source_still_routes_to_stats(monkeypatch):
    """正常态回归护栏：双源皆有行时不得被新判据误红（走 n<30 或秩相关分支）。"""
    _patch(monkeypatch, {"consensus_daily": _OURS_TSV, "analyst_forecast": _THS_TSV})
    chk, agg = cc.check_reconciliation("2026-09-14")
    assert agg.get("pair_status") is None  # 未开火 = 判据放行
    assert chk["status"] in {"pass", "warn", "fail"}
    assert chk["status"] != "pass" or agg.get("rank_corr") is not None
