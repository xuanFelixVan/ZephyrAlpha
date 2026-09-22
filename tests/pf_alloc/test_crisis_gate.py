# [A_test] module_id: MOD-TEST-PFALLOC-CRISIS-GATE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-PFALLOC-CRISIS-GATE | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] tests.pf_alloc.test_crisis_gate
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.pf_alloc.crisis_gate; zephyr.pf_alloc.allocation_inputs;
#   zephyr.pf_alloc.allocation_orchestrator; zephyr.pf_alloc.core.regime_meta_allocator;
#   scripts.backtest.sim_paper_ledger(按文件路径加载); pytest
# [CONSUMERS] pytest; CI_pipeline
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 测试零 IO：CH 读走注入 reader、写侧假 writer/sink、告警假 alerter、
#   配置文件落 tmp_path（宪法 §9.6：禁写 data/ 生产目录与生产表）
# [MODIFY-GUARD] src/zephyr/pf_alloc/crisis_gate.py; src/zephyr/pf_alloc/allocation_orchestrator.py;
#   src/zephyr/pf_alloc/core/regime_meta_allocator.py; scripts/backtest/sim_paper_ledger.py
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError→fail；预期异常用 pytest.raises
# [TESTS] self
# [A_module] module_id: MOD-TEST-PFALLOC-CRISIS-GATE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_crisis_gate——WO-2a 危机态三级接线单测（验收场景全覆盖，2026-09-18）。

覆盖（wo2_blackswan_workbook §6 验收 2a + 任务红线七场景）：
  ① crisis→skip（L1 纯函数，skip=True 且 reason 明示"不落 marker 由调用方保证"）；
  ② warning→CRISIS_SHRINKAGE_FLOOR=0.05 激活（shrinkage 生效断言，monkeypatch 参数域）；
  ③ L2 冻结新开仓不动存量（CRISIS_FREEZE_NEW_POSITIONS，减持不经裁决中心）；
  ④ L3 entry→cash（panic 日被拦，signal='cash'，持有/强平不动，resolver 异常 fail-closed）；
  ⑤ 无快照→平坦 fail-closed 不误触（normal + fail_closed）；
  ⑥ θ 配置读取（tmp yaml 注入；未知键/越界硬错）；
  ⑦ 留痕与告警（假 writer 列序对齐 INSERT 真源；alerter 复用出声，crisis=CRITICAL）。
