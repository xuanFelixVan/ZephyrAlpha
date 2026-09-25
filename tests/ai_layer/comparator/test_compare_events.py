"""test_compare_events — C8 L7 接线：事件白名单/journal 先落盘/drain 幂等+毒丸/归档触发沿/先验只读。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import zephyr.ai_layer.comparator.compare_events as ce
from zephyr.ai_layer.comparator.compare_events import (
    ARCHIVED_KIND,
    CompareJournal,
    MAX_ATTEMPTS,
    archive_and_notify,
    comparison_prior_query,
)
from zephyr.ai_layer.comparator.experiment_store import ComparisonExperimentRecord


@pytest.fixture()
def journal(tmp_path: Path) -> CompareJournal:
    return CompareJournal(state_dir=tmp_path / "ai_compare")


def _record(**over: Any) -> ComparisonExperimentRecord:
    values: dict = {
        "experiment_id": "EX-20260923-arch", "challenger_ref": "cand", "champion_ref": "champ",
        "venue_ref": "venue_c4", "criteria_yaml": "a: 1\n", "criteria_hash": "a" * 64,
        "status": "archived", "evaluator_session": "eval", "contractor_session": "ctor",
        "verdict": "win",
    }
    values.update(over)
    return ComparisonExperimentRecord(**values)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# emit：白名单 + 必填键 + journal 先落盘
# ---------------------------------------------------------------------------

def test_emit_rejects_unknown_kind_and_missing_keys(journal: CompareJournal, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown_compare_kind"):
        journal.emit("intake_scored_due", {"card_id": "x"})
    with pytest.raises(ValueError, match="payload_missing_keys"):
        journal.emit(ARCHIVED_KIND, {"experiment_id": "EX-1"})  # 缺 verdict
    assert journal.pending() == []  # 拒 emit 零落盘（不落半截事件）


def test_emit_writes_journal_first(journal: CompareJournal, tmp_path: Path) -> None:
    evt = journal.emit(ARCHIVED_KIND, {"experiment_id": "EX-20260923-arch", "verdict": "win"})
    assert evt.id.startswith("CMPARE-")
    journal_path = tmp_path / "ai_compare" / "pending_events.jsonl"
    assert journal_path.exists()  # journal 先落盘（唯一真源）
    pending = journal.pending()
    assert len(pending) == 1 and pending[0].kind == ARCHIVED_KIND
    assert pending[0].payload["verdict"] == "win"


def test_register_handler_rejects_unknown_kind(journal: CompareJournal) -> None:
    with pytest.raises(ValueError, match="unknown_compare_kind"):
        journal.register_handler("nope", lambda raw: {})


# ---------------------------------------------------------------------------
# drain：成功出队 / 失败留队+计数 / 毒丸留档 / 缺消费者留队 / KillSwitch fail-closed
# ---------------------------------------------------------------------------

def test_drain_success_dequeues_and_receipt(journal: CompareJournal) -> None:
    journal.emit(ARCHIVED_KIND, {"experiment_id": "EX-1", "verdict": "win"})
    seen: list[dict[str, Any]] = []
    receipt = journal.drain(handler=lambda raw: seen.append(raw) or {"ok": True})
    assert seen and seen[0]["kind"] == ARCHIVED_KIND
    assert receipt["processed"] and receipt["pending_left"] == 0
    assert journal.pending() == []  # 幂等：成功才出队


def test_drain_failure_retains_and_poisons_after_max(journal: CompareJournal) -> None:
    journal.emit(ARCHIVED_KIND, {"experiment_id": "EX-1", "verdict": "win"})

    def boom(raw: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("l7_down")

    for i in range(MAX_ATTEMPTS):
        receipt = journal.drain(handler=boom)
        assert receipt["failed"] and receipt["pending_left"] == 1
    events = journal.pending()
    assert events[0].poison is True and events[0].attempts == MAX_ATTEMPTS  # 毒丸留档
    assert journal.status()["poison"] == 1
    # 毒丸不再自动消费（正常事件插队也被处理，毒丸原地保留）
    journal.emit(ARCHIVED_KIND, {"experiment_id": "EX-2", "verdict": "draw"})
    receipt = journal.drain(handler=lambda raw: {"ok": True})
    assert receipt["pending_left"] == 1  # 只剩毒丸


def test_drain_without_consumer_retains_event(journal: CompareJournal) -> None:
    """L7 消费体缺席：事件滞留 journal 等消费（缺消费者≠丢事件）。"""
    journal.emit(ARCHIVED_KIND, {"experiment_id": "EX-1", "verdict": "win"})
    receipt = journal.drain()  # 默认 handler → RuntimeError(no_consumer_yet)
    assert receipt["failed"]
    assert "no_consumer_yet" in receipt["failed"][0]["error"]
    assert receipt["pending_left"] == 1


def test_drain_stops_on_kill_switch(journal: CompareJournal, monkeypatch: pytest.MonkeyPatch) -> None:
    journal.emit(ARCHIVED_KIND, {"experiment_id": "EX-1", "verdict": "win"})
    monkeypatch.setattr(ce, "probe_kill_switch", lambda: (False, "kill_switch=test"))
    receipt = journal.drain(handler=lambda raw: {"ok": True})
    assert receipt["stop_reason"] == "kill_switch=test"
    assert receipt["pending_left"] == 1  # 全保留待恢复重放


# ---------------------------------------------------------------------------
# 归档触发沿（事件触发零定时器：archive 成功 → emit）
# ---------------------------------------------------------------------------

class FakeStore:
    def __init__(self, record: ComparisonExperimentRecord | None) -> None:
        self._record = record

    def get(self, experiment_id: str) -> ComparisonExperimentRecord | None:
        return self._record

    def archive(self, experiment_id: str) -> tuple[bool, str]:
        if self._record is None or not self._record.verdict:
            raise ValueError(f"archive_requires_verdict:{experiment_id}")
        self._record = _record(status="archived")
        return True, "ok"


def test_archive_and_notify_emits_with_full_payload(tmp_path: Path) -> None:
    store, journal = FakeStore(_record()), CompareJournal(state_dir=tmp_path / "ai_compare")
    evt = archive_and_notify(store, journal, "EX-20260923-arch")  # type: ignore[arg-type]
    assert evt.kind == ARCHIVED_KIND
    assert evt.payload["experiment_id"] == "EX-20260923-arch"
    for key in ("verdict", "criteria_hash", "criteria_yaml", "attribution", "too_good_exit"):
        assert key in evt.payload  # DESIGN §3 载荷契约


def test_archive_and_notify_requires_verdict(tmp_path: Path) -> None:
    store = FakeStore(_record(verdict=None, status="verdict"))
    with pytest.raises(ValueError, match="archive_requires_verdict"):
        archive_and_notify(store, CompareJournal(state_dir=tmp_path), "EX-20260923-arch")


def test_archive_and_notify_missing_card(tmp_path: Path) -> None:
    with pytest.raises(KeyError, match="experiment_not_found"):
        archive_and_notify(FakeStore(None), CompareJournal(state_dir=tmp_path), "EX-404")


# ---------------------------------------------------------------------------
# comparison_prior_query：只读 + 过滤 + L7 委托注入位
# ---------------------------------------------------------------------------

class FakeQueryStore:
    def __init__(self, records: list[ComparisonExperimentRecord]) -> None:
        self.records = records

    def list_archived(self) -> list[ComparisonExperimentRecord]:
        return self.records


def test_prior_query_filters_by_family_and_simhash() -> None:
    records = [
        _record(experiment_id="EX-1", mechanism_family="optimization", candidate_simhash="111"),
        _record(experiment_id="EX-2", mechanism_family="ranking", candidate_simhash="222"),
    ]
    out = comparison_prior_query(store=FakeQueryStore(records))  # type: ignore[arg-type]
    assert [r["experiment_id"] for r in out] == ["EX-1", "EX-2"]
    by_family = comparison_prior_query(mechanism_family="optimization", store=FakeQueryStore(records))  # type: ignore[arg-type]
    assert [r["experiment_id"] for r in by_family] == ["EX-1"]
    by_sim = comparison_prior_query(candidate_simhash="222", store=FakeQueryStore(records))  # type: ignore[arg-type]
    assert [r["experiment_id"] for r in by_sim] == ["EX-2"]


def test_prior_query_delegates_to_remote_l7_service() -> None:
    def remote(**kw: Any) -> list[dict[str, Any]]:
        return [{"experiment_id": "EX-L7", "queried": kw}]

    out = comparison_prior_query(
        mechanism_family="ranking", candidate_simhash="42", remote_query=remote,
    )
    assert out[0]["experiment_id"] == "EX-L7"
    assert out[0]["queried"] == {"mechanism_family": "ranking", "candidate_simhash": "42"}
