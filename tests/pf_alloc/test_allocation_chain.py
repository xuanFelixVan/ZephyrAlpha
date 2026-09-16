# [A_test] module_id: MOD-TEST-PFALLOC-CHAIN | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PA-030 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] tests.pf_alloc.test_allocation_chain
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.pf_alloc.allocation_config/inputs/orchestrator/persistence;
#   zephyr.pf_alloc.batched_position_builder; pytest
# [CONSUMERS] pytest; CI_pipeline
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 测试只读生产口径、写侧一律注入假 sink 或 tmp_path（宪法 §9.6：禁写 data/ 生产目录）；
#   链的 fail-closed 三态（全死面板/缺输入/未落库）必须以"抛错"为断言，不得退化为告警
# [MODIFY-GUARD] src/zephyr/pf_alloc/allocation_orchestrator.py
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError→fail；预期异常用 pytest.raises（抛不出即 fail）
# [TESTS] self
# [A_module] module_id: MOD-TEST-PFALLOC-CHAIN | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #PFA-1 #PFA-2 #PFA-3 #PFA-4 车道 D 实盘分配链接线（pf_alloc_consumer_mining）
"""test_allocation_chain——pf_alloc 实盘分配链（config→inputs→orchestrator→persistence）单测。

覆盖（车道 D 收口，2026-09-16，真源=pf_alloc_consumer_mining PFA-1/2/3/4）：
  ① 正常多 sleeve：Σallocations=1.0、逐标的可追溯（裁决令牌 + 批次 + 落地行 TSV 行数）；
  ② 死成员/零权重成员显式剔除且**不静默再归一**（全灭面板 fail-closed 抛错，
     部分死成员以 budget=0 留痕入 alloc_budget_daily，绝不等权兜底）；
  ③ 现金席位：平钱包/空仓必须产出可见 cash drag 记录（结构化 CashSeat + warning），
     而非无声 100% 现金；零额度成员不得伪造现金记录；
  ④ 持久化：写侧只走注入 sink（禁触 data/）、列序=DDL 声明列、未持久化 fail-closed、
     TierState 快照落 tmp_path；
  ⑤ 输入层缺数据 fail-closed（非法日期/无教材/无净值/宇宙为空）；
  ⑥ 事件正门 handle_pf_alloc_daily_event（未知 kind、缺业务日期一律抛错，禁 log-and-skip）。
"""

from __future__ import annotations

import json

import pytest

from zephyr.pf_alloc.allocation_config import (
    AllocationConfig,
    AllocationConfigError,
    load_allocation_config,
)
from zephyr.pf_alloc.allocation_inputs import (
    FLAT_PROBABILITIES,
    AllocationInputError,
    BaseWeightTable,
    PerformanceScoreTable,
    build_base_weights,
    load_performance_scores,
    load_regime_input,
    validate_date_literal,
)
from zephyr.pf_alloc.allocation_orchestrator import (
    CashSeat,
    ExcludedMember,
    handle_pf_alloc_daily_event,
    run_daily_allocation,
    screen_panel,
    verify_allocation_invariants,
)
from zephyr.pf_alloc.allocation_persistence import (
    TABLE_COLUMNS,
    AllocationPersistenceError,
    write_rows,
)

TRADE_DATE = "2026-09-15"
UNIVERSE = [{"strategy_id": f"S{i}", "strategy_type": "多因子"} for i in range(1, 4)]


# ── 假件（零 IO：不连 CH、不落生产路径）────────────────────────────────


def make_config(tmp_path, **overrides) -> AllocationConfig:
    """落点全部指到 tmp_path（宪法 §9.6：测试禁写 data/ 与 .runtime 生产暂存）。"""
    base = {
        "write_to_db": False,
        "persist_path": (tmp_path / "tier_state.json").as_posix(),
        "tdm_path": (tmp_path / "missing_tdm.yaml").as_posix(),  # 可选文件缺失=等权先验
        "legacy_wallet_capital": 1_000_000.0,
    }
    base.update(overrides)
    return AllocationConfig(**base)  # type: ignore[arg-type]


