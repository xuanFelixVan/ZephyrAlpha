"""expectation_revision_assembler 测试（st-infoaxis P2 研报首刀）——假 reader 全离线。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.alt_data.expectation_revision_assembler import (  # noqa: E402
    assemble_rating_changes,
    assemble_revision_trio,
    maybe_emit_expectation_revision,
    run_assembly,
)

# SQL ORDER BY symbol, publish_date ASC 形态（先期在前、后期在后）
RATINGS = (
    "600519.SH\t2026-09-10\t增持\n"
    "600519.SH\t2026-09-20\t买入\n"
    "000001.SZ\t2026-09-24\t买入\n"
    "000001.SZ\t2026-09-25\t买入\n"
    "300750.SZ\t2026-09-20\t买入\n"
    "300750.SZ\t2026-09-25\t强烈推荐\n"
    "688001.SH\t2026-09-15\t中性\n"
    "688001.SH\t2026-09-25\t减持\n"
)


def _q(ratings=RATINGS, now="", prior="", fail=False):
    def q(sql: str) -> str:
        if fail:
            raise RuntimeError("down")
        if "research_report" in sql:
            return ratings
        if "n_buy" in sql:
            return now
        if "eps_consensus FROM" in sql:
            return prior
        raise AssertionError(sql[:70])

    return q


def test_rating_changes_upgrade_downgrade_unmapped():
    res = assemble_rating_changes("2026-10-13", ch_query=_q())
    ev = {r["symbol"]: r for r in res["rows"]}
    assert ev["600519.SH"]["direction"] == "upgrade"  # 增持5→买入7
    assert ev["600519.SH"]["from_score"] == 5 and ev["600519.SH"]["to_score"] == 7
    assert ev["688001.SH"]["direction"] == "downgrade"  # 中性3→减持2
    assert "000001.SZ" not in ev  # 维持不落行
    assert res["stats"]["unmapped_rating"] == 1  # 强烈推荐跳过计数
    assert res["stats"]["events"] == 2


NOW = "600519.SH\t50.0\t2.0\t10\t7\t2\t1\n000001.SZ\t1.0\t0.1\t3\t1\t1\t1\n"
PRIOR = "600519.SH\t45.0\n"


def test_revision_trio_math():
    res = assemble_revision_trio("2026-10-13", ch_query=_q(now=NOW, prior=PRIOR))
    by = {r["symbol"]: r for r in res["rows"]}
    assert abs(by["600519.SH"]["revision_momentum"] - (50 - 45) / 45) < 1e-9
    assert abs(by["600519.SH"]["revision_breadth"] - (7 + 2 - 1) / 10) < 1e-9
    assert abs(by["600519.SH"]["dispersion"] - 2.0 / 50.0) < 1e-9
    assert "000001.SZ" not in by  # 无先值不落行


def test_fail_open():
    r1 = assemble_rating_changes("2026-10-13", ch_query=_q(fail=True))
    assert "不可达" in r1["stats"]["error"]
    r2 = assemble_revision_trio("2026-10-13", ch_query=_q(fail=True))
    assert "不可达" in r2["stats"]["error"]


def test_run_assembly_dry_and_write():
    q = _q(now=NOW, prior=PRIOR)
    res = run_assembly("2026-10-13", dry_run=True, ch_query=q)
    assert res["action"] == "dry_run"

    def w(t, c, tsv):
        return True

    res2 = run_assembly("2026-10-13", ch_query=q, writer=w)
    assert res2["action"] == "emitted"
    assert res2["rating_events"] == 2 and res2["trio_rows"] == 1


def test_hook_wake_filter():
    assert maybe_emit_expectation_revision(task_id="daily_kline", success=True)["action"] == "skipped_wake_point"
    assert maybe_emit_expectation_revision(task_id="consensus_refresh", success=False)["action"] == "skipped_wake_point"
