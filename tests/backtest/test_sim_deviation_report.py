# [BLUEPRINT] MOD-BT-093 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_sim_deviation_report
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.sim_deviation_report
# [CONSUMERS] 月度偏离报告质量守卫（MODIFY-GUARD）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 指标纯函数合成数据测试（不依赖 CH）+ CH 支持的月份报告集成断言
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-093 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_deviation_report 质量守卫——四项指标纯函数+verdict+月度报告集成。"""

from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "sim_deviation_report", _REPO / "scripts" / "backtest" / "sim_deviation_report.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["sim_deviation_report"] = mod
spec.loader.exec_module(mod)


def test_metrics_perfect_agreement():
    days = {f"2026-08-{d:02d}": 1 for d in range(1, 29)}
    m = mod.compute_metrics(days, days, set(), set(), {}, {})
    assert m["signal_agree"] == 1.0
    assert m["missed_rate"] == 0.0


def test_metrics_captures_missed_entry():
    bt = {f"2026-08-{d:02d}": 1 for d in range(1, 29)}
    sim = dict(bt)
    for d in range(5, 10):
        sim[f"2026-08-{d:02d}"] = 0  # 模拟盘早平仓 5 天
    m = mod.compute_metrics(sim, bt, {("2026-08-13", "exit")}, {("2026-08-13", "exit"), ("2026-08-18", "entry")}, {}, {})
    assert m["signal_agree"] < 1.0
    assert ("2026-08-18", "entry") in [tuple(x) for x in m["missed"]]


def test_verdict_thresholds():
    ok, breaches = mod.verdict_of({"signal_agree": 0.95, "missed_rate": 0.0, "gap_rel": 0.1})
    assert ok and not breaches
    ok2, breaches2 = mod.verdict_of({"signal_agree": 0.5, "missed_rate": 0.5, "gap_rel": 0.9})
    assert not ok2 and len(breaches2) == 3


def test_monthly_report_ch_backed():
    """CH 集成：2026-08 月度报告（恐慌反弹 sim 数据在库）。"""
    buf = StringIO()
    orig = sys.stdout
    sys.stdout = buf
    try:
        mod.main.__globals__["argparse_like"] = None  # no-op 占位
        # 直接调 main 的核心路径：--month 2026-08 --dry-run
        sys_argv = sys.argv
        sys.argv = ["sim_deviation_report.py", "--month", "2026-08", "--dry-run"]
        try:
            mod.main()
        finally:
            sys.argv = sys_argv
        out = buf.getvalue()
    finally:
        sys.stdout = orig
    assert '"month": "2026-08"' in out
    assert "STR-VREV-025" in out