class FakeReader:
    """CH 只读假件：按 SQL 特征分流，记录全部被问过的语句（可审计）。"""

    def __init__(self, *, snapshot=None, equity=None, prev_budgets=None):
        self.snapshot = snapshot
        self.equity = equity or {}
        self.prev_budgets = prev_budgets or []
        self.sqls: list[str] = []

    def __call__(self, sql: str):
        self.sqls.append(sql)
        if "regime_snapshot_history" in sql:
            return [self.snapshot] if self.snapshot else []
        if "alloc_budget_daily" in sql:
            return list(self.prev_budgets)
        if "min(trade_date)" in sql:
            sid = next((k for k in self.equity if f"'{k}'" in sql), None)
            return [(self.equity[sid][0][0] if sid else None,)]
        if "sim_pocket_daily" in sql:
            sid = next((k for k in self.equity if f"'{k}'" in sql), None)
            rows = self.equity.get(sid) or []
            return [(r[0], r[1]) for r in reversed(rows)]
        return []


def snapshot_row(**over):
    """regime_snapshot_history 一行的列序（与 load_regime_input 的 cols 严格对齐）。"""
    cols = (
        "run_id", "trade_date", "p_r1", "p_r2", "p_r3", "p_r4", "p_r10", "p_r11", "p_r12",
        "dominant", "confidence", "confidence_signal", "risk_signal", "shrinkage", "probs_json",
    )
    defaults = {
        "run_id": "reg-run-1", "trade_date": TRADE_DATE,
        "p_r1": 0.9, "p_r2": 0.05, "p_r3": 0.02, "p_r4": 0.01,
        "p_r10": 0.01, "p_r11": 0.005, "p_r12": 0.005,
        "dominant": "r1", "confidence": 0.9, "confidence_signal": 1.0,
        "risk_signal": 0.8, "shrinkage": 0.72, "probs_json": "{}",
    }
    defaults.update(over)
    return tuple(defaults[c] for c in cols)


class RecordingSink:
    """写侧假件：吃下 TSV 并如实回报投递事实（禁在测试里碰真库）。"""

    def __init__(self, disposition="local_durable"):
        self.calls: list[tuple[str, str, bytes]] = []
        self.disposition = disposition

    def __call__(self, table: str, columns: str, payload: bytes) -> str:
        self.calls.append((table, columns, payload))
        return self.disposition

    def rows_of(self, table: str) -> list[dict[str, str]]:
        for name, columns, payload in self.calls:
            if name == table:
                cols = [c.strip() for c in columns.strip().strip("()").split(",") if c.strip()]
                return [
                    dict(zip(cols, line.split("\t")))
                    for line in payload.decode("utf-8").rstrip("\n").split("\n")
                ]
        return []

    @property
    def tables(self):
        return [c[0] for c in self.calls]


def run(tmp_path, *, reader=None, sink=None, universe=None, alpha=None, config=None, **kw):
    cfg = config or make_config(tmp_path)
    rd = reader if reader is not None else FakeReader()
    sk = sink if sink is not None else RecordingSink()
    return run_daily_allocation(
        TRADE_DATE,
        universe=UNIVERSE if universe is None else universe,
        config=cfg,
        reader=rd,
        sink=sk,
        alpha_provider=alpha,
        run_suffix="t",
        **kw,
    )


# ── ① 正常多 sleeve：权重和=1 + 逐笔可追溯 ────────────────────────────


def test_multi_sleeve_allocations_sum_to_one(tmp_path):
    reader = FakeReader(snapshot=snapshot_row())
    res = run(tmp_path, reader=reader, alpha=lambda sid, sig: ["600000.SH", "000001.SZ"])
    alive = [s for s in res.strategies if not s.excluded_reason]
    assert len(alive) == 3
    assert sum(a.allocation for a in alive) == pytest.approx(1.0, abs=1e-6)
    assert 0.0 < res.global_shrinkage <= 1.0
    assert res.sum_effective_budget <= res.global_shrinkage + 1e-9
    # 钱包额度 = 总盘 × budget，且总钱包不超总盘
    total = res.portfolio_total_capital
    assert sum(res.wallet_capital.values()) <= total + 1e-6
    assert total == pytest.approx(3 * 1_000_000.0)


