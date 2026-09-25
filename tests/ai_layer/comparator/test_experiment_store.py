"""test_experiment_store — L4 实验卡库：三 guard 纯函数全枚举 + DDL 断言 + FakeConn 流转 + PG opt-in。"""

from __future__ import annotations

import re
from typing import Any

import pytest

from zephyr.ai_layer.comparator.experiment_store import (
    ALLOWED_TRANSITIONS,
    DEFAULT_SCHEMA,
    SCHEMA_RE,
    STATUS_FLOW,
    ExperimentDraft,
    ComparisonExperimentRecord,
    ExperimentStore,
    FrozenCriteriaError,
    ExperimentTransitionError,
    VerdictAppendOnlyError,
    canonical_criteria_text,
    check_frozen_update,
    check_schema_name,
    check_status_transition,
    check_verdict_append,
    criteria_hash,
    deploy,
    new_experiment_id,
    render_criteria_ref,
    verify,
)
from zephyr.ai_layer.comparator import VENUE_IDS

HASH64 = "a" * 64


# ---------------------------------------------------------------------------
# 纯函数：schema 白名单 / id 格式 / canonical 哈希
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("schema", ["ai_compare", "ai_compare_test_l4x"])
def test_schema_whitelist_accepts(schema: str) -> None:
    assert check_schema_name(schema) == schema


@pytest.mark.parametrize("schema", ["ai_intake", "ai_compare_evil; DROP", "AI_COMPARE", "", "ai_compare_test_"])
def test_schema_whitelist_rejects(schema: str) -> None:
    with pytest.raises(ValueError, match="schema 名不合规"):
        check_schema_name(schema)


def test_new_experiment_id_format() -> None:
    eid = new_experiment_id("20260923", "demo-slug1")
    assert eid == "EX-20260923-demo-slug1"


@pytest.mark.parametrize("day,slug", [("2026-9-23", "x"), ("", "x"), ("20260923", "UPPER"), ("20260923", "")])
def test_new_experiment_id_rejects(day: str, slug: str) -> None:
    with pytest.raises(ValueError):
        new_experiment_id(day, slug)


def test_render_criteria_ref_roundtrip() -> None:
    ref = render_criteria_ref("EX-20260923-demo", HASH64)
    assert ref == f"EX-20260923-demo#{HASH64}"
    with pytest.raises(ValueError, match="experiment_id"):
        render_criteria_ref("bad id", HASH64)
    with pytest.raises(ValueError, match="criteria_hash"):
        render_criteria_ref("EX-20260923-demo", "xyz")


def test_canonical_and_hash_deterministic() -> None:
    a = canonical_criteria_text({"b": 1, "a": [1, 2]})
    b = canonical_criteria_text({"a": [1, 2], "b": 1})
    assert a == b
    digest = criteria_hash(a)
    assert re.fullmatch(r"[0-9a-f]{64}", digest)
    assert criteria_hash(a + "\n") != digest


# ---------------------------------------------------------------------------
# 纯函数：三 guard 全枚举
# ---------------------------------------------------------------------------

def test_status_transition_enumerated() -> None:
    # 允许边恰好三条（frozen→running→verdict→archived 链）
    assert ALLOWED_TRANSITIONS == {
        "frozen": ("running",),
        "running": ("verdict",),
        "verdict": ("archived",),
    }
    assert check_status_transition("frozen", "running") == (True, "ok")
    assert check_status_transition("running", "verdict") == (True, "ok")
    assert check_status_transition("verdict", "archived") == (True, "ok")
    assert check_status_transition("frozen", "frozen") == (True, "no_op")
    for current, target in [
        ("frozen", "verdict"), ("frozen", "archived"), ("running", "archived"),
        ("running", "frozen"), ("verdict", "running"), ("archived", "verdict"),
        ("bogus", "running"),
    ]:
        ok, why = check_status_transition(current, target)
        assert not ok and why.startswith(("illegal_transition", "unknown_status")), (current, target)


