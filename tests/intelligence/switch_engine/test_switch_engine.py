"""S4 switch_engine 验收测试：七态迁移全覆盖/非法边拒绝/回切单命令可逆/T1-T6 机检。"""

from __future__ import annotations

import pytest

from zephyr.intelligence.switch_engine.criteria import (
    CRITERIA_ROOT_KEY,
    load_criteria,
)
from zephyr.intelligence.switch_engine.switch_engine import (
    ACTION_AUTO_ROLLBACK,
    ACTION_BLOCK_PROMOTION,
    ACTION_FREEZE_SWITCH,
    ACTION_IMMEDIATE_ROLLBACK,
    ACTION_PAUSE_SHADOW,
    ACTION_ROLLBACK_REVIEW,
    EVENT_EDGES,
    SwitchTransitionError,
    SwitchEngine,
    evaluate_triggers,
)
from zephyr.intelligence.switch_engine.switch_registry import (
    SwitchRegistryRecord,
    SwitchRegistryStore,
)

_REAL_TRIGGERS: dict = load_criteria()[CRITERIA_ROOT_KEY]

_SIMPLE_CRITERIA: dict = {
    "t1_correctness_incidents_min": 1,
    "t2_disagreement_rate_max": 0.05,
    "t3_perf_delta_pct_max": 20,
    "t3_consecutive_trading_days": 5,
    "t4_cost_increase_pct_max": 15,
    "t4_requires_compensating_benefit": True,
}


@pytest.fixture()
def engine(store: SwitchRegistryStore, make_record) -> SwitchEngine:
    return SwitchEngine(store)


@pytest.fixture()
def opened(store: SwitchRegistryStore, make_record, engine: SwitchEngine) -> str:
    return engine.open_switch(make_record("SW-1")).switch_id


def _walk_to(store: SwitchRegistryStore, engine: SwitchEngine, target: str, switch_id: str) -> None:
    """沿合法边走到目标态（路径：shadow→canary→promoted→champion→retired→tombstone）。"""
    path = {
        "canary": ("graduate",),
        "promoted": ("graduate", "promote"),
        "champion": ("graduate", "promote", "stabilize"),
        "retired": ("graduate", "promote", "stabilize", "supersede"),
        "tombstone": ("graduate", "promote", "stabilize", "supersede", "seal"),
    }
    for event in path.get(target, ()):  # shadow 无需迁移
        if event == "promote":
            engine.promote(switch_id, approved_by="owner_one_click", receipt_ref="rcpt-1")
        else:
            engine.transition(switch_id, event, f"walk:{event}")


def test_open_switch_initial_shadow(engine: SwitchEngine, opened: str) -> None:
    record = engine.store.require(opened)
    assert record.state == "shadow"  # 影子不下真决策：开户恒 shadow
    assert record.state_history[-1]["state"] == "shadow"


def test_seven_state_full_edge_coverage(
    store: SwitchRegistryStore, engine: SwitchEngine, make_record
) -> None:
    """验收锚 S4：七态迁移全覆盖——EVENT_EDGES 每条边逐一走到并断言落点。"""
    covered_sources = {src for src, _ in EVENT_EDGES}
    assert covered_sources == {"shadow", "canary", "promoted", "champion", "retired", "tombstone"}
    for (source, event), target in sorted(EVENT_EDGES.items()):
        switch_id = f"SW-{source}-{event}"
        engine.open_switch(make_record(switch_id, object_ref=f"obj-{switch_id}"))
        _walk_to(store, engine, source, switch_id)
        assert engine.store.require(switch_id).state == source
        record = (
            engine.promote(switch_id, approved_by="auto", receipt_ref="rcpt")
            if event == "promote"
            else engine.transition(switch_id, event, f"cov:{event}")
        )
        assert record.state == target, f"边 {source}--{event}--> 未落 {target}"


def test_aborted_is_terminal(engine: SwitchEngine, opened: str) -> None:
    engine.transition(opened, "abort", "criteria-failed")
    assert engine.store.require(opened).state == "aborted"
    assert engine.legal_targets("aborted") == {}  # 终态无出边（重开=新 switch_id）
    with pytest.raises(SwitchTransitionError, match="表外迁移"):
        engine.transition(opened, "graduate", "zombie")


def test_illegal_edge_rejected(engine: SwitchEngine, opened: str) -> None:
    with pytest.raises(SwitchTransitionError, match="表外迁移"):
        engine.transition(opened, "promote", "skip-shadow")  # shadow 不可直提


def test_revert_promoted_single_command(
    engine: SwitchEngine, opened: str
) -> None:
    """验收锚 S4：回切单命令可逆 promoted→canary+消费指针还原。"""
    engine.transition(opened, "graduate", "green")
    engine.promote(opened, approved_by="owner_one_click", receipt_ref="rcpt-9")
    from zephyr.intelligence.switch_engine.switch_engine import active_ref

    assert active_ref(engine.store.require(opened)) == "session/st-demo"  # B 上岗
    reverted = engine.revert(opened, reason="T1-incident")
    assert reverted.state == "canary"
    assert reverted.rollback["plan_ref"].endswith("revert")
    assert reverted.rollback["reason"] == "T1-incident"
    assert active_ref(engine.store.require(opened)) == "main"  # 指针还原 A


