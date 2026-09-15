# [BLUEPRINT] MOD-BT-200 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_dsr_recalc_backfill
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] scripts/backtest/dsr_recalc_backfill.py（被测）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯函数级测试零 CH/零网络（假 conn）；测试隔离（不写生产路径）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/backtest/test_dsr_recalc_backfill.py
# [A_module] module_id=MOD-BT-200 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""DSR 存量重算回填（A2+A3）单元测试——重折减数学/考证锚/窗口解析/计划生成。"""

from __future__ import annotations

import math
from statistics import NormalDist

import pytest

from scripts.backtest.dsr_recalc_backfill import (
    _AUDIT_ANCHORS,
    approx_dsr_from_sharpe,
    audit_batch_n,
    parse_window,
    recalc_plan,
    refold_dsr,
    trading_days,
)


class FakeCHConn:
    def __init__(self, days: int = 669) -> None:
        self.days = days
        self.calls: list[str] = []

    def execute(self, sql: str):  # noqa: ANN001
        self.calls.append(sql)
        if "count()" in sql and "kline_index" in sql:
            return [(self.days,)]
        return []


# ============ refold_dsr 重折减数学 ============

def test_refold_identity_when_n_unchanged():
    assert refold_dsr(0.9809, 1, 1) == pytest.approx(0.9809, abs=1e-9)


def test_refold_decreases_with_larger_n():
    few = refold_dsr(0.9809, 1, 100)
    many = refold_dsr(0.9809, 1, 10000)
    assert few < 0.9809
    assert many < few


def test_refold_anchor_overturned():
    # 0.9809 恐慌反弹行（N=1 solo 零折减虚高）按累计口径必须跌破 0.5（显式翻案锚）
    assert refold_dsr(0.9809, 1, 4481) < 0.5


def test_refold_extreme_dsr_clamped():
    # dsr=0.0 / 1.0 不产生 inf/nan
    for edge in (0.0, 1.0):
        v = refold_dsr(edge, 1, 500)
        assert math.isfinite(v)
        assert 0.0 <= v <= 1.0


def test_refold_math_matches_manual_composition():
    dsr_old, n_old, n_new = 0.6694, 4, 300
    nd = NormalDist()
    from zephyr.simulation.deflated_sharpe_calculator import _expected_max_sharpe

    manual = nd.cdf(nd.inv_cdf(dsr_old) + _expected_max_sharpe(n_old) - _expected_max_sharpe(n_new))
    assert refold_dsr(dsr_old, n_old, n_new) == pytest.approx(manual, abs=1e-12)


# ============ approx_dsr_from_sharpe 缺口补齐 ============

def test_approx_dsr_normal_case():
    # 年化 Sharpe 1.15、T=970、N=1 → 无折减 DSR 应略低于 0.5+（正态日频 SR≈0.072）
    v = approx_dsr_from_sharpe(1.15, 970, 1)
    assert 0.0 < v < 1.0
    # N 增大单调下降
    assert approx_dsr_from_sharpe(1.15, 970, 4481) < v


def test_approx_dsr_negative_sharpe_low():
    assert approx_dsr_from_sharpe(-0.3, 601, 4481) < 0.5


def test_approx_dsr_validation():
    with pytest.raises(ValueError):
        approx_dsr_from_sharpe(1.0, 2, 10)


# ============ parse_window 考证 ============

def test_parse_window_ok():
    notes = "window=2024-01-01/2026-06-30; kind=stock; is_sharpe_ref=-0.3"
    assert parse_window(notes) == ("2024-01-01", "2026-06-30", "stock")


def test_parse_window_none_for_no_evidence():
    assert parse_window(None) is None
    assert parse_window("随便一句备注") is None
    assert parse_window("") is None


# ============ audit_batch_n 考证锚 ============

def test_audit_batch_n_anchor_ok():
    rows = [{"run_id": "R1", "num_trials": 33}, {"run_id": "R2", "num_trials": None}]
    audit = {r[0]: r[1] for r in _AUDIT_ANCHORS.items()}
    audit["R2"] = 4
    out = audit_batch_n(rows, audit)
    assert out["R1"] == 33      # 已落账优先
    assert out["SCR-C4-20260913-232609"] == 1


def test_audit_batch_n_anchor_mismatch_fails_closed():
    bad = dict(_AUDIT_ANCHORS)
    bad["SCR-C4-20260913-232609"] = 35
    with pytest.raises(RuntimeError):
        audit_batch_n([], bad)


# ============ recalc_plan / trading_days ============

def _row(run_id, sid, is_sharpe, dsr, notes="window=2021-04-01/2023-12-31; kind=etf", batch="B", verdict="translated_c4"):
    return {"run_id": run_id, "screen_batch": batch, "strategy_id": sid, "verdict": verdict,
            "is_sharpe": is_sharpe, "deflated_sharpe": dsr, "num_trials": None, "notes": notes}


def test_recalc_plan_refold_and_gapfill():
    rows = [
        _row("R1", "S1", 1.15, 0.9809, "window=2016-01-01/2019-12-31; kind=index"),
        _row("R2", "S2", 0.5, None),
    ]
    conn = FakeCHConn(days=669)
    plan, skipped = recalc_plan(rows, {"R1": 1, "R2": 5}, 4481, conn)
    assert len(plan) == 2 and skipped == []
    refolded = next(p for p in plan if p["strategy_id"] == "S1")
    gap = next(p for p in plan if p["strategy_id"] == "S2")
    assert refolded["method"].startswith("refold")
    assert refolded["dsr_new"] == pytest.approx(round(refold_dsr(0.9809, 1, 4481), 4))
    assert gap["method"].startswith("normal_approx T=669")


def test_recalc_plan_skips_no_window_rows():
    rows = [_row("R1", "S1", 0.8, None, notes="")]
    plan, skipped = recalc_plan(rows, {"R1": 1}, 4481, FakeCHConn())
    assert plan == []
    assert skipped and "no_window_evidence" in skipped[0]["reason"]


def test_trading_days_cached():
    conn = FakeCHConn(days=970)
    cache: dict = {}
    assert trading_days(conn, "2020-01-01", "2023-12-31", cache) == 970
    assert trading_days(conn, "2020-01-01", "2023-12-31", cache) == 970
    assert len([c for c in conn.calls if "kline_index" in c]) == 1