def test_frozen_update_guard() -> None:
    assert check_frozen_update("criteria_yaml") == (False, "frozen_criteria_immutable:criteria_yaml")
    assert check_frozen_update("criteria_hash")[0] is False
    assert check_frozen_update("verdict")[0] is True
    assert check_frozen_update("evidence_ref")[0] is True


def test_verdict_append_only_guard() -> None:
    assert check_verdict_append(None, "win") == (True, "ok")
    ok, why = check_verdict_append("win", "loss")
    assert not ok and why == "verdict_append_only:win"
    ok, why = check_verdict_append(None, "victory")
    assert not ok and why == "unknown_verdict:victory"


# ---------------------------------------------------------------------------
# DDL 断言（离线：SQL 文本与包枚举同源护栏）
# ---------------------------------------------------------------------------

def test_ddl_contains_venue_enum_and_timestamptz() -> None:
    from zephyr.ai_layer.comparator.experiment_store import _SQL_TABLE

    for venue in VENUE_IDS:
        assert venue in _SQL_TABLE, venue
    assert _SQL_TABLE.count("TIMESTAMPTZ") >= 3  # created_at/frozen_at/updated_at（RULE-SCHEMA-TZ）
    assert "ai_comparison_experiment" in _SQL_TABLE


def test_ddl_statements_idempotent_render() -> None:
    stmts = None
    from zephyr.ai_layer.comparator.experiment_store import _ddl_statements

    stmts = _ddl_statements("ai_compare")
    assert stmts[0] == "CREATE SCHEMA IF NOT EXISTS ai_compare"
    assert any("DROP TRIGGER IF EXISTS" in s for s in stmts)
    assert any("frozen_criteria_immutable" in s for s in stmts)
    assert any("verdict_append_only" in s for s in stmts)


# ---------------------------------------------------------------------------
# FakeConn 注入：服务层流转逻辑（禁写生产路径，零 PG 依赖）
# ---------------------------------------------------------------------------

class FakeCursor:
    def __init__(self, row: tuple | None = None) -> None:
        self.executed: list[tuple[str, Any]] = []
        self._row = row
        self.description = tuple((name,) for name in (
            "experiment_id", "challenger_ref", "champion_ref", "venue_ref", "domain_id",
            "mechanism_family", "candidate_simhash", "criteria_yaml", "criteria_hash",
            "status", "fairness_fields", "verdict", "too_good_exit", "attribution",
            "rejection_reason", "evidence_ref", "verdict_log", "evaluator_session",
            "contractor_session", "dispatched_at", "first_commit_at", "created_at",
            "frozen_at", "updated_at",
        ))

    def execute(self, sql: str, params: Any = None) -> None:
        self.executed.append((sql.strip(), params))

    def fetchone(self) -> tuple | None:
        return self._row


class FakeWriteConn:
    def __init__(self) -> None:
        self.cursor_obj = FakeCursor()
        self.closed = False

    def cursor(self) -> FakeCursor:
        return self.cursor_obj


class FakeReadConn:
    def __init__(self, cursor_obj: FakeCursor) -> None:
        self._cursor = cursor_obj

    def cursor(self) -> FakeCursor:
        return self._cursor


class FakeService:
    """只注入只读连接（读路径经 DatabaseService 的契约形态）。"""

    def __init__(self, row: tuple | None) -> None:
        self.read_cursor = FakeCursor(row)

    def get_depgraph_conn(self, read_only: bool = True) -> FakeReadConn:
        assert read_only is True
        return FakeReadConn(self.read_cursor)


def _frozen_row(**over: Any) -> tuple:
    values = {
        "experiment_id": "EX-20260923-demo", "challenger_ref": "cand", "champion_ref": "champ",
        "venue_ref": "venue_c4", "domain_id": None, "mechanism_family": "optimization",
        "candidate_simhash": "111", "criteria_yaml": "a: 1\n", "criteria_hash": HASH64,
        "status": "frozen", "fairness_fields": "{}", "verdict": None, "too_good_exit": None,
        "attribution": None, "rejection_reason": None, "evidence_ref": None,
        "verdict_log": "[]", "evaluator_session": "eval-sid", "contractor_session": "ctor-sid",
        "dispatched_at": None, "first_commit_at": None, "created_at": "t", "frozen_at": "t",
        "updated_at": "t",
    }
    values.update(over)
    return tuple(values[c.name if hasattr(c, "name") else i] for i, c in enumerate(
        [type("C", (), {"name": n})() for n in (
            "experiment_id", "challenger_ref", "champion_ref", "venue_ref", "domain_id",
            "mechanism_family", "candidate_simhash", "criteria_yaml", "criteria_hash",
            "status", "fairness_fields", "verdict", "too_good_exit", "attribution",
            "rejection_reason", "evidence_ref", "verdict_log", "evaluator_session",
            "contractor_session", "dispatched_at", "first_commit_at", "created_at",
            "frozen_at", "updated_at",
        )]
    ))


