# [A_test] module_id: MOD-PFALLOC-ALLOC-DAILY | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PA-030 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md | §test
# [MODULE] tests.pf_alloc.test_sim_ledger_allocation_wiring
# [DOMAIN] D_PF_ALLOC
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/pf_alloc/test_sim_ledger_allocation_wiring.py
# [TTL] task_bound
"""纸面账本钱包额度 ← pf_alloc 分配快照 的接线回归锁（车道 D 接线①，PFA-2 治本）。

三侧同锁（缺一即可被静默回退）：
1. **有分配**：ensure_wallet 开钱包行的 initial_capital/cash/equity = 分配快照
   allocated_capital（= run_daily_allocation().wallet_capital 同源值），note 记快照 run_id，
   **不再**声称"策略引擎未接线"（额度侧）；
2. **无分配**（当日无行/本策略无行/表未建/查询异常）：逐元回退今天的 flat 口径
   （INITIAL_CAPITAL），且**回退原因写进 note**（fail-open 只在回退路径，禁静默伪造数字）；
3. **等价性**：以真链（注入假 reader/假 sink，零生产 IO）产出 res.wallet_capital，再把同一
   run 的落地行喂回账本 → 钱包额度与链返回值逐分对齐（证明"读表"与"读返回值"同一口径）。

全部离线：CH 读写与内置引擎 run() 全 mock（宪法 §9.6 测试禁写生产路径）。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
for _p in (str(_REPO), str(_REPO / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_spec = importlib.util.spec_from_file_location(
    "sim_paper_ledger_alloc_wiring", _REPO / "scripts" / "backtest" / "sim_paper_ledger.py")
mod = importlib.util.module_from_spec(_spec)
sys.modules["sim_paper_ledger_alloc_wiring"] = mod
_spec.loader.exec_module(mod)

DAY = "2026-09-15"
SID = "STR-E-WIRING-001"
ALLOC_TABLE = "c1_backtest.alloc_budget_daily"


def slice_row(sid: str, *, run_id: str = "alloc-2026-09-15-zz1",
              capital: float = 250_000.0) -> tuple:
    """SQL_DAY_SLICE 列序一行（strategy_id, run_id, allocation, global_shrinkage,
    effective_budget, allocated_capital, final_weight, budget_action, current_tier）——
    位置即契约，改序=账本读到 final_weight 当额度（静默事故形态），故此处按真源模板对齐。"""
    return (sid, run_id, 0.5, 0.6, 0.25, capital, 0.2, "RETARGET", "idle")


@pytest.fixture()
def ledger(monkeypatch):
    """离线账本：钱包存在性=无行、分配切片可配、write_tsv 捕获不落库、内置引擎禁用。"""
    from zephyr.data import ch_writer

    state: dict = {"alloc_rows": [], "alloc_error": None, "writes": [], "sqls": []}

    def fake_q(sql: str):
        state["sqls"].append(sql)
        if "alloc_budget_daily" in sql:
            if state["alloc_error"]:
                raise RuntimeError(state["alloc_error"])
            return list(state["alloc_rows"])
        return [(0,)]  # sim_pocket_daily 无当日行 → 继续开行

    monkeypatch.setattr(mod, "_q", fake_q)
    monkeypatch.setattr(
        mod, "run",
        lambda *a, **k: pytest.fail("非内置引擎策略不得走内置引擎 run()"))

    def fake_write(table, cols, payload):
        state["writes"].append((table, cols, payload.decode("utf-8")))
        return True

    monkeypatch.setattr(ch_writer, "write_tsv", fake_write)
    return state


def _row_of(state: dict, table: str, cols: str | None = None) -> dict[str, str]:
    """捕获的 TSV -> 列名字典（按写侧声明列解码，禁按位置猜列）。"""
    for name, columns, tsv in state["writes"]:
        if name == table:
            header = cols or columns
            names = [c.strip() for c in header.strip().strip("()").split(",") if c.strip()]
            return dict(zip(names, tsv.strip().split("\n")[0].split("\t"), strict=False))
    raise AssertionError(f"未捕获 {table} 的写入")


def pocket_row(state: dict) -> dict[str, str]:
    return _row_of(state, mod._TABLE)


def trade_event(state: dict) -> dict[str, str]:
    return _row_of(state, "c1_backtest.sim_trade_log")


# ── ① 有分配：额度取快照，note 记来源，不再声称"未接线" ─────────────────
def test_wallet_seeded_from_allocation_snapshot(ledger):
    ledger["alloc_rows"] = [slice_row(SID, run_id="alloc-2026-09-15-abc123", capital=250_000.0)]
    out = mod.ensure_wallet(SID, day=DAY)
    row = pocket_row(ledger)

    assert out["created"] is True and out["capital"] == 250_000.0
    assert float(row["initial_capital"]) == 250_000.0
    assert float(row["cash"]) == 250_000.0 == float(row["equity"])
    assert row["signal"] == "open"
    assert "alloc-2026-09-15-abc123" in row["note"]  # 分配快照版本留痕
    assert "未接线" not in row["note"]  # 额度侧不再是占位叙事
    # 事件溯源同额（rebuild() 按现金到账处理，两侧不同额=对账断链）
    assert float(trade_event(ledger)["cash_after"]) == 250_000.0


def test_zero_budget_allocation_is_honoured_never_fabricated(ledger):
    """被显式剔除的死成员额度=0 是一种裁定事实，不得被"好心"抬回 100 万。"""
    ledger["alloc_rows"] = [slice_row(SID, capital=0.0)]
    out = mod.ensure_wallet(SID, day=DAY)
    row = pocket_row(ledger)

    assert out["capital"] == 0.0
    assert float(row["initial_capital"]) == 0.0 and float(row["equity"]) == 0.0
    assert "alloc-2026-09-15-zz1" in row["note"] and "未接线" not in row["note"]


# ── ② 无分配：逐元回退今天的口径 + 原因入 note ─────────────────────────
def test_no_allocation_row_at_all_falls_back_with_reason(ledger):
    ledger["alloc_rows"] = []
    out = mod.ensure_wallet(SID, day=DAY)
    row = pocket_row(ledger)

    assert out["capital"] == mod.INITIAL_CAPITAL
    assert float(row["initial_capital"]) == mod.INITIAL_CAPITAL
    assert float(row["cash"]) == mod.INITIAL_CAPITAL == float(row["equity"])
    assert row["signal"] == "open"
    assert "回退 flat" in row["note"] and "无快照行" in row["note"]  # 原因留痕（非静默）
    assert "策略引擎未接线" in row["note"]  # 既有行为不变


def test_other_strategy_row_same_day_does_not_leak_capital(ledger):
    """当日切片里只有他策略的行 → 本策略仍是回退口径（错取他策略额度=最恶劣的静默伪造）。"""
    ledger["alloc_rows"] = [slice_row("STR-SOMEONE-ELSE", capital=999_999.0)]
    out = mod.ensure_wallet(SID, day=DAY)

    assert out["capital"] == mod.INITIAL_CAPITAL
    assert "无本策略行" in out["capital_source"]
    assert "999" not in pocket_row(ledger)["initial_capital"]


def test_missing_table_or_ch_error_falls_back_open_not_crash(ledger):
    ledger["alloc_error"] = "Code: 60. Table with same name already exists: doesn't exist"
    out = mod.ensure_wallet(SID, day=DAY)  # 分配链缺席绝不阻断开户
    row = pocket_row(ledger)

    assert out["created"] is True and out["capital"] == mod.INITIAL_CAPITAL
    assert float(row["initial_capital"]) == mod.INITIAL_CAPITAL
    assert "alloc_budget_daily 不可读" in row["note"]
    assert "doesn't exist" in row["note"]  # 原始原因原样入行，不粉饰


def test_illegal_day_literal_never_reaches_sql(ledger):
    """裸串入 SQL 的前置门（allocation_inputs 同口径）：非法日期→回退，不发查询。"""
    ledger["sqls"].clear()
    cap, source = mod.allocation_wallet_capital(SID, "2026-9-5")

    assert cap is None and "日期" in source
    assert ledger["sqls"] == []


# ── ③ 等价性：账本读到的额度 == run_daily_allocation 返回的 wallet_capital ──
class _EmptyReader:
    def __call__(self, sql: str):
        return []  # 无教材/无净值/无上期预算=冷启动缺省口径


class _Sink:
    def __init__(self):
        self.calls: list[tuple[str, str, bytes]] = []

    def __call__(self, table: str, columns: str, payload: bytes) -> str:
        self.calls.append((table, columns, payload))
        return "local_durable"

    def rows_of(self, table: str) -> list[dict[str, str]]:
        for name, columns, payload in self.calls:
            if name == table:
                names = [c.strip() for c in columns.strip().strip("()").split(",") if c.strip()]
                return [dict(zip(names, line.split("\t"), strict=False))
                        for line in payload.decode("utf-8").rstrip("\n").split("\n")]
        return []


def test_wallet_capital_equals_run_daily_allocation_output(tmp_path, ledger):
    from zephyr.pf_alloc.allocation_config import AllocationConfig
    from zephyr.pf_alloc.allocation_orchestrator import run_daily_allocation

    cfg = AllocationConfig(
        write_to_db=False,
        persist_path=(tmp_path / "tier_state.json").as_posix(),
        tdm_path=(tmp_path / "missing_tdm.yaml").as_posix(),
    )
    universe = [{"strategy_id": SID, "strategy_type": "多因子"},
                {"strategy_id": "STR-E-WIRING-002", "strategy_type": "多因子"}]
    sink = _Sink()
    res = run_daily_allocation(DAY, universe=universe, config=cfg, reader=_EmptyReader(),
                               sink=sink, run_suffix="t", alpha_provider=lambda sid, sig: ["600000.SH"])

    landed = sink.rows_of(ALLOC_TABLE)  # 同一次 run 的落地行（重跑=新 run_id 追加）
    assert [r["run_id"] for r in landed] == [res.run_id] * len(landed)
    ledger["alloc_rows"] = [
        (r["strategy_id"], r["run_id"], r["allocation"], r["global_shrinkage"],
         r["effective_budget"], float(r["allocated_capital"]), r["final_weight"],
         r["budget_action"], r["current_tier"])
        for r in landed
    ]

    out = mod.ensure_wallet(SID, day=DAY)
    assert out["capital"] == pytest.approx(res.wallet_capital[SID], abs=0.01)
    assert float(pocket_row(ledger)["initial_capital"]) == pytest.approx(
        res.wallet_capital[SID], abs=0.01)
    assert res.run_id in pocket_row(ledger)["note"]
