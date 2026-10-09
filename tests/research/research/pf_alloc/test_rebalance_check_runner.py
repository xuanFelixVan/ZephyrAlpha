# [BLUEPRINT] MOD-PA-044 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] tests.pf_alloc.test_rebalance_check_runner
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] pytest; zephyr.pf_alloc.rebalance_check_runner
# [CONSUMERS] FAC-E8 再平衡巡检读数件守卫（只读对照/失明告警/报告落盘/决策贯通）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] reader/alerter/now 全注入替身，零真 CH/零墙钟依赖/零网络；报告写 tmp_path；
#   决策口径=MOD-PF-003 真件（非复刻）——漂移超阈+成本通过必得 REBALANCE 决策
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [A_module] module_id=MOD-PA-044-T | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""rebalance_check_runner 单测——巡检读数件（数据面/决策面/失明面/报告面）。"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from zephyr.pf_alloc.rebalance_check_runner import run_rebalance_check

_NOW = datetime(2026, 9, 27, 5, 45, tzinfo=UTC)


class _FakeAlerter:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def notify(self, title, text, *, level="INFO", source=""):
        self.calls.append((level, {"title": title, "text": text}))


def _reader_from(budget_rows: dict[str, list], pocket_rows: list):
    """按 SQL 关键词分流的假 reader（positional 行序=各模板契约）。"""

    def _read(sql: str):
        if "max(trade_date)" in sql:
            return budget_rows.get("latest") or []
        if "LIMIT 1 BY strategy_id" in sql and "sleeve_plan_id" not in sql and "budget_action" not in sql:
            return pocket_rows
        if "budget_action" in sql:  # SQL_DAY_SLICE
            return budget_rows.get("slice") or []
        raise AssertionError(f"假 reader 未覆盖的 SQL: {sql[:80]}")

    return _read


def _budget_slice_row(sid: str, final_weight: float):
    # 列序真源 SQL_DAY_SLICE: strategy_id, run_id, allocation, global_shrinkage,
    # effective_budget, allocated_capital, final_weight, budget_action, current_tier
    return (sid, "run-x", 0.5, 1.0, 0.5, 5000.0, final_weight, "NO_ACTION", "idle")


def _pocket_row(sid: str, position_value: float, equity: float):
    return (sid, position_value, equity)


def test_drift_beyond_threshold_yields_rebalance(tmp_path: Path):
    # 目标 40% vs 当前 0%（全现金）→ 漂移 0.4 >> 阈值 0.02，成本 0.4 > 2×0 → REBALANCE
    reader = _reader_from(
        {"latest": [("2026-09-26",)], "slice": [_budget_slice_row("STR-A", 0.40)]},
        [_pocket_row("STR-A", 0.0, 10000.0)],
    )
    alerter = _FakeAlerter()
    out = run_rebalance_check(reader=reader, alerter=alerter, now=_NOW, out_path=tmp_path / "r.json")
    assert out["ok"] is True
    assert out["decision"]["decision"] == "rebalance"
    assert out["decision"]["trigger_source"] == "drift_threshold"
    assert (tmp_path / "r.json").exists()
    saved = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    assert saved["decision"]["decision"] == "rebalance"
    assert any(level == "WARN" for level, _ in alerter.calls)  # REBALANCE=Advisory 必出声


def test_no_drift_skips_silently(tmp_path: Path):
    reader = _reader_from(
        {"latest": [("2026-09-26",)], "slice": [_budget_slice_row("STR-A", 0.40)]},
        [_pocket_row("STR-A", 4000.0, 10000.0)],  # 市值/权益=0.40=目标
    )
    alerter = _FakeAlerter()
    out = run_rebalance_check(reader=reader, alerter=alerter, now=_NOW, out_path=tmp_path / "r.json")
    assert out["ok"] is True
    assert out["decision"]["decision"] == "skip_no_trigger"
    assert alerter.calls == []  # 无漂移零告警零留痕


def test_blind_scan_when_budget_side_empty(tmp_path: Path):
    reader = _reader_from({"latest": [], "slice": []}, [_pocket_row("STR-A", 100.0, 100.0)])
    alerter = _FakeAlerter()
    out = run_rebalance_check(reader=reader, alerter=alerter, now=_NOW, out_path=tmp_path / "r.json")
    assert out["ok"] is False
    assert "blind_scan" in out["error"]
    assert any(level == "WARN" for level, _ in alerter.calls)


def test_reader_exception_degrades_not_raises(tmp_path: Path):
    def _boom(sql: str):
        raise RuntimeError("ch down")

    alerter = _FakeAlerter()
    out = run_rebalance_check(reader=_boom, alerter=alerter, now=_NOW, out_path=tmp_path / "r.json")
    assert out["ok"] is False
    assert "ch down" in out["error"]
    assert any(level == "ERROR" for level, _ in alerter.calls)


def test_union_keys_fill_zero_not_drop(tmp_path: Path):
    """预算面有而钱包面无的策略=0 仓参与对照（禁丢键掩盖漂移）。"""
    reader = _reader_from(
        {
            "latest": [("2026-09-26",)],
            "slice": [_budget_slice_row("STR-A", 0.30), _budget_slice_row("STR-B", 0.10)],
        },
        [_pocket_row("STR-A", 0.0, 10000.0)],  # STR-B 无钱包行 → current 0.0
    )
    out = run_rebalance_check(reader=reader, alerter=_FakeAlerter(), now=_NOW, out_path=tmp_path / "r.json")
    assert out["ok"] is True
    assert out["wallets"] == 2