def test_each_symbol_traceable_to_adjudication_and_persisted(tmp_path):
    sink = RecordingSink()
    res = run(tmp_path, sink=sink, alpha=lambda sid, sig: ["600000.SH"])
    rows = sink.rows_of("c1_backtest.alloc_budget_daily")
    assert len(rows) == len(res.strategies) == 3
    for strat, row in zip(res.strategies, rows):
        assert strat.symbols and all(s.adjudication_id for s in strat.symbols)
        assert row["strategy_id"] == strat.strategy_id
        assert row["adjudication_id"].startswith(strat.symbols[0].adjudication_id[:8])
        payload = json.loads(row["batch_plan_json"])
        assert [s["symbol"] for s in payload["symbols"]] == [x.symbol for x in strat.symbols]
        assert all(s["adjudication_id"] for s in payload["symbols"])
        assert payload["cash_seat"]["strategy_id"] == strat.strategy_id
        assert payload["schema_version"]
    assert "c1_backtest.alloc_shrinkage_daily" in sink.tables
    assert len(sink.rows_of("c1_backtest.alloc_budget_daily")[0]) == len(
        TABLE_COLUMNS["c1_backtest.alloc_budget_daily"]
    )


def test_batch_plan_has_batches_when_allowed(tmp_path):
    res = run(tmp_path, alpha=lambda sid, sig: ["600000.SH", "000001.SZ", "000002.SZ"])
    assert any(s.batches for s in res.strategies[0].symbols)
    b = next(b for s in res.strategies[0].symbols for b in s.batches)
    assert {"batch_id", "weight_fraction", "trigger_conditions", "status"} <= set(b)


# ── ② 死成员/零权重：显式剔除，绝不静默再归一 ─────────────────────────


def _panel(weights: dict[str, float], scores: dict[str, float]):
    """构造 (先验表, 绩效表) 面板输入（screen_panel 的纯单测缝，不经 IO）。"""
    base = BaseWeightTable(weights=dict(weights), sources={k: "test" for k in weights})
    return base, PerformanceScoreTable(
        scores=dict(scores),
        sample_days={k: 100 for k in weights},
        details={},
    )


def test_screen_panel_excludes_dead_members_without_renormalizing():
    base, perf = _panel(
        {"S1": 0.5, "S2": 0.0, "S3": 0.2}, {"S1": 1.1, "S2": 1.0, "S3": 0.0}
    )
    alive, excluded = screen_panel(["S1", "S2", "S3"], base, perf)
    assert alive == ["S1"]
    assert {e.strategy_id for e in excluded} == {"S2", "S3"}
    assert all(isinstance(e, ExcludedMember) and e.reason for e in excluded)
    # 剔除后活成员集是分配器的唯一输入（不在本件重算权重——重算=静默再归一）
    assert sum(base.weights[s] for s in alive) == pytest.approx(0.5)


def test_screen_panel_fail_closed_when_all_members_dead():
    base, perf = _panel({"S1": 0.0, "S2": 0.0}, {"S1": 0.0, "S2": 0.0})
    with pytest.raises(AllocationInputError) as exc:
        screen_panel(["S1", "S2"], base, perf)
    assert "死成员" in str(exc.value)  # 禁"raw 全零→回退等权"的静默路径


