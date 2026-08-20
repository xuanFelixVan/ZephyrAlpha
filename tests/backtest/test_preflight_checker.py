# [BLUEPRINT] MOD-BT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.backtest.test_preflight_checker
# [TTL] permanent
"""BM-BT-02-D 回测前置检查器单元测试。"""
from __future__ import annotations

import datetime

from zephyr.backtest.core.preflight_checker import (
    ERR_PREFLIGHT_VIOLATION,
    run_backtest_preflight,
)

D = datetime.date


class TestStructural:
    def test_empty_symbols_fails(self):
        r = run_backtest_preflight([], D(2026, 1, 1), D(2026, 6, 30))
        assert not r.passed
        assert any(ERR_PREFLIGHT_VIOLATION in v for v in r.violations)

    def test_inverted_window_fails(self):
        r = run_backtest_preflight(["600000"], D(2026, 6, 30), D(2026, 1, 1))
        assert not r.passed

    def test_valid_structure_passes_with_skip_mark(self):
        r = run_backtest_preflight(["600000"], D(2026, 1, 1), D(2026, 6, 30))
        assert r.passed
        assert r.violations == ()
        assert r.skipped  # 无 DQ 注入时必须留 skipped 痕迹，防假通过


class TestDqInjection:
    def test_dq_violation_fails(self):
        checks = {"completeness": lambda t, w: ["kline_daily 缺口 3 日"]}
        r = run_backtest_preflight(["600000"], D(2026, 1, 1), D(2026, 6, 30), dq_checks=checks)
        assert not r.passed
        assert "kline_daily 缺口 3 日" in r.violations[0]

    def test_dq_clean_passes(self):
        checks = {"completeness": lambda t, w: []}
        r = run_backtest_preflight(["600000"], D(2026, 1, 1), D(2026, 6, 30), dq_checks=checks)
        assert r.passed and not r.skipped

    def test_multiple_checks_and_tables_fanout(self):
        calls = []

        def mk(name):
            def fn(t, w):
                calls.append((name, t))
                return []

            return fn

        checks = {"a": mk("a"), "b": mk("b")}
        r = run_backtest_preflight(["600000"], D(2026, 1, 1), D(2026, 6, 30), dq_checks=checks)
        assert r.passed
        assert calls == [("a", "c1_market.kline_daily"), ("b", "c1_market.kline_daily")]
