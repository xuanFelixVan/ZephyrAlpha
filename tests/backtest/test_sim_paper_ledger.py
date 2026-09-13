# [BLUEPRINT] MOD-BT-087 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_sim_paper_ledger
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.sim_paper_ledger
# [CONSUMERS] 模拟盘方案C质量守卫（MODIFY-GUARD: sim_paper_ledger/sim_trade_log）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读断言基于已落库事实；重建等价性=事件溯源设计的核心验收线
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-087 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_paper_ledger 质量守卫——钱包日账/事件流水/重建等价性三断言（真实台账只读）。"""

from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "sim_paper_ledger", _REPO / "scripts" / "backtest" / "sim_paper_ledger.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["sim_paper_ledger"] = mod
spec.loader.exec_module(mod)


def _run_replay() -> str:
    buf = StringIO()
    orig = sys.stdout
    sys.stdout = buf
    try:
        res = mod.run("replay_demo", "2026-07-01", "2026-09-11")
    finally:
        sys.stdout = orig
    assert res["rows"] and res["events"]
    return json.dumps({"final_equity": res["final_equity"], "rows": len(res["rows"]),
                       "events": len(res["events"])})


def test_replay_pipeline_consistent():
    """52 日回放：钱包行=交易日数，事件=2（一进一出），权益>初始。"""
    out = json.loads(_run_replay())
    assert out["rows"] == 52
    assert out["events"] == 2
    assert out["final_equity"] > mod.INITIAL_CAPITAL


def test_rebuild_matches_pocket():
    """事件流重建的钱包日账与落库快照逐字段一致（容差 0.01 元）。"""
    rows = mod.rebuild(mod.STRATEGY_ID, "replay_demo", "2026-07-01", "2026-09-11")
    orig = mod._q(
        "SELECT trade_date, argMax(cash, ingest_ts), argMax(shares, ingest_ts),"
        " argMax(position_value, ingest_ts), argMax(equity, ingest_ts)"
        " FROM c1_backtest.sim_pocket_daily WHERE strategy_id = 'STR-VREV-025'"
        " GROUP BY trade_date ORDER BY trade_date")
    assert len(rows) == len(orig) >= 50
    mismatch = 0
    for rebuilt, landed in zip(rows, orig):
        for a, b in [(rebuilt[3], landed[1]), (rebuilt[5], landed[2]),
                     (rebuilt[6], landed[3]), (rebuilt[7], landed[4])]:
            if abs(float(a) - float(b)) > 0.01:
                mismatch += 1
    assert mismatch == 0


def test_events_have_reason_snapshot():
    """每个事件必带触发判据快照（AI 复核需求的最低保障）。"""
    ev = mod._q("SELECT signal_reason FROM c1_backtest.sim_trade_log FINAL "
                "WHERE strategy_id = 'STR-VREV-025'")
    assert ev and all(r[0] and len(str(r[0])) > 5 for r in ev)