def test_dead_member_gets_zero_budget_and_stays_auditable(tmp_path, monkeypatch):
    """死成员在装配层的落地面：budget=0 + excluded_reason 留痕，活成员不被抹平。"""
    dead = "S3"

    def fake_base(ids, cfg):
        return BaseWeightTable(
            weights={sid: (0.0 if sid == dead else 0.4) for sid in ids},
            sources={sid: "test" for sid in ids},
            max_single_sleeve=0.25,
            max_total_position=1.0,
            plan_id="TEST-PLAN",
        )

    monkeypatch.setattr(
        "zephyr.pf_alloc.allocation_orchestrator.build_base_weights", fake_base
    )
    sink = RecordingSink()
    res = run(tmp_path, sink=sink, alpha=lambda sid, sig: ["600000.SH"])
    by_id = {s.strategy_id: s for s in res.strategies}
    assert by_id[dead].effective_budget == 0.0
    assert by_id[dead].excluded_reason and "死成员" in by_id[dead].excluded_reason
    assert res.wallet_capital[dead] == 0.0
    assert any("dead_members_excluded" in w for w in res.warnings)
    assert {e.strategy_id for e in res.excluded_members} == {dead}
    # 活成员仍各得 0.5（等权兜底会把三人都抬到 1/3 —— 那正是被禁止的静默再归一）
    alive_allocs = {s.strategy_id: s.allocation for s in res.strategies if s.strategy_id != dead}
    assert all(v == pytest.approx(0.5, abs=1e-6) for v in alive_allocs.values())
    # 死成员保留在落地表里（可追溯：0 也是一种被裁定的事实）
    rows = sink.rows_of("c1_backtest.alloc_budget_daily")
    assert len(rows) == 3
    dead_row = next(r for r in rows if r["strategy_id"] == dead)
    assert float(dead_row["effective_budget"]) == 0.0
    assert "死成员" in json.loads(dead_row["batch_plan_json"])["excluded_reason"]


def test_verify_allocation_invariants_rejects_broken_allocator():
    class _Bad:
        allocations = {"S1": 0.5, "S2": 0.4}  # Σ≠1
        effective_budgets = {"S1": 0.4, "S2": 0.3}
        global_shrinkage = 0.7

    with pytest.raises(AllocationInputError):
        verify_allocation_invariants(_Bad(), ["S1", "S2"])

    class _Foreign:
        allocations = {"S1": 1.0}
        effective_budgets = {"S1": 1.0}
        global_shrinkage = 1.0

    with pytest.raises(AllocationInputError):  # 成员集与面板不符
        verify_allocation_invariants(_Foreign(), ["S1", "S2"])


# ── ③ 现金席位：平钱包空转必须可见，零额度不得伪造 ───────────────────


def test_flat_wallet_no_alpha_produces_visible_cash_drag(tmp_path):
    """PFA-2 病灶复现口径：额度已分到钱包但没有标的 → 必须产出 cash drag 事实。"""
    res = run(tmp_path, alpha=None)
    assert res.cash_seats and len(res.cash_seats) == 3
    for seat in res.cash_seats:
        assert isinstance(seat, CashSeat)
        assert seat.cash_weight == pytest.approx(1.0)
        assert seat.cash_capital == pytest.approx(res.wallet_capital[seat.strategy_id])
        assert seat.cash_drag is True
    assert any("cash_drag" in w for w in res.warnings)
    assert res.cash_drag_capital == pytest.approx(sum(res.wallet_capital.values()))


def test_zero_budget_wallet_does_not_fabricate_cash_drag(tmp_path, monkeypatch):
    def fake_base(ids, cfg):
        return BaseWeightTable(
            weights={sid: (0.0 if sid == "S3" else 0.4) for sid in ids},
            sources={sid: "test" for sid in ids},
            plan_id="TEST-PLAN",
        )

    monkeypatch.setattr(
        "zephyr.pf_alloc.allocation_orchestrator.build_base_weights", fake_base
    )
    res = run(tmp_path, alpha=lambda sid, sig: ["600000.SH"])
    seat = next(c for c in res.cash_seats if c.strategy_id == "S3")
    assert seat.cash_capital == 0.0 and seat.cash_drag is False


def test_cash_three_accounts_reconcile_to_total(tmp_path):
    """对账闭合：投出 + 钱包闲置 + 组合级未分配 = 总盘（缺一即"闷声出事"）。"""
    res = run(tmp_path, alpha=lambda sid, sig: ["600000.SH", "000001.SZ"])
    deployed = sum(c.invested_weight for c in res.cash_seats) * res.portfolio_total_capital
    assert deployed + res.cash_drag_capital + res.unallocated_cash == pytest.approx(
        res.portfolio_total_capital, abs=2.0
    )


