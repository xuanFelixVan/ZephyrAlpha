# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] tests.ai_layer.heritage.test_heritage_events
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.heritage.heritage_events; zephyr.ai_layer.heritage.store
# [CONSUMERS] pytest tests/ai_layer/heritage/test_heritage_events.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 三事件合成载荷→正确动作计划（纯函数零 DB）；胜局双条目/aborted 缺陷/retired 降级三分支；
#              journal 用 tmp_path 注入（禁写 .runtime 生产态）；毒丸 MAX_ATTEMPTS=3 留档；
#              KillSwitch 非 normal 停消费全量保留（monkeypatch 探针）；DB 用例只写临时 schema
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §三（事件契约真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知 kind/缺必填键 emit 拒；断言失败即红
# [TESTS] tests/ai_layer/heritage/test_heritage_events.py
# [TTL] permanent
"""test_heritage_events - 三回写边事件消费验收（DESIGN 施工项 5）。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import zephyr.ai_layer.heritage.heritage_events as he
from zephyr.ai_layer.heritage.heritage_events import (
    MAX_ATTEMPTS,
    HeritageJournal,
    closure_payload_to_actions,
    comparison_payload_to_actions,
    parse_no_new_pattern,
    switch_payload_to_actions,
)

SWITCH_WIN: dict[str, object] = {
    "switch_id": "SW-20260920-001",
    "outcome": "promoted",
    "domain_id": "trading_algo",
    "winner_ref": "MOD-W-1",
    "loser_ref": "MOD-W-0",
    "diff_summary": "胜者把信号确认窗从固定 3 根改为波动自适应，回撤更小而胜率不降，双窗成绩稳定",
    "criteria_ref": "EX-20260918-abc",
    "criteria_hash": "a" * 64,
    "mechanism_family": "prediction",
    "title": "胜局档案",
    "plain_zh": "胜者档案与判据快照双条目回流，供组合素材与防重复考古",
}

CMP_WIN: dict[str, object] = {
    "experiment_id": "EX-20260918-bcd",
    "criteria_hash": "b" * 64,
    "venue": "venue_c4",
    "verdict": "win",
    "why_win": "IS 双窗一致且置换检验显著，判据冻结哈希随实验卡归档",
    "domain_id": "governance",
    "winner_ref": "MOD-G-1",
    "diff_summary": "抽词方式从整串匹配改为 token 重叠加权，边界样本误判率下降且吞吐不降",
    "mechanism_family": "detection",
    "title": "实验裁定回流",
    "plain_zh": "实验归档判据快照与胜者档案，判据翻案后此快照仍是史实",
}

WO_KNOWN: dict[str, object] = {
    "work_order_id": "WO-20260917-001",
    "kind": "defect_fix",
    "heritage_ref": "HT-20260923-003",
    "plain_zh": "工单关单回执引用新建缺陷模式条目，登记由关单流经 store 完成",
}
WO_RECUR: dict[str, object] = {
    "work_order_id": "WO-20260917-002",
    "kind": "incident_fix",
    "no_new_pattern": "known_pattern: HT-20260923-003",
}


class FakeStore:
    """动作计划执行记录器（零 DB）。"""

    def __init__(self) -> None:
        self.registered: list[object] = []
        self.transitions: list[tuple[str, str]] = []
        self.occurrences: list[tuple[str, str]] = []

    def register(self, draft: object, **_kw: object) -> str:
        self.registered.append(draft)
        return f"HT-20260923-{len(self.registered):03d}"

    def transition_status(self, entry_id: str, target: str, *, note: str = "") -> str:
        self.transitions.append((entry_id, target))
        return f"demote:{target}"

    def record_occurrence(self, entry_id: str, source_ref: str, **_kw: object) -> int:
        self.occurrences.append((entry_id, source_ref))
        return 2


def _journal_with(tmp_path: Path, store: FakeStore) -> HeritageJournal:
    return HeritageJournal(state_dir=tmp_path, store=store)  # type: ignore[arg-type]


# ---------------------------------------------------------------- 纯函数（payload→动作计划）


def test_switch_win_yields_elite_and_criteria() -> None:
    actions = switch_payload_to_actions(SWITCH_WIN)
    kinds = [a.draft.entry_kind for a in actions if a.action == "register"]
    assert kinds == ["elite", "criteria"], "胜局→elite+criteria 双条目"


def test_switch_aborted_routes_defect_or_skip() -> None:
    aborted = {
        "switch_id": "SW-20260920-002", "outcome": "aborted", "domain_id": "trading_algo",
        "root_cause": "回撤控制缺位", "signature": "drawdown>.*无止损", "recipe": "补止损闸+回放验证长度足够差异",
        "pattern_norm": "missing_stop_gate", "affected_surfaces": ["src/x.py"],
        "title": "败因", "plain_zh": "切换败因带根因回流为缺陷模式，防同坑重踩",
    }
    actions = switch_payload_to_actions(aborted)
    assert len(actions) == 1 and actions[0].action == "register"
    assert actions[0].draft.entry_kind == "defect"
    incomplete = dict(aborted, recipe="")
    actions2 = switch_payload_to_actions(incomplete)
    assert actions2[0].action == "skip"


def test_switch_retired_demotes_entry() -> None:
    actions = switch_payload_to_actions(
        {"switch_id": "SW-1", "outcome": "retired", "domain_id": "governance",
         "heritage_entry_id": "HT-20260920-001", "title": "退役", "plain_zh": "对象退役触发精英降级信号回流"}
    )
    assert actions[0].action == "demote" and actions[0].target_status == "archived"
    no_map = switch_payload_to_actions(
        {"switch_id": "SW-2", "outcome": "retired", "domain_id": "governance",
         "title": "退役", "plain_zh": "无映射条目的退役事件跳过降级并留痕"}
    )
    assert no_map[0].action == "skip"


def test_switch_unknown_outcome_rejected() -> None:
    with pytest.raises(ValueError, match="unknown_switch_outcome"):
        switch_payload_to_actions({"switch_id": "SW-3", "outcome": "bogus", "domain_id": "governance"})


def test_comparison_win_yields_criteria_and_elite() -> None:
    actions = comparison_payload_to_actions(CMP_WIN)
    kinds = [a.draft.entry_kind for a in actions if a.action == "register"]
    assert kinds == ["criteria", "elite"], "criteria 条目+win 时 elite 条目"
    loss = dict(CMP_WIN, verdict="loss")
    kinds_loss = [a.draft.entry_kind for a in comparison_payload_to_actions(loss) if a.action == "register"]
    assert kinds_loss == ["criteria"], "非 win 只出 criteria"


def test_closure_payload_routes() -> None:
    actions = closure_payload_to_actions(WO_KNOWN)
    assert actions[0].action == "noop", "新建缺陷回执=登记已由关单流完成，回执仅校验不重复累加"
    known = closure_payload_to_actions(WO_RECUR)
    assert known[0].action == "occurrence" and known[0].entry_id == "HT-20260923-003"
    debt = closure_payload_to_actions(
        {"work_order_id": "WO-3", "kind": "incident_fix", "no_new_pattern": "mechanical_debt"}
    )
    assert debt[0].action == "noop"
    with pytest.raises(ValueError, match="closure_receipt_invalid"):
        closure_payload_to_actions({"work_order_id": "WO-4", "kind": "incident_fix"})
    with pytest.raises(ValueError, match="closure_receipt_invalid"):
        closure_payload_to_actions({"work_order_id": "WO-5", "kind": "defect_fix"})


def test_parse_no_new_pattern_two_shapes() -> None:
    assert parse_no_new_pattern("known_pattern: HT-1") == ("known_pattern", "HT-1")
    assert parse_no_new_pattern({"reason": "dup_of", "ref": "CASE-2026-1"}) == ("dup_of", "CASE-2026-1")
    assert parse_no_new_pattern("mechanical_debt") == ("mechanical_debt", None)


# ---------------------------------------------------------------- journal（tmp_path 注入）


def test_emit_validates_kind_and_keys(tmp_path: Path) -> None:
    journal = HeritageJournal(state_dir=tmp_path, store=FakeStore())
    with pytest.raises(ValueError, match="unknown_heritage_kind"):
        journal.emit("bogus_kind", {})
    with pytest.raises(ValueError, match="payload_missing_keys"):
        journal.emit("switch_archived_due", {"switch_id": "SW-1"})
    event = journal.emit("switch_archived_due", dict(SWITCH_WIN))
    assert event.id.startswith("AHERIT-")
    assert len(journal.pending()) == 1


def test_drain_executes_actions_and_empties_journal(tmp_path: Path) -> None:
    store = FakeStore()
    journal = _journal_with(tmp_path, store)
    journal.emit("switch_archived_due", dict(SWITCH_WIN))
    receipt = journal.drain()
    assert len(receipt["processed"]) == 1 and receipt["pending_left"] == 0
    kinds = [d.entry_kind for d in store.registered]
    assert kinds == ["elite", "criteria"], "合成载荷→正确生成 elite/criteria 条目"


def test_drain_work_order_closure_paths(tmp_path: Path) -> None:
    store = FakeStore()
    journal = _journal_with(tmp_path, store)
    journal.emit("work_order_closed_due", dict(WO_KNOWN))
    journal.emit("work_order_closed_due", dict(WO_RECUR))
    journal.drain()
    assert store.registered == [], "事件层不代登记（登记走关单流 store.register）"
    assert store.occurrences == [("HT-20260923-003", "WO-20260917-002")], "known_pattern 复发 occurrence+1"


def test_poison_after_max_attempts(tmp_path: Path) -> None:
    journal = HeritageJournal(state_dir=tmp_path, store=FakeStore())

    def always_fail(raw: dict[str, object]) -> dict[str, object]:
        raise RuntimeError("boom")

    journal.emit("work_order_closed_due", {"work_order_id": "WO-9", "kind": "feature_dev"})
    for _ in range(MAX_ATTEMPTS):
        receipt = journal.drain(handler=always_fail)
        assert len(receipt["failed"]) == 1
    events = journal.pending()
    assert events[0].poison and events[0].attempts == MAX_ATTEMPTS, "毒丸 MAX_ATTEMPTS=3 留档"
    receipt = journal.drain(handler=always_fail)
    assert receipt["processed"] == [] and receipt["skipped"][0]["why"] == "poison_held"
    assert journal.purge_poison(events[0].id) is True
    assert journal.pending() == []


def test_kill_switch_stops_consumption_and_retains_all(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(he, "probe_kill_switch", lambda: (False, "kill_switch=test"))
    journal = _journal_with(tmp_path, FakeStore())
    journal.emit("work_order_closed_due", {"work_order_id": "WO-1", "kind": "feature_dev"})
    receipt = journal.drain()
    assert receipt["stop_reason"] == "kill_switch=test"
    assert receipt["pending_left"] == 1, "非 normal 停消费全量保留"
    assert (tmp_path / "pending_events.jsonl").exists()


def test_journal_status_shape(tmp_path: Path) -> None:
    journal = _journal_with(tmp_path, FakeStore())
    journal.emit("work_order_closed_due", {"work_order_id": "WO-1", "kind": "feature_dev"})
    status = journal.status()
    assert status["pending"] == 1 and status["by_kind"] == {"work_order_closed_due": 1}


# ---------------------------------------------------------------- DB（临时 schema，验收合成载荷→真条目）


def _pg_reachable() -> bool:
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        get_depgraph_pg_connection(read_only=True).cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001
        return False


needs_pg = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")


@needs_pg
def test_switch_event_creates_real_entries(heritage_schema: str, tmp_path: Path) -> None:
    from zephyr.ai_layer.heritage.store import HeritageStore

    store = HeritageStore(
        heritage_schema,
        state_dir=tmp_path / "state",
        domain_lookup=lambda domain: True,
        l4_hash_lookup=lambda exp: "a" * 64 if exp == "EX-20260918-abc" else None,
    )
    journal = HeritageJournal(state_dir=tmp_path / "journal", store=store)
    journal.emit("switch_archived_due", dict(SWITCH_WIN))
    receipt = journal.drain()
    assert receipt["pending_left"] == 0 and not receipt["failed"], receipt
    assert len(store.snapshot_faces()["elite"]) == 1
    conn = store.read_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT count(*) AS n FROM {heritage_schema}.ai_heritage_entry")
    assert cur.fetchone()["n"] == 2, "胜局→elite+criteria 双条目落库"
    with (tmp_path / "journal" / "last_receipt.json").open(encoding="utf-8") as handle:
        saved = json.load(handle)
    assert saved["processed"][0]["result"]["actions"][0]["entry_id"].startswith("HT-")
