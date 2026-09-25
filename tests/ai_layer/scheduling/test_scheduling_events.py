# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] tests.ai_layer.scheduling.test_events
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_events — C3 验收：8 kind 白名单/必填键/journal 先落盘/drain 幂等/毒丸/KillSwitch fail-closed。"""

from __future__ import annotations

import json
from typing import Any

import pytest

import zephyr.ai_layer.scheduling.scheduling_events as se
from zephyr.ai_layer.scheduling.scheduling_events import (
    KIND_WORK_ORDER_DEAD,
    KIND_WORK_ORDER_SHADOW_READY,
    MAX_ATTEMPTS,
    PAYLOAD_REQUIRED_KEYS,
    SCHEDULING_KINDS,
    SchedulingJournal,
)


@pytest.fixture()
def j(tmp_path: Any) -> SchedulingJournal:
    return SchedulingJournal(state_dir=tmp_path / "ai_scheduling")


def test_eight_kinds_registered() -> None:
    """C3 验收：恰好 8 个轻 kind（红蓝 R3 补 3 项、R4 计数校正 8）。"""
    assert len(SCHEDULING_KINDS) == 8
    for kind in (
        "evolution_winner_due",
        "order_created_due",
        "order_confirmed_due",
        "order_dispatch_due",
        "order_deferred_due",
        "work_order_shadow_ready",
        "work_order_closed_due",
        "work_order_dead",
    ):
        assert kind in SCHEDULING_KINDS


def test_emit_rejects_unknown_kind_and_missing_keys(j: SchedulingJournal) -> None:
    with pytest.raises(ValueError, match="unknown_scheduling_kind"):
        j.emit("intake_scored_due", {"card_id": "x"})
    with pytest.raises(ValueError, match="payload_missing_keys"):
        j.emit(KIND_WORK_ORDER_DEAD, {"work_order_id": "WO-1"})  # 缺 reason
    assert j.pending() == []  # 拒 emit 零落盘（不落半截事件）


def test_emit_writes_journal_first(j: SchedulingJournal, tmp_path: Any) -> None:
    evt = j.emit(KIND_WORK_ORDER_DEAD, {"work_order_id": "WO-1", "reason": "3 次派工失败"})
    assert evt.id.startswith("SCHED-")
    path = tmp_path / "ai_scheduling" / "pending_events.jsonl"
    assert path.exists()  # journal 先落盘（唯一真源）
    pending = j.pending()
    assert len(pending) == 1 and pending[0].kind == KIND_WORK_ORDER_DEAD


def test_shadow_ready_payload_contract() -> None:
    """L6 关单契约七键已锁（DESIGN §3 只消费不改造）。"""
    assert PAYLOAD_REQUIRED_KEYS[KIND_WORK_ORDER_SHADOW_READY] == (
        "work_order_id",
        "module_id",
        "challenger_branch",
        "criteria_yaml_ref",
        "criteria_hash",
        "domain",
        "tier_action",
    )


def test_register_handler_rejects_unknown_kind(j: SchedulingJournal) -> None:
    with pytest.raises(ValueError, match="unknown_scheduling_kind"):
        j.register_handler("nope", lambda raw: {})


def test_drain_success_dequeues_and_receipt(j: SchedulingJournal) -> None:
    j.emit(KIND_WORK_ORDER_DEAD, {"work_order_id": "WO-1", "reason": "r"})
    seen: list[dict[str, Any]] = []
    receipt = j.drain(handler=lambda raw: seen.append(raw) or {"ok": True})
    assert seen and seen[0]["kind"] == KIND_WORK_ORDER_DEAD
    assert receipt["processed"] and receipt["pending_left"] == 0
    assert j.pending() == []  # 幂等：成功才出队


def test_drain_failure_retains_and_poisons_after_max(j: SchedulingJournal) -> None:
    j.emit(KIND_WORK_ORDER_DEAD, {"work_order_id": "WO-1", "reason": "r"})

    def boom(raw: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("l6_down")

    for _ in range(MAX_ATTEMPTS):
        receipt = j.drain(handler=boom)
        assert receipt["failed"] and receipt["pending_left"] == 1
    events = j.pending()
    assert events[0].poison is True and events[0].attempts == MAX_ATTEMPTS  # 毒丸留档
    assert j.status()["poison"] == 1
    # 毒丸不再自动消费（新事件插队被处理，毒丸原地保留）
    j.emit(KIND_WORK_ORDER_DEAD, {"work_order_id": "WO-2", "reason": "r"})
    receipt = j.drain(handler=lambda raw: {"ok": True})
    assert receipt["pending_left"] == 1  # 只剩毒丸


def test_purge_poison_manual_only(j: SchedulingJournal) -> None:
    j.emit(KIND_WORK_ORDER_DEAD, {"work_order_id": "WO-1", "reason": "r"})
    for _ in range(MAX_ATTEMPTS):
        j.drain(handler=lambda raw: (_ for _ in ()).throw(RuntimeError("down")))
    assert j.purge_poison(j.pending()[0].id) is True  # 人工清除唯一合法入口
    assert j.pending() == []
    assert j.purge_poison("nonexistent") is False


def test_drain_without_consumer_retains_event(j: SchedulingJournal) -> None:
    """L6/L7 消费体缺席：事件滞留 journal（缺消费者≠丢事件）。"""
    j.emit(KIND_WORK_ORDER_DEAD, {"work_order_id": "WO-1", "reason": "r"})
    receipt = j.drain()  # 默认 handler → RuntimeError(no_consumer_yet)
    assert receipt["failed"]
    assert "no_consumer_yet" in receipt["failed"][0]["error"]
    assert receipt["pending_left"] == 1


def test_drain_stops_on_kill_switch(j: SchedulingJournal, monkeypatch: pytest.MonkeyPatch) -> None:
    j.emit(KIND_WORK_ORDER_DEAD, {"work_order_id": "WO-1", "reason": "r"})
    monkeypatch.setattr(se, "probe_kill_switch", lambda: (False, "kill_switch=test"))
    receipt = j.drain(handler=lambda raw: {"ok": True})
    assert receipt["stop_reason"] == "kill_switch=test"
    assert receipt["pending_left"] == 1  # fail-closed：全保留待恢复重放


def test_json_round_trip(j: SchedulingJournal) -> None:
    evt = j.emit("order_deferred_due", {"order_id": "WO-1", "reason": "Q1 满"})
    line = json.loads(j.journal_path.read_text(encoding="utf-8").splitlines()[0])
    assert line["payload"]["reason"] == "Q1 满"  # 中文原样落盘（ensure_ascii=False）
    assert evt.to_json()