def _store(row: tuple | None = None) -> tuple[ExperimentStore, FakeWriteConn]:
    write = FakeWriteConn()
    store = ExperimentStore(
        schema="ai_compare_test_unit", service=FakeService(row), write_conn=write
    )
    return store, write


def test_store_schema_whitelist_still_enforced() -> None:
    with pytest.raises(ValueError, match="schema 名不合规"):
        ExperimentStore(schema="ai_intake")


def _draft(**over: Any) -> ExperimentDraft:
    values: dict = {
        "experiment_id": "EX-20260923-demo", "challenger_ref": "cand",
        "champion_ref": "champ", "venue_ref": "venue_c4",
        "evaluator_session": "eval-sid", "contractor_session": "ctor-sid",
    }
    values.update(over)
    return ExperimentDraft(**values)  # type: ignore[arg-type]


def test_freeze_rejects_session_collision_and_bad_venue() -> None:
    store, _ = _store()
    with pytest.raises(ValueError, match="session_mutuality_violation"):
        store.freeze(_draft(evaluator_session="same", contractor_session="same"), {})
    with pytest.raises(ValueError, match="未知考场"):
        store.freeze(_draft(venue_ref="venue_x"), {})
    with pytest.raises(ValueError, match="缺必填字段"):
        store.freeze(_draft(challenger_ref=""), {})


def test_freeze_writes_canonical_and_hash() -> None:
    row = _frozen_row(criteria_yaml="a: 1\n", criteria_hash=criteria_hash("a: 1\n"))
    store, write = _store(row)
    record = store.freeze(_draft(), {"a": 1})
    sql, params = write.cursor_obj.executed[0]
    assert "INSERT INTO ai_compare_test_unit.ai_comparison_experiment" in sql
    assert params["criteria_yaml"] == "a: 1\n"
    assert params["criteria_hash"] == criteria_hash("a: 1\n")
    assert isinstance(record, ComparisonExperimentRecord)
    assert record.status == "frozen"


def test_store_transition_machine_via_fake() -> None:
    row = _frozen_row()
    store, write = _store(row)
    ok, why = store.transition("EX-20260923-demo", "running")
    assert ok and why == "ok"
    sql, params = write.cursor_obj.executed[0]
    assert "SET status = %s" in sql and params[0] == "running"
    with pytest.raises(ExperimentTransitionError, match="illegal_transition:frozen->archived"):
        store.transition("EX-20260923-demo", "archived")


def test_store_set_verdict_append_only_and_e3_attribution() -> None:
    store, write = _store(_frozen_row())
    ok, _ = store.set_verdict("EX-20260923-demo", "win", evidence_ref="ev1")
    assert ok
    sql, params = write.cursor_obj.executed[0]
    assert "verdict_log = verdict_log || %s::jsonb" in sql
    store2, _ = _store(_frozen_row(verdict="win"))
    with pytest.raises(VerdictAppendOnlyError, match="verdict_append_only:win"):
        store2.set_verdict("EX-20260923-demo", "loss")
    store3, _ = _store(_frozen_row())
    with pytest.raises(ValueError, match="归因三选一"):
        store3.set_verdict("EX-20260923-demo", "rejected_too_good")
    with pytest.raises(ValueError, match="too_good_exit"):
        store3.set_verdict("EX-20260923-demo", "win", too_good_exit="E9")