def test_revert_canary_to_shadow(engine: SwitchEngine, opened: str) -> None:
    engine.transition(opened, "graduate", "green")
    assert engine.revert(opened, reason="T4-review").state == "shadow"


def test_revert_illegal_target_rejected(engine: SwitchEngine, opened: str) -> None:
    engine.transition(opened, "graduate", "green")
    engine.promote(opened, approved_by="auto", receipt_ref="r")
    with pytest.raises(SwitchTransitionError, match="目标态非法"):
        engine.revert(opened, reason="x", target_state="champion")


def test_promote_guards(engine: SwitchEngine, opened: str) -> None:
    with pytest.raises(SwitchTransitionError, match="仅可自 canary"):
        engine.promote(opened, approved_by="auto", receipt_ref="r")  # shadow 直提拒
    engine.transition(opened, "graduate", "green")
    with pytest.raises(ValueError, match="approved_by"):
        engine.promote(opened, approved_by="yolo", receipt_ref="r")
    with pytest.raises(ValueError, match="receipt_ref"):
        engine.promote(opened, approved_by="auto", receipt_ref="")
    record = engine.promote(opened, approved_by="independent_review", receipt_ref="r-1")
    assert record.promotion_record["approved_by"] == "independent_review"
    assert record.promotion_record["promoted_at"].endswith("+00:00")


def test_revert_plan_dry_run_no_mutation(
    store: SwitchRegistryStore, engine: SwitchEngine, opened: str
) -> None:
    engine.transition(opened, "graduate", "green")
    plan = engine.revert_plan(opened)
    assert plan == {
        "switch_id": opened, "from_state": "canary", "legal": True,
        "event": "rollback_to_shadow", "to_state": "shadow",
    }
    assert store.require(opened).state == "canary"  # dry-run 零状态变更


def _fired(verdicts, trigger: str):
    return next(v for v in verdicts if v.trigger == trigger)


def test_triggers_t1_t3_real_criteria() -> None:
    signals = {
        "correctness_incidents": 1,
        "perf_median_delta_pct": 25,
        "perf_degradation_days": 6,
    }
    verdicts = evaluate_triggers(signals, _REAL_TRIGGERS, "canary")
    assert _fired(verdicts, "T1").fired and _fired(verdicts, "T1").action == ACTION_IMMEDIATE_ROLLBACK
    assert _fired(verdicts, "T3").fired and _fired(verdicts, "T3").action == ACTION_AUTO_ROLLBACK
    below_days = evaluate_triggers(
        {"perf_median_delta_pct": 25, "perf_degradation_days": 3}, _REAL_TRIGGERS, "canary"
    )
    assert not _fired(below_days, "T3").fired  # 连续 5 交易日不满足不触发


def test_triggers_t2_state_dependent() -> None:
    signals = {"disagreement_rate": 0.06}
    shadow = evaluate_triggers(signals, _SIMPLE_CRITERIA, "shadow")
    canary = evaluate_triggers(signals, _SIMPLE_CRITERIA, "canary")
    assert _fired(shadow, "T2").action == ACTION_BLOCK_PROMOTION  # 影子期禁升 canary
    assert _fired(canary, "T2").action == ACTION_ROLLBACK_REVIEW  # canary 期回切审议
    within = evaluate_triggers({"disagreement_rate": 0.04}, _SIMPLE_CRITERIA, "canary")
    assert not _fired(within, "T2").fired


def test_triggers_t4_t5_t6() -> None:
    t4 = evaluate_triggers({"cost_increase_pct": 16}, _SIMPLE_CRITERIA, "promoted")
    assert _fired(t4, "T4").action == ACTION_ROLLBACK_REVIEW
    t4_offset = evaluate_triggers(
        {"cost_increase_pct": 16, "compensating_benefit_claimed": True},
        _SIMPLE_CRITERIA, "promoted",
    )
    assert not _fired(t4_offset, "T4").fired  # 有补偿收益主张不触发
    t5 = evaluate_triggers({"anomalous_gain": True}, _SIMPLE_CRITERIA, "shadow")
    assert _fired(t5, "T5").action == ACTION_FREEZE_SWITCH  # 好得反常 → 冻结+L4 三查
    t6 = evaluate_triggers({"quota_exceeded": True}, _SIMPLE_CRITERIA, "shadow")
    assert _fired(t6, "T6").action == ACTION_PAUSE_SHADOW  # 暂停影子，非回切


def test_triggers_no_signals_no_fire() -> None:
    """信号缺失=不触发不编造（机检诚实条款）。"""
    verdicts = evaluate_triggers({}, _SIMPLE_CRITERIA, "canary")
    assert all(not v.fired for v in verdicts)
    assert len(verdicts) == 6  # T1-T6 全量机检
