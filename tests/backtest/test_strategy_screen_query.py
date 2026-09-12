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
    assert len(hist) == 3  # 2022/2024 两份原文的 C2 行 + 一行 C4 成绩
    c4 = [h for h in hist if h["batch"].startswith("C4")]
    assert len(c4) == 1 and c4[0]["is_sharpe"] == 0.727
    assert all(h["run_archive_exists"] for h in hist)


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
