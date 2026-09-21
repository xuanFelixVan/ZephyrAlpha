# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] tests.ai_layer.intake.test_events
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.intake.intake_events (IntakeJournal, IntakeEvent, INTAKE_KINDS, PAYLOAD_REQUIRED_KEYS)
# [CONSUMERS] pytest tests/ai_layer/intake/test_events.py
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 全用例零 DB 零生产路径（journal 一律落 tmp_path，DEFAULT_STATE_DIR 永不触碰）；
#              KillSwitch 停消费行为经 monkeypatch 假探针覆盖（确定性），真实探针单测只断言形态不依赖环境状态；
#              毒丸路径全枚举：失败计 attempts→达 MAX_ATTEMPTS 留档→停自动消费→purge 唯一清除口
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §三（接线图=事件契约真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；emit 未知 kind/缺必填键的 ValueError 拒绝路径逐一落用例
# [TESTS] tests/ai_layer/intake/test_events.py
# [TTL] permanent
"""test_events - L2 事件层 journal emit/status/drain/毒丸/KillSwitch 验收（DESIGN 施工项 6）。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.ai_layer.intake import intake_events as ev_mod
from zephyr.ai_layer.intake.intake_events import (
    DEFAULT_STATE_DIR,
    EVENT_ID_PREFIX,
    INTAKE_KINDS,
    MAX_ATTEMPTS,
    PAYLOAD_REQUIRED_KEYS,
    IntakeEvent,
    IntakeJournal,
)


@pytest.fixture()
def journal(tmp_path: Path) -> IntakeJournal:
    """隔离 journal（tmp_path 状态目录，绝不触 DEFAULT_STATE_DIR）。"""
    return IntakeJournal(state_dir=tmp_path / "journal")


def _probe_always(clear: bool, why: str = "normal"):
    """构造恒定探针（替换模块级 probe_kill_switch，确定性覆盖停消费分支）。"""
    return lambda: (clear, why)


def test_seven_kinds_match_design_contract() -> None:
    assert {
        "intake_ingest_due",
        "intake_clean_due",
        "intake_reject_due",
        "intake_scored_due",
        "intake_e2_handoff",
        "intake_exam_receipt",
        "intake_kpi_alert",
    } == INTAKE_KINDS
    assert PAYLOAD_REQUIRED_KEYS["intake_ingest_due"] == ("source_slug", "raw_staging_path")
    assert PAYLOAD_REQUIRED_KEYS["intake_kpi_alert"] == ("scope", "key", "pass_rate", "action")


def test_emit_persists_journal_line_first(journal: IntakeJournal) -> None:
    evt = journal.emit("intake_clean_due", {"card_ids": ["CC-1"], "domain_id": "governance"})
    assert evt.id.startswith(EVENT_ID_PREFIX) and evt.attempts == 0 and not evt.poison
    assert journal.journal_path.exists(), "journal 先落盘（唯一真源）"
    lines = journal.journal_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    raw = json.loads(lines[0])
    assert raw["kind"] == "intake_clean_due" and raw["payload"]["card_ids"] == ["CC-1"]


def test_emit_rejects_unknown_kind_and_missing_keys(journal: IntakeJournal) -> None:
    with pytest.raises(ValueError, match="unknown_intake_kind"):
        journal.emit("not_a_kind", {})
    with pytest.raises(ValueError, match="payload_missing_keys:intake_clean_due"):
        journal.emit("intake_clean_due", {"card_ids": ["CC-1"]}), "缺 domain_id"
    with pytest.raises(ValueError, match="payload_missing_keys:intake_ingest_due"):
        journal.emit("intake_ingest_due", {})
    assert journal.pending() == [], "被拒事件绝不落半截"


def test_register_handler_rejects_unknown_kind(journal: IntakeJournal) -> None:
    with pytest.raises(ValueError, match="unknown_intake_kind"):
        journal.register_handler("typo_kind", lambda raw: {})


def test_status_counts_and_receipt(journal: IntakeJournal) -> None:
    journal.emit("intake_clean_due", {"card_ids": ["CC-1"], "domain_id": "governance"})
    journal.emit("intake_clean_due", {"card_ids": ["CC-2"], "domain_id": "trading_algo"})
    journal.emit("intake_scored_due", {"card_id": "CC-1", "verdict": "win", "score": 0.9})
    status = journal.status()
    assert status["pending"] == 3 and status["poison"] == 0
    assert status["by_kind"] == {"intake_clean_due": 2, "intake_scored_due": 1}
    assert status["receipt"] == {}, "未消费过无回执"
    assert status["journal"] == str(journal.journal_path)


def test_drain_processes_once_and_replay_is_noop(journal: IntakeJournal) -> None:
    for i in range(2):
        journal.emit("intake_clean_due", {"card_ids": [f"CC-{i}"], "domain_id": "governance"})
    calls: list[str] = []
    journal.register_handler("intake_clean_due", lambda raw: calls.append(raw["payload"]["card_ids"][0]) or {})
    receipt = journal.drain(max_events=10)
    assert len(receipt["processed"]) == 2 and receipt["pending_left"] == 0
    assert calls == ["CC-0", "CC-1"]
    again = journal.drain(max_events=10)
    assert again["processed"] == [] and calls == ["CC-0", "CC-1"], "重放零副作用"
    saved = json.loads(journal.receipt_path.read_text(encoding="utf-8"))
    assert saved["drained_at"] and saved["stop_reason"] is None


def test_drain_failure_bumps_attempts_until_poison(journal: IntakeJournal) -> None:
    journal.emit("intake_clean_due", {"card_ids": ["CC-bad"], "domain_id": "governance"})

    def boom(raw: dict) -> dict:
        raise RuntimeError("handler 炸了")

    journal.register_handler("intake_clean_due", boom)
    for round_no in range(1, MAX_ATTEMPTS):
        receipt = journal.drain(max_events=5)
        assert len(receipt["failed"]) == 1 and "RuntimeError" in receipt["failed"][0]["error"]
        evt = journal.pending()[0]
        assert evt.attempts == round_no and not evt.poison, "失败保留+计 attempts"
    final = journal.drain(max_events=5)
    assert len(final["failed"]) == 1
    evt = journal.pending()[0]
    assert evt.attempts == MAX_ATTEMPTS and evt.poison, "达 MAX_ATTEMPTS 判毒丸留档"
    assert evt.last_error.startswith("RuntimeError")


def test_poison_held_not_consumed_and_purge(journal: IntakeJournal) -> None:
    journal.emit("intake_clean_due", {"card_ids": ["CC-bad"], "domain_id": "governance"})

    def boom(raw: dict) -> dict:
        raise RuntimeError("x")

    journal.register_handler("intake_clean_due", boom)
    for _ in range(MAX_ATTEMPTS):
        journal.drain(max_events=5)
    poison = journal.pending()[0]
    assert poison.poison
    status = journal.status()
    assert status["poison"] == 1
    receipt = journal.drain(max_events=5)
    assert receipt["skipped"] and receipt["skipped"][0]["why"] == "poison_held"
    assert journal.pending() and journal.pending()[0].poison, "毒丸不被自动消费"
    assert journal.purge_poison(poison.id) is True, "人工处置删行是唯一清除口"
    assert journal.purge_poison("no-such-id") is False
    assert journal.pending() == []


def test_mixed_queue_consumes_healthy_and_holds_poison(journal: IntakeJournal) -> None:
    journal.emit("intake_scored_due", {"card_id": "CC-ok", "verdict": "win", "score": 0.9})
    journal.emit("intake_clean_due", {"card_ids": ["CC-bad"], "domain_id": "governance"})
    journal.register_handler("intake_scored_due", lambda raw: {"ok": True})

    def boom(raw: dict) -> dict:
        raise RuntimeError("x")

    journal.register_handler("intake_clean_due", boom)
    journal.drain(max_events=10)  # 第一条成功、第二条失败 break
    for _ in range(MAX_ATTEMPTS - 1):
        journal.drain(max_events=10)
    assert [e.poison for e in journal.pending()] == [True], "健康件已出队，仅毒丸在队"
    assert journal.pending()[0].attempts == MAX_ATTEMPTS


def test_drain_stops_on_kill_switch_and_keeps_events(journal: IntakeJournal, monkeypatch: pytest.MonkeyPatch) -> None:
    journal.emit("intake_clean_due", {"card_ids": ["CC-1"], "domain_id": "governance"})
    monkeypatch.setattr(ev_mod, "probe_kill_switch", _probe_always(False, "kill_switch=frozen"))
    receipt = journal.drain(max_events=5)
    assert receipt["stop_reason"] == "kill_switch=frozen"
    assert receipt["processed"] == [] and receipt["pending_left"] == 1, "停消费全量保留"


def test_drain_honors_max_events_budget(journal: IntakeJournal) -> None:
    for i in range(5):
        journal.emit("intake_scored_due", {"card_id": f"CC-{i}", "verdict": "win", "score": 0.5})
    journal.register_handler("intake_scored_due", lambda raw: {"ok": True})
    receipt = journal.drain(max_events=2)
    assert len(receipt["processed"]) == 2 and receipt["pending_left"] == 3


def test_default_handler_no_handler_branch(journal: IntakeJournal) -> None:
    out = journal.default_handler(
        {
            "id": "x",
            "kind": "intake_clean_due",
            "payload": {"card_ids": ["CC-1"], "domain_id": "governance"},
        }
    )
    assert out == {"accepted": False, "reason": "no_handler:intake_clean_due"}, "无落点 kind 显式回执"


def test_event_from_line_tolerates_missing_fields() -> None:
    evt = IntakeEvent.from_line({"id": "AINTAKE-1", "kind": "intake_clean_due"})
    assert evt.payload == {} and evt.attempts == 0 and not evt.poison and evt.last_error == ""
    assert "intake_clean_due" in evt.to_json()


def test_real_probe_returns_typed_tuple() -> None:
    """真实 KillSwitch 探针只断言形态（不依赖环境开关状态，停消费分支由假探针覆盖）。"""
    from zephyr.ai_layer.intake.intake_events import probe_kill_switch

    clear, why = probe_kill_switch()
    assert isinstance(clear, bool) and isinstance(why, str) and why