def test_available_cash_shortfall_clips_weights_and_records_scale(tmp_path):
    """T+1 冻结注入点：可用资金只有一半 → 权重必须被 pro-rata 削减并留痕（不得假装买满）。"""
    res_full = run(tmp_path, alpha=lambda sid, sig: ["600000.SH", "000001.SZ"])
    half = sum(s.final_weight for s in res_full.strategies[0].symbols)

    res = run(
        tmp_path,
        alpha=lambda sid, sig: ["600000.SH", "000001.SZ"],
        available_cash_provider=lambda sid, cap: cap * 0.5,
    )
    clipped = sum(s.final_weight for s in res.strategies[0].symbols)
    assert clipped < half  # 裁剪真实生效（原实现算完 clip 就丢弃权重）
    seat = next(c for c in res.cash_seats if c.strategy_id == "S1")
    assert seat.clip_scale == pytest.approx(0.5, abs=1e-6)
    assert seat.degrade_reason and "available_cash" in seat.degrade_reason


# ── ④ 持久化：写侧走注入 sink / 列序真源 / 未落库 fail-closed ────────


def test_persist_paths_never_point_at_data_dir(tmp_path):
    with pytest.raises(AllocationConfigError):
        AllocationConfig(persist_path="data/runtime/alloc/tier.json")
    with pytest.raises(AllocationConfigError):
        AllocationConfig(tdm_path="data/config/tdm.yaml")
    cfg = make_config(tmp_path)
    assert "data" not in cfg.persist_full_path.as_posix().split("/")
    assert cfg.persist_full_path.parent == tmp_path


def test_tier_state_snapshot_written_under_tmp(tmp_path):
    res = run(tmp_path, alpha=lambda sid, sig: ["600000.SH"], universe=UNIVERSE)
    assert res.persisted["budget_daily"] == "local_durable"
    assert (tmp_path / "tier_state.json").exists()  # BudgetChangeHandler 落 tmp，不落 .runtime 根


def test_write_disabled_skips_sink_entirely(tmp_path):
    sink = RecordingSink()
    cfg = make_config(tmp_path, write_to_db=False)
    res = run(tmp_path, sink=sink, config=cfg, universe=UNIVERSE, write=False)
    assert sink.calls == []  # 显式 write=False 胜过"注入 sink 即写"的推断
    assert res.persisted["budget_daily"] == "skipped_write_disabled"
    assert res.persisted["shrinkage_daily"] == "skipped_write_disabled"


def test_injected_sink_writes_even_when_config_says_no(tmp_path):
    """对照口径：write=None 时注入 sink 即视为影子落该 sink（测试/影子专用通道）。"""
    sink = RecordingSink()
    res = run(tmp_path, sink=sink, config=make_config(tmp_path, write_to_db=False))
    assert res.persisted["budget_daily"] == "local_durable"
    assert "c1_backtest.alloc_budget_daily" in sink.tables


def test_not_durable_disposition_is_fail_closed():
    with pytest.raises(AllocationPersistenceError):
        write_rows(
            "c1_backtest.alloc_budget_daily",
            [dict.fromkeys(TABLE_COLUMNS["c1_backtest.alloc_budget_daily"], 0)],
            sink=lambda t, c, p: "not_durable",
        )


def test_missing_declared_column_raises_never_silent_pad():
    cols = TABLE_COLUMNS["c1_backtest.alloc_budget_daily"]
    row = dict.fromkeys(cols, 0)
    row.pop("effective_budget")
    with pytest.raises(AllocationPersistenceError) as exc:
        write_rows("c1_backtest.alloc_budget_daily", [row], sink=lambda t, c, p: "ch_committed")
    assert "effective_budget" in str(exc.value)


def test_unknown_table_raises_before_any_write():
    with pytest.raises(AllocationPersistenceError):
        write_rows("c1_backtest.alloc_nope", [{"a": 1}], sink=lambda t, c, p: "ch_committed")