"""

from __future__ import annotations

import importlib.util
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from zephyr.pf_alloc.allocation_config import AllocationConfig
from zephyr.pf_alloc.allocation_inputs import FLAT_PROBABILITIES, RegimeInput
from zephyr.pf_alloc.core import regime_meta_allocator as rma
from zephyr.pf_alloc.core.regime_meta_allocator import RegimeMetaAllocator
from zephyr.pf_alloc.crisis_gate import (
    STATE_CRISIS,
    STATE_NORMAL,
    STATE_WARNING,
    CrisisGateError,
    alert_crisis_level,
    classify_crisis_state,
    crisis_block_check,
    load_crisis_gate_config,
    log_crisis_gate_row,
    resolve_crisis_state,
)

TRADE_DATE = "2026-09-15"


# ── 假件（零 IO）──────────────────────────────────────────────────────


def _regime(*, dominant="r1", p_r10=0.01, has_snapshot=True, source_day=None) -> RegimeInput:
    """构造 RegimeInput（7 维概率只突出 p_r10，其余均分余量）。"""
    rest = max(0.0, 1.0 - p_r10) / 6.0
    probs = (rest, rest, rest, rest, p_r10, rest, rest)
    if not has_snapshot:
        return RegimeInput(
            probabilities=FLAT_PROBABILITIES,
            dominant="unknown",
            source_run_id="synthetic_fail_closed",
            source_date=None,
            lag_days=-1,
            snapshot_shrinkage=None,
            risk_signal=1.0,
            risk_signal_source="neutral_fail_closed",
            is_crisis=False,
            max_probability=max(FLAT_PROBABILITIES),
        )
    return RegimeInput(
        probabilities=probs,
        dominant=dominant,
        source_run_id="reg-run-1",
        source_date=source_day or date(2026, 9, 14),
        lag_days=1,
        snapshot_shrinkage=0.72,
        risk_signal=0.8,
        risk_signal_source="snapshot_direct",
        is_crisis=dominant == "r10",
        max_probability=max(probs),
    )


class FakeReader:
    """CH 只读假件：按 SQL 特征分流（与 test_allocation_chain.FakeReader 同构）。"""

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
            return [(None,)]
        if "sim_pocket_daily" in sql:
            return []
        return []


def snapshot_row(**over):
    """regime_snapshot_history 一行的列序（与 load_regime_input 的 cols 严格对齐）。"""
    cols = (
        "run_id",
        "trade_date",
        "p_r1",
        "p_r2",
        "p_r3",
        "p_r4",
        "p_r10",
        "p_r11",
        "p_r12",
        "dominant",
        "confidence",
        "confidence_signal",
        "risk_signal",
        "shrinkage",
        "probs_json",
    )
    defaults = {
        "run_id": "reg-run-1",
        "trade_date": "2026-09-14",
        "p_r1": 0.30,
        "p_r2": 0.05,
        "p_r3": 0.03,
        "p_r4": 0.02,
        "p_r10": 0.55,
        "p_r11": 0.03,
        "p_r12": 0.02,
        "dominant": "r1",
        "confidence": 0.55,
        "confidence_signal": 0.30,
        "risk_signal": 0.8,
        "shrinkage": 0.24,
        "probs_json": "{}",
    }
    defaults.update(over)
    return tuple(defaults[c] for c in cols)


class RecordingWriter:
    """CH 写侧假件：吃下 INSERT 并如实记录（禁在测试里碰真库）。"""

    def __init__(self, fail: bool = False):
        self.calls: list[tuple[str, list[tuple]]] = []
        self.fail = fail

    def execute(self, sql: str, params: list[tuple]):
        if self.fail:
            raise RuntimeError("CH 不可写（模拟）")
        self.calls.append((sql, params))


class RecordingAlerter:
    """alerter 假件：记录 notify 调用（复用通道的出声断言面）。"""

    def __init__(self):
        self.calls: list[tuple] = []

    def notify(self, task_id, error, level="ERROR", source=None, extra=None):
        self.calls.append((task_id, error, level, source, extra))
        return True


# ── ① 判定三档 + ⑤ 无快照 fail-closed 不误触 ─────────────────────────


def test_classify_normal_warning_crisis():
    normal = classify_crisis_state(_regime(dominant="r1", p_r10=0.10), warning_theta=0.5)
    warning = classify_crisis_state(_regime(dominant="r3", p_r10=0.60), warning_theta=0.5)
    crisis = classify_crisis_state(_regime(dominant="r10", p_r10=0.40), warning_theta=0.5)
    assert normal.state == STATE_NORMAL
    assert warning.state == STATE_WARNING
    assert crisis.state == STATE_CRISIS
    # crisis ⊃ warning：floor 语义随行
    assert crisis.floor_active and warning.floor_active and not normal.floor_active


def test_no_snapshot_flat_fail_closed_no_misfire():
    """验收③：无快照日平坦分布不误触发（normal 且 fail_closed 标记）。"""
    cs = classify_crisis_state(_regime(has_snapshot=False), warning_theta=0.5)
    assert cs.state == STATE_NORMAL
    assert cs.fail_closed is True
    assert cs.source_date is None and cs.lag_days == -1
    block = crisis_block_check(TRADE_DATE, state=cs)
    assert block.skip is False
    assert "fail-closed" in block.reason


def test_crisis_block_check_skip_true_no_marker_contract():
    """验收①：crisis→skip=True；reason 明示不落 marker 由调用方保证（可重放）。"""
    cs = classify_crisis_state(_regime(dominant="r10"), warning_theta=0.5)
    block = crisis_block_check(TRADE_DATE, state=cs)
    assert block.skip is True
    assert block.state == STATE_CRISIS
    assert "不落 marker" in block.reason and "调用方保证" in block.reason
    # warning 不拦（照跑 + 缩额在 L2）
    warn_block = crisis_block_check(
        TRADE_DATE, state=classify_crisis_state(_regime(dominant="r3", p_r10=0.6), warning_theta=0.5)
    )
    assert warn_block.skip is False and warn_block.state == STATE_WARNING


def test_resolve_crisis_state_real_read_path_with_fake_reader():
    """resolve_crisis_state 复用 load_regime_input（注入 reader 全链跑通，零真 CH）。"""
    reader = FakeReader(snapshot=snapshot_row(dominant="r10", p_r10=0.7))
    cs = resolve_crisis_state(TRADE_DATE, reader=reader)
    assert cs.state == STATE_CRISIS
    assert cs.source_date == date(2026, 9, 14) and cs.lag_days == 1
    # 无快照行 → 平坦 fail-closed normal
    empty = resolve_crisis_state(TRADE_DATE, reader=FakeReader())
    assert empty.state == STATE_NORMAL and empty.fail_closed is True
    # warning 快照：p_r10=0.55≥0.5 但 dominant=r1
    warn = resolve_crisis_state(TRADE_DATE, reader=FakeReader(snapshot=snapshot_row(p_r10=0.55, dominant="r1")))
    assert warn.state == STATE_WARNING


# ── ⑥ θ 与全部参数走 config/crisis_gate.yaml ─────────────────────────


def test_theta_config_loaded_from_yaml(tmp_path):
    yaml_path = tmp_path / "crisis_gate.yaml"
    yaml_path.write_text("enabled: true\nwarning_theta: 0.7\n", encoding="utf-8")
    cfg = load_crisis_gate_config(yaml_path)
    assert cfg.warning_theta == 0.7 and cfg.enabled is True
    # 同一 p_r10=0.6：θ=0.5 → warning；θ=0.7 → normal（θ 生效的语义断言）
    regime = _regime(dominant="r3", p_r10=0.60)
    assert classify_crisis_state(regime, warning_theta=0.5).state == STATE_WARNING
    assert classify_crisis_state(regime, warning_theta=0.7).state == STATE_NORMAL


def test_theta_config_missing_file_defaults_and_errors(tmp_path):
    # 缺文件=全缺省（可选文件）
    cfg = load_crisis_gate_config(tmp_path / "missing.yaml")
    assert cfg.enabled is True and cfg.warning_theta == 0.5
    # 未知键=硬错（防拼写漂移静默不生效）
    bad = tmp_path / "bad.yaml"
    bad.write_text("enabled: true\nwarnning_theta: 0.5\n", encoding="utf-8")
    with pytest.raises(CrisisGateError):
        load_crisis_gate_config(bad)
    # θ 越界=硬错
    oob = tmp_path / "oob.yaml"
    oob.write_text("warning_theta: 1.5\n", encoding="utf-8")
    with pytest.raises(CrisisGateError):
        load_crisis_gate_config(oob)


def test_gate_disabled_bypasses_block():
    cfg = load_crisis_gate_config(tmp_path := Path(__file__).parent / "_nonexistent")  # noqa: F841
    from zephyr.pf_alloc.crisis_gate import CrisisGateConfig

    bypass = CrisisGateConfig(enabled=False)
    crisis = classify_crisis_state(_regime(dominant="r10"), warning_theta=0.5)
    block = crisis_block_check(TRADE_DATE, state=crisis, gate_config=bypass)
    assert block.skip is False and block.state == "disabled"


# ── ② warning→CRISIS_SHRINKAGE_FLOOR=0.05 激活（shrinkage 生效断言）──


class TestWarningFloorActivation:
    def test_compute_shrinkage_floor_active_lowers_to_005(self, monkeypatch):
        """crisis_floor_active=True（warning 档）激活 0.05 floor（monkeypatch 参数域）。"""
        monkeypatch.setattr(rma, "RISK_SIGNAL_MIN", 0.10)
        alloc = RegimeMetaAllocator()
        normal = alloc._compute_shrinkage([0.50, 0.50], {"risk_base": 0.10})
        warning = alloc._compute_shrinkage([0.50, 0.50], {"risk_base": 0.10}, crisis_floor_active=True)
        assert normal.final_shrinkage == pytest.approx(rma.SHRINKAGE_FLOOR)  # 0.09 兜底
        assert warning.final_shrinkage == pytest.approx(rma.CRISIS_SHRINKAGE_FLOOR)  # 0.05
        assert warning.is_crisis is False  # warning 档不改 is_crisis 归因

    def test_current_param_domain_floor_not_binding(self):
        """当前参数域 raw≥0.09：floor 激活是前瞻口径，输出不变（不夸大生效范围）。"""
        alloc = RegimeMetaAllocator()
        plain = alloc._compute_shrinkage([0.50, 0.50], {"risk_base": 0.2})
        active = alloc._compute_shrinkage([0.50, 0.50], {"risk_base": 0.2}, crisis_floor_active=True)
        assert plain.final_shrinkage == pytest.approx(rma.SHRINKAGE_FLOOR)
        assert active.final_shrinkage == pytest.approx(rma.SHRINKAGE_FLOOR)

    def test_allocate_backward_compatible_kwargs(self, monkeypatch):
        """扩参数向后兼容：缺省 False=既有行为零变化；is_crisis 通道不受影响。"""
        monkeypatch.setattr(rma, "RISK_SIGNAL_MIN", 0.10)
        alloc = RegimeMetaAllocator()
        common = dict(
            regime_probabilities=[0.50, 0.50],
            performance_scores={"a": 1.0, "b": 1.0},
            risk_signal_inputs={"risk_base": 0.10},
        )
        base = alloc.allocate(**common)
        with_floor = alloc.allocate(**common, crisis_floor_active=True)
        crisis = alloc.allocate(**common, is_crisis=True)
        assert base.global_shrinkage == pytest.approx(rma.SHRINKAGE_FLOOR)
        assert with_floor.global_shrinkage == pytest.approx(rma.CRISIS_SHRINKAGE_FLOOR)
        assert crisis.global_shrinkage == pytest.approx(rma.CRISIS_SHRINKAGE_FLOOR)


# ── ③ L2 冻结新开仓（不动存量减持）───────────────────────────────────


class TestL2StrategyLayer:
    def _facts(self, *, is_crisis=False):
        from zephyr.pf_alloc.allocation_orchestrator import _LayerFacts, _strategy_layer

        facts = _LayerFacts(
            sleeve_cap=0.25,
            total_cap=1.0,
            sum_effective=0.5,
            symbol_aggregate={},
            freeze={"S1": False},
            retain={"S1": None},
            calendar_block_new=False,
            calendar_cap_adjustment=1.0,
            is_crisis=is_crisis,
        )
        return facts, _strategy_layer(facts)

    def _request(self):
        from zephyr.position.core.position_adjudication_center import (
            AdjudicationRequest,
            IntendedAction,
        )

        return AdjudicationRequest(
            request_id="t:S1:600000.SH",
            strategy_id="S1",
            symbol="600000.SH",
            action=IntendedAction.OPEN,
            intended_weight=0.10,
            context={"strategy_effective_budget": 0.30},
        )

    def test_crisis_freezes_new_positions(self):
        facts, layer = self._facts(is_crisis=True)
        verdict = layer(self._request())
        assert verdict.allowed is False
        assert verdict.adjusted_weight == 0.0
        assert "CRISIS_FREEZE_NEW_POSITIONS" in verdict.violations
        assert "不动存量" in verdict.reason and "不强平" in verdict.reason

    def test_crisis_priority_over_tier1(self):
        facts, layer = self._facts(is_crisis=True)
        facts.freeze["S1"] = True
        verdict = layer(self._request())
        assert "CRISIS_FREEZE_NEW_POSITIONS" in verdict.violations

    def test_non_crisis_unchanged_tier1_semantics(self):
        facts, layer = self._facts(is_crisis=False)
        verdict = layer(self._request())
        assert verdict.allowed is True
        facts.freeze["S1"] = True
        verdict2 = layer(self._request())
        assert verdict2.allowed is False
        assert "TIER1_FREEZE_NEW_POSITIONS" in verdict2.violations


class RecordingAllocator:
    """allocate 假件：记录 kwargs（断言 orchestrator 传参），委托真分配器保行为。"""

    def __init__(self):
        self.kwargs_seen: list[dict] = []
        self._inner = RegimeMetaAllocator()

    def allocate(self, **kwargs):
        self.kwargs_seen.append(dict(kwargs))
        return self._inner.allocate(**kwargs)


def _run_orchestrator(tmp_path, snapshot, **kw):
    """orchestrator 全链假件跑法（复刻 test_allocation_chain harness 的最小集）。"""
    from zephyr.pf_alloc.allocation_orchestrator import run_daily_allocation

    cfg = AllocationConfig(
        write_to_db=False,
        persist_path=(tmp_path / "tier_state.json").as_posix(),
        tdm_path=(tmp_path / "missing_tdm.yaml").as_posix(),
    )
    reader = FakeReader(snapshot=snapshot)
    allocator = RecordingAllocator()
    res = run_daily_allocation(
        TRADE_DATE,
        universe=[{"strategy_id": "S1", "strategy_type": "多因子"}],
        config=cfg,
        reader=reader,
        sink=lambda table, columns, payload: "local_durable",
        alpha_provider=lambda sid, sig: ["600000.SH"],
        allocator=allocator,
        run_suffix="t",
        **kw,
    )
    return res, allocator


def test_orchestrator_crisis_passes_is_crisis_and_freezes(tmp_path, monkeypatch):
    """验收①：注入 crisis 快照 → 分配器收 is_crisis=True；裁决层冻结新开仓。"""
    # 告警/留痕假件替换（禁写生产 failures/ 与 CH）
    import zephyr.pf_alloc.allocation_orchestrator as ao

    monkeypatch.setattr(ao, "alert_crisis_level", lambda *a, **k: True)
    monkeypatch.setattr(ao, "log_crisis_gate_row", lambda **k: True)
    crisis_row = snapshot_row(dominant="r10", p_r10=0.7)
    res, allocator = _run_orchestrator(tmp_path, crisis_row)
    assert allocator.kwargs_seen and allocator.kwargs_seen[0]["is_crisis"] is True
    assert allocator.kwargs_seen[0]["crisis_floor_active"] is True
    assert any("crisis_gate_crisis" in w for w in res.warnings)
    frozen = [s for st in res.strategies for s in (st.symbols or ()) if not s.allowed]
    assert frozen and all("CRISIS_FREEZE_NEW_POSITIONS" in s.reason for s in frozen)


def test_orchestrator_warning_activates_floor_only(tmp_path, monkeypatch):
    """warning 快照：floor 激活但 is_crisis=False（不冻结新开仓）。"""
    import zephyr.pf_alloc.allocation_orchestrator as ao

    monkeypatch.setattr(ao, "alert_crisis_level", lambda *a, **k: True)
    monkeypatch.setattr(ao, "log_crisis_gate_row", lambda **k: True)
    warn_row = snapshot_row(dominant="r1", p_r10=0.55)
    res, allocator = _run_orchestrator(tmp_path, warn_row)
    assert allocator.kwargs_seen[0]["is_crisis"] is False
    assert allocator.kwargs_seen[0]["crisis_floor_active"] is True
    assert any("crisis_gate_warning" in w for w in res.warnings)
    allowed = [s for st in res.strategies for s in (st.symbols or ()) if s.allowed]
    assert allowed  # warning 不冻结


def test_orchestrator_normal_day_no_alert_no_log(tmp_path, monkeypatch):
    """normal 日：零告警零留痕（既有行为零变化）。"""
    import zephyr.pf_alloc.allocation_orchestrator as ao

    calls: list[str] = []
    monkeypatch.setattr(ao, "alert_crisis_level", lambda *a, **k: calls.append("alert") or True)
    monkeypatch.setattr(ao, "log_crisis_gate_row", lambda **k: calls.append("log") or True)
    normal_row = snapshot_row(dominant="r1", p_r10=0.01)
    _run_orchestrator(tmp_path, normal_row)
    assert calls == []


# ── ④ L3 entry→cash（账本级拦截）─────────────────────────────────────


def _load_ledger_module():
    spec = importlib.util.spec_from_file_location(
        "sim_paper_ledger",
        Path(__file__).resolve().parents[2] / "scripts" / "backtest" / "sim_paper_ledger.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _panic_frames():
    """合成两连跌：第 3 日命中 panic（上证 -2.5%/-1.54%），个股平价。"""
    import pandas as pd

    idx = pd.to_datetime(["2026-09-01", "2026-09-02", "2026-09-03"])
    sh = pd.DataFrame({"close": [100.0, 97.5, 96.0]}, index=idx)
    px = pd.DataFrame({"close": [100.0, 100.0, 100.0]}, index=idx)
    return sh, px


def _crisis_state(crisis=True):
    cs = classify_crisis_state(
        _regime(dominant="r10" if crisis else "r1", p_r10=0.7 if crisis else 0.01), warning_theta=0.5
    )
    return cs


class TestL3LedgerEntryBlock:
    def test_crisis_day_entry_blocked_to_cash(self, monkeypatch):
        mod = _load_ledger_module()
        sh, px = _panic_frames()
        monkeypatch.setattr(mod, "pd_idx", lambda sym, start, end: sh if sym == "000001" else px)
        res = mod.run(
            "sim_daily",
            "2026-09-01",
            "2026-09-03",
            run_id="t-crisis",
            crisis_resolver=lambda day: _crisis_state(crisis=True),
        )
        # panic 日被拦：signal='cash'，note 留痕，无 entry 事件，钱包全程满现金
        blocked_row = res["rows"][-1]
        assert blocked_row[9] == "cash"
        assert "crisis_gate:entry_blocked" in blocked_row[12]
        assert not any(e[3] == "entry" for e in res["events"])
        assert res["crisis_blocked_days"] == ["2026-09-03"]
        assert res["final_equity"] == pytest.approx(1_000_000.0)

    def test_non_crisis_day_entry_proceeds(self, monkeypatch):
        mod = _load_ledger_module()
        sh, px = _panic_frames()
        monkeypatch.setattr(mod, "pd_idx", lambda sym, start, end: sh if sym == "000001" else px)
        res = mod.run(
            "sim_daily",
            "2026-09-01",
            "2026-09-03",
            run_id="t-normal",
            crisis_resolver=lambda day: _crisis_state(crisis=False),
        )
        assert any(e[3] == "entry" for e in res["events"])
        assert res["crisis_blocked_days"] == []

    def test_resolver_error_fails_closed(self, monkeypatch):
        """resolver 异常=读不到≠安全 → fail-closed 拦 entry（持有不受影响）。"""
        mod = _load_ledger_module()
        sh, px = _panic_frames()
        monkeypatch.setattr(mod, "pd_idx", lambda sym, start, end: sh if sym == "000001" else px)

        def boom(day):
            raise RuntimeError("CH down")

        res = mod.run("sim_daily", "2026-09-01", "2026-09-03", run_id="t-boom", crisis_resolver=boom)
        assert res["rows"][-1][9] == "cash"
        assert "resolver_error" in res["rows"][-1][12]
        assert not any(e[3] == "entry" for e in res["events"])

    def test_holding_and_exit_untouched_by_crisis(self, monkeypatch):
        """crisis 只拦 entry：已持仓的持有/强平路径与无闸日完全一致。"""
        mod = _load_ledger_module()

        def frames_with_entry_then_crisis():
            import pandas as pd

            idx = pd.to_datetime(["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04"])
            sh = pd.DataFrame({"close": [100.0, 97.5, 96.0, 96.0]}, index=idx)
            px = pd.DataFrame({"close": [100.0, 100.0, 100.0, 101.0]}, index=idx)
            return sh, px

        sh, px = frames_with_entry_then_crisis()

        def resolver_by_day(day):
            # 09-03 normal（正常 entry）；09-04 crisis（持仓日照常 holding）
            return _crisis_state(crisis=(day == "2026-09-04"))

        monkeypatch.setattr(mod, "pd_idx", lambda sym, start, end: sh if sym == "000001" else px)
        res = mod.run("sim_daily", "2026-09-01", "2026-09-04", run_id="t-hold", crisis_resolver=resolver_by_day)
        signals = [r[9] for r in res["rows"]]
        assert signals[2] == "entry"  # crisis 前 entry 正常
        assert signals[3] == "holding"  # crisis 日持仓日照常持有（不强平不清仓）


# ── ⑦ 留痕与告警（假件面；列序对齐 schemas 真源）──────────────────────


def test_log_crisis_gate_row_column_order_and_insert():
    from schemas.categories.crisis_gate_log import INSERT_COLUMNS

    writer = RecordingWriter()
    cs = classify_crisis_state(_regime(dominant="r10"), warning_theta=0.5)
    ok = log_crisis_gate_row(
        trade_date=TRADE_DATE,
        crisis_state=cs,
        action_l1="blocked",
        action_l2="frozen_new",
        action_l3="entry_to_cash",
        probe_ts=__import__("datetime").datetime(2026, 9, 15, 1, 0, tzinfo=__import__("datetime").timezone.utc),
        writer=writer,
    )
    assert ok is True
    sql, rows = writer.calls[0]
    assert "c1_backtest.crisis_gate_log" in sql
    for col in ("probe_ts", "trade_date", "state", "p_r10", "dominant", "action_l1", "action_l2", "action_l3"):
        assert col in INSERT_COLUMNS and col in sql
    row = rows[0]
    assert (
        row[1] == __import__("datetime").date.fromisoformat(TRADE_DATE) and row[2] == STATE_CRISIS
    )  # B20：Date 列槽位契约=date 对象（str 断言即假绿通道，fullflow B20）
    assert (row[5], row[6], row[7]) == ("blocked", "frozen_new", "entry_to_cash")


def test_log_crisis_gate_row_failure_never_raises():
    cs = classify_crisis_state(_regime(), warning_theta=0.5)
    assert log_crisis_gate_row(trade_date=TRADE_DATE, crisis_state=cs, writer=RecordingWriter(fail=True)) is False


def test_alert_reuses_alerter_levels():
    alerter = RecordingAlerter()
    crisis = classify_crisis_state(_regime(dominant="r10"), warning_theta=0.5)
    warning = classify_crisis_state(_regime(dominant="r3", p_r10=0.6), warning_theta=0.5)
    normal = classify_crisis_state(_regime(), warning_theta=0.5)
    assert alert_crisis_level("l1", trade_date=TRADE_DATE, crisis_state=crisis, alerter=alerter)
    assert alert_crisis_level("l2", trade_date=TRADE_DATE, crisis_state=warning, alerter=alerter)
    assert alert_crisis_level("l3", trade_date=TRADE_DATE, crisis_state=normal, alerter=alerter)
    levels = {c[0]: c[2] for c in alerter.calls}
    assert levels["crisis_gate_l1"] == "CRITICAL"  # crisis 落 failure 文件的触发面
    assert levels["crisis_gate_l2"] == "WARN"
    assert "crisis_gate_l3" not in levels  # normal 不出声


def test_log_crisis_gate_row_date_column_serializable():
    """B20 治本回归：trade_date 列槽位必须入 date 对象（真驱动序列化契约）。

    fullflow B20 实证：str 字面量入 Date 列槽位→驱动取 value.year 抛 AttributeError
    →被 log_crisis_gate_row 的 except 吞成 warning→留痕静默蒸发；假 writer 只查列序
    查不到该缺陷，本用例直达行元组元素类型断言。
    """
    import datetime as _dt

    writer = RecordingWriter()
    cs = classify_crisis_state(_regime(), warning_theta=0.5)
    ok = log_crisis_gate_row(
        trade_date=TRADE_DATE,
        crisis_state=cs,
        probe_ts=_dt.datetime(2026, 9, 15, 1, 0, tzinfo=_dt.timezone.utc),
        writer=writer,
    )
    assert ok is True
    day = writer.calls[0][1][0][1]
    assert isinstance(day, _dt.date) and not isinstance(day, _dt.datetime)
    assert day.isoformat() == TRADE_DATE
    assert day.year == 2026  # 驱动序列化面：Date 列取 value.year 必须可行（B20 病根行）