def test_store_archive_requires_verdict() -> None:
    store, _ = _store(_frozen_row(verdict=None))
    with pytest.raises(ValueError, match="archive_requires_verdict"):
        store.archive("EX-20260923-demo")


def test_store_get_returns_none_when_missing() -> None:
    store, _ = _store(None)
    assert store.get("EX-20260923-none") is None


# ---------------------------------------------------------------------------
# PG opt-in（真 DDL、真触发器；临时 schema，session 级清理）
# ---------------------------------------------------------------------------


def _pg_draft(experiment_id: str) -> ExperimentDraft:
    return ExperimentDraft(
        experiment_id=experiment_id,
        challenger_ref="cand-v1",
        champion_ref="champ-current",
        venue_ref="venue_replay",
        evaluator_session="eval-sid",
        contractor_session="ctor-sid",
    )


def test_pg_deploy_verify_and_full_lifecycle(test_schema: str) -> None:
    ok, missing = verify(test_schema)
    assert ok and not missing
    store = ExperimentStore(schema=test_schema)
    try:
        eid = "EX-20260923-pglife"
        record = store.freeze(_pg_draft(eid), {"P1": 0, "P3": 0.98})
        assert record.status == "frozen"
        assert record.criteria_hash == criteria_hash(canonical_criteria_text({"P1": 0, "P3": 0.98}))
        assert store.transition(eid, "running") == (True, "ok")
        assert store.transition(eid, "verdict") == (True, "ok")
        assert store.set_verdict(eid, "win", evidence_ref="ev-001")[0]
        assert store.archive(eid) == (True, "ok")
        archived = store.get(eid)
        assert archived is not None and archived.status == "archived" and archived.verdict == "win"
        assert len(store.list_archived()) == 1
    finally:
        store.close()


def test_pg_frozen_criteria_update_rejected_by_trigger(test_schema: str) -> None:
    store = ExperimentStore(schema=test_schema)
    try:
        eid = "EX-20260923-pgfrozen"
        store.freeze(_pg_draft(eid), {"k": "v"})
        with pytest.raises(Exception, match="frozen_criteria_immutable"):
            store.write_conn().cursor().execute(
                f"UPDATE {test_schema}.ai_comparison_experiment "
                "SET criteria_yaml = %s WHERE experiment_id = %s",
                ("tampered: true\n", eid),
            )
        app_guard = check_frozen_update("criteria_yaml")
        assert app_guard[0] is False  # 应用层同判（双道）
    finally:
        store.close()


def test_pg_verdict_append_only_by_trigger(test_schema: str) -> None:
    store = ExperimentStore(schema=test_schema)
    try:
        eid = "EX-20260923-pgappend"
        store.freeze(_pg_draft(eid), {"k": "v"})
        store.transition(eid, "running")
        store.transition(eid, "verdict")
        store.set_verdict(eid, "draw")
        with pytest.raises(Exception, match="verdict_append_only"):
            store.write_conn().cursor().execute(
                f"UPDATE {test_schema}.ai_comparison_experiment "
                "SET verdict = 'win' WHERE experiment_id = %s",
                (eid,),
            )
    finally:
        store.close()


def test_pg_illegal_status_transition_by_trigger(test_schema: str) -> None:
    store = ExperimentStore(schema=test_schema)
    try:
        eid = "EX-20260923-pgstatus"
        store.freeze(_pg_draft(eid), {"k": "v"})
        with pytest.raises(Exception, match="illegal_status_transition"):
            store.write_conn().cursor().execute(
                f"UPDATE {test_schema}.ai_comparison_experiment "
                "SET status = 'archived' WHERE experiment_id = %s",
                (eid,),
            )
        with pytest.raises(ValueError, match="archive_requires_verdict"):
            store.archive(eid)
    finally:
        store.close()


def test_pg_deploy_idempotent_and_default_schema_regex(test_schema: str) -> None:
    n1 = deploy(test_schema)
    n2 = deploy(test_schema)
    assert n1 == n2  # 幂等（语句数稳定）
    assert SCHEMA_RE.match(DEFAULT_SCHEMA)
    assert STATUS_FLOW == ("frozen", "running", "verdict", "archived")