def test_env_overrides_and_yaml_broken_config_fail_closed(tmp_path):
    cfg = load_allocation_config(
        yaml_path=str(tmp_path / "nope.yaml"),
        env={"ZEPHYR_PF_ALLOC_LEGACY_WALLET_CAPITAL": "500000", "ZEPHYR_PF_ALLOC_ENABLED": "0"},
    )
    assert cfg.legacy_wallet_capital == 500_000.0 and cfg.enabled is False
    assert cfg.resolve_portfolio_total(4) == pytest.approx(2_000_000.0)
    bad = tmp_path / "bad.yaml"
    bad.write_text("enabled: true\n: : :\n", encoding="utf-8")
    with pytest.raises(AllocationConfigError):
        load_allocation_config(yaml_path=str(bad), env={})
    typo = tmp_path / "typo.yaml"
    typo.write_text("enbled: false\n", encoding="utf-8")
    with pytest.raises(AllocationConfigError):
        load_allocation_config(yaml_path=str(typo), env={})


def test_disabled_switch_returns_empty_wallets_without_writing(tmp_path):
    sink = RecordingSink()
    res = run(tmp_path, sink=sink, config=make_config(tmp_path, enabled=False))
    assert res.enabled is False and res.wallet_capital == {}
    assert sink.calls == [] and res.persisted == {"disabled": "allocation_disabled"}


# ── ⑤ 输入层缺数据 fail-closed ───────────────────────────────────────


@pytest.mark.parametrize("bad", ["2026/09/15", "15-09-2026", "", "2026-9-5", "昨天"])
def test_illegal_date_literal_rejected(bad):
    with pytest.raises(AllocationInputError):
        validate_date_literal(bad)


def test_no_regime_snapshot_falls_back_to_flat_probs_neutral_throttle(tmp_path):
    cfg = make_config(tmp_path)
    reg = load_regime_input(TRADE_DATE, cfg, reader=FakeReader())  # 空结果=无教材
    assert reg.has_snapshot is False
    assert reg.probabilities == FLAT_PROBABILITIES
    assert reg.risk_signal_source == "neutral_fail_closed"
    assert reg.lag_days == -1 and reg.source_run_id == "synthetic_fail_closed"


def test_no_equity_series_yields_neutral_score_and_zero_samples(tmp_path):
    table = load_performance_scores(["S1"], TRADE_DATE, make_config(tmp_path), reader=FakeReader())
    assert table.scores["S1"] == pytest.approx(1.0)
    assert table.sample_days["S1"] == 0
    assert table.details["S1"].returns_used == 0


def test_empty_universe_fail_closed(tmp_path):
    with pytest.raises(AllocationInputError):
        run(tmp_path, universe=[])


def test_pp001_missing_file_gives_equal_weight_source(tmp_path):
    table = build_base_weights(["S1", "S2"], make_config(tmp_path))
    assert table.plan_id == ""
    assert set(table.sources.values()) == {"equal_weight"}


# ── ⑥ 事件正门（禁 cron/Timer：节拍由事件给）─────────────────────────


def test_event_gate_dispatches_valid_event(tmp_path):
    res = handle_pf_alloc_daily_event(
        {"kind": "pf_alloc_daily", "payload": {"trade_date": TRADE_DATE,
                                              "universe": UNIVERSE}},
        config=make_config(tmp_path),
        reader=FakeReader(),
        sink=RecordingSink(),
        alpha_provider=lambda sid, sig: ["600000.SH"],
    )
    assert res.trade_date == TRADE_DATE and len(res.strategies) == 3


@pytest.mark.parametrize(
    "event",
    [
        {"kind": "pf_alloc_weird", "payload": {"trade_date": TRADE_DATE}},
        {"kind": "pf_alloc_daily", "payload": {}},
        {"kind": "", "payload": {"trade_date": TRADE_DATE}},
    ],
)
def test_event_gate_rejects_unknown_kind_or_missing_date(tmp_path, event):
    with pytest.raises(AllocationInputError):
        handle_pf_alloc_daily_event(event, config=make_config(tmp_path), reader=FakeReader())
