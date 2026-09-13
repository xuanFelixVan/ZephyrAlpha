# [BLUEPRINT] MOD-BT-079 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_strategy_screen_query
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.strategy_screen_query
# [CONSUMERS] strategy_screen 查询器质量守卫（MODIFY-GUARD）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 只读（真实台账）；断言基于 C4 批已落库事实（2026-09-13 终态）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-079 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""strategy_screen_query 质量守卫——summary/trace/failed 三入口对真实台账的只读断言。"""

from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "strategy_screen_query", _REPO / "scripts" / "backtest" / "strategy_screen_query.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["strategy_screen_query"] = mod
spec.loader.exec_module(mod)


def _run(fn, ns) -> str:
    buf = StringIO()
    orig = sys.stdout
    sys.stdout = buf
    try:
        assert fn(ns) == 0
    finally:
        sys.stdout = orig
    return buf.getvalue()


def test_summary_counts_consistent():
    out = json.loads(_run(mod.cmd_summary, argparse_ns()))
    assert out["total"] >= 955
    assert out["uniq_strategy"] >= 556
    verdicts = {(b["batch"], b["verdict"]): b["rows"] for b in out["batches"]}
    assert verdicts[("C2-intake-2026-09-12", "screened_in")] == 381
    assert verdicts[("C4-translated-20260912", "translated_c4")] == 37
    assert verdicts[("C4-translated-20260912", "deferred_c4")] == 321
    assert any(r["reason"].startswith("deferred_") for r in out["failure_reasons"])


def test_trace_full_history():
    out = json.loads(_run(mod.cmd_trace, argparse_ns(pattern="6a6ec8869ddb")))
    assert len(out) == 1
    hist = out[0]["history"]
    # 台账只增：C2 两份原文行 + IS 成绩行 + 若干复测批行；断言关键事实而非行数
    assert len(hist) >= 3
    c2 = [h for h in hist if h["batch"].startswith("C2")]
    assert len(c2) == 2 and all(h["verdict"] == "screened_in" for h in c2)
    is_row = [h for h in hist if h["verdict"] == "translated_c4"]
    assert len(is_row) == 1 and is_row[0]["is_sharpe"] == 0.727
    assert all(h["run_archive_exists"] for h in hist)


def test_bothwin_gate():
    out = json.loads(_run(mod.cmd_bothwin, argparse_ns()))
    assert out["tested"] >= 35
    assert 0 < out["passed"] < out["tested"]
    assert "CAND-e3da6fa71af1" in out["passed_ids"]  # 恐慌反弹：唯一三窗全绿已知
    for i in out["items"]:
        if i["gate_bothwin_pass"]:
            assert i["is_sharpe"] > 0
            assert all(s["sharpe"] > 0 for s in i["segments"])


def test_failed_reason_filter():
    out = json.loads(_run(mod.cmd_failed, argparse_ns(reason="fundamental_gate", limit=5)))
    assert 0 < out["count"] <= 5
    assert all(i["reason"] == "deferred_fundamental_gate" for i in out["items"])


class argparse_ns:
    def __init__(self, **kw):
        self.reason = kw.get("reason")
        self.batch = kw.get("batch")
        self.limit = kw.get("limit", 100)
        self.min_sharpe = kw.get("min_sharpe")
        self.pattern = kw.get("pattern")
