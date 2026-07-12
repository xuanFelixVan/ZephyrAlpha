# [A_test] module_id: SRC-TST-0869 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_event_store_stress.py — Event Store 压力测试（DW-0006）

测试场景：
1. 100 并发写入者同时追加事件
2. 事件回放正确性
3. 完整性校验
4. ProjectionEngine 折叠正确性
5. SnapshotManager 快照 + 增量回放
6. GateEventAdapter gate 事件追加
"""

from __future__ import annotations

import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest

from zephyr.governance.audit_trail.event_store import EventStore
from zephyr.governance.persistence.sqlite_schema import SchemaManager
from zephyr.governance.observability_governance.projection_engine import ProjectionEngine
from zephyr.governance.audit.snapshot_manager import SnapshotManager

# gate_event_adapter 真源在 zephyr.gov_enforcement.behavioral_admission.gate_event_adapter（DW-0006 已补全）
gate_event_adapter_mod = pytest.importorskip("zephyr.gov_enforcement.behavioral_admission.gate_event_adapter")
GateEventAdapter = gate_event_adapter_mod.GateEventAdapter


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_event_store.db"


@pytest.fixture()
def store(db_path: Path) -> EventStore:
    SchemaManager.ensure_task_events_table(db_path)
    s = EventStore(db_path, auto_init=False)
    yield s
    s.close()


@pytest.fixture()
def projection(db_path: Path) -> ProjectionEngine:
    SchemaManager.ensure_task_events_table(db_path)
    p = ProjectionEngine(db_path)
    yield p
    p.close()


@pytest.fixture()
def snapshot_mgr(db_path: Path) -> SnapshotManager:
    SchemaManager.ensure_task_events_table(db_path)
    sm = SnapshotManager(db_path, auto_init=False)
    yield sm
    sm.close()


@pytest.fixture()
def gate_adapter(db_path: Path) -> GateEventAdapter:
    SchemaManager.ensure_task_events_table(db_path)
    ga = GateEventAdapter(db_path)
    yield ga
    ga.close()


class TestEventStoreBasic:
    def test_append_and_replay(self, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        eid1 = store.append_event(task_id, "CREATED", {"title": "Test task"})
        eid2 = store.append_event(task_id, "STATUS_CHANGED", {"status": "IN_PROGRESS"})
        eid3 = store.append_event(task_id, "PRIORITY_CHANGED", {"priority": "P1"})

        events = store.replay_events(task_id)
        assert len(events) == 3
        assert events[0].event_type == "CREATED"
        assert events[1].event_type == "STATUS_CHANGED"
        assert events[2].event_type == "PRIORITY_CHANGED"
        assert events[0].event_id == eid1

    def test_append_with_string_payload(self, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", '{"key": "value"}')
        events = store.replay_events(task_id)
        assert len(events) == 1
        assert json.loads(events[0].payload) == {"key": "value"}

    def test_append_with_none_payload(self, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", None)
        events = store.replay_events(task_id)
        assert len(events) == 1
        assert json.loads(events[0].payload) == {}

    def test_replay_empty(self, store: EventStore) -> None:
        events = store.replay_events("NONEXISTENT-TASK")
        assert events == []

    def test_verify_integrity_valid(self, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {"title": "Test"})
        store.append_event(task_id, "STATUS_CHANGED", {"status": "IN_PROGRESS"})

        result = store.verify_integrity(task_id)
        assert result["valid"] is True
        assert result["event_count"] == 2
        assert result["errors"] == []

    def test_verify_integrity_empty(self, store: EventStore) -> None:
        result = store.verify_integrity("NONEXISTENT-TASK")
        assert result["valid"] is True
        assert result["event_count"] == 0

    def test_session_id_stored(self, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {}, session_id="session-20260523-001")
        events = store.replay_events(task_id)
        assert events[0].session_id == "session-20260523-001"

    def test_session_id_none(self, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {})
        events = store.replay_events(task_id)
        assert events[0].session_id is None


class TestProjectionEngine:
    def test_fold_created(self, projection: ProjectionEngine, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {"title": "Test", "status": "PENDING"})
        state = projection.fold_to_current_state(task_id)
        assert state["title"] == "Test"
        assert state["status"] == "PENDING"

    def test_fold_status_changed(self, projection: ProjectionEngine, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {"title": "Test", "status": "PENDING"})
        store.append_event(task_id, "STATUS_CHANGED", {"status": "IN_PROGRESS"})
        state = projection.fold_to_current_state(task_id)
        assert state["status"] == "IN_PROGRESS"

    def test_fold_priority_changed(self, projection: ProjectionEngine, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {"title": "Test", "priority": "P2"})
        store.append_event(task_id, "PRIORITY_CHANGED", {"priority": "P0"})
        state = projection.fold_to_current_state(task_id)
        assert state["priority"] == "P0"

    def test_fold_field_updated(self, projection: ProjectionEngine, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {"title": "Test"})
        store.append_event(task_id, "FIELD_UPDATED", {"field": "description", "value": "Updated"})
        state = projection.fold_to_current_state(task_id)
        assert state["description"] == "Updated"

    def test_fold_unknown_event_type(self, projection: ProjectionEngine, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {"title": "Test"})
        store.append_event(task_id, "CUSTOM_EVENT", {"data": "ignored"})
        state = projection.fold_to_current_state(task_id)
        assert state["title"] == "Test"
        assert "data" not in state

    def test_fold_empty_events(self, projection: ProjectionEngine) -> None:
        state = projection.fold_to_current_state("NONEXISTENT-TASK")
        assert state == {"task_id": "NONEXISTENT-TASK"}


class TestSnapshotManager:
    def test_create_and_load(self, snapshot_mgr: SnapshotManager) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        state = {"task_id": task_id, "status": "IN_PROGRESS", "priority": "P1"}
        snapshot_mgr.create_snapshot(task_id, state)

        loaded = snapshot_mgr.load_latest_snapshot(task_id)
        assert loaded is not None
        assert loaded["status"] == "IN_PROGRESS"
        assert loaded["priority"] == "P1"

    def test_load_nonexistent(self, snapshot_mgr: SnapshotManager) -> None:
        loaded = snapshot_mgr.load_latest_snapshot("NONEXISTENT-TASK")
        assert loaded is None

    def test_get_replay_start_with_snapshot(self, snapshot_mgr: SnapshotManager, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {"title": "Test", "status": "PENDING"})
        store.append_event(task_id, "STATUS_CHANGED", {"status": "IN_PROGRESS"})

        events_before = store.replay_events(task_id)
        last_ev = events_before[-1]

        state = {
            "task_id": task_id,
            "status": "IN_PROGRESS",
            "_last_event_timestamp": last_ev.timestamp,
            "_last_event_id": last_ev.event_id,
        }
        snapshot_mgr.create_snapshot(task_id, state)

        store.append_event(task_id, "STATUS_CHANGED", {"status": "COMPLETED"})

        snap_state, events_after = snapshot_mgr.get_replay_start(task_id)
        assert snap_state["status"] == "IN_PROGRESS"
        assert len(events_after) >= 1
        assert events_after[-1].event_type == "STATUS_CHANGED"

    def test_get_replay_start_no_snapshot(self, snapshot_mgr: SnapshotManager, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {"title": "Test"})

        snap_state, events_after = snapshot_mgr.get_replay_start(task_id)
        assert snap_state == {}
        assert len(events_after) == 1

    def test_latest_snapshot_wins(self, snapshot_mgr: SnapshotManager) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        snapshot_mgr.create_snapshot(task_id, {"status": "PENDING"})
        snapshot_mgr.create_snapshot(task_id, {"status": "COMPLETED"})

        loaded = snapshot_mgr.load_latest_snapshot(task_id)
        assert loaded["status"] == "COMPLETED"


class TestGateEventAdapter:
    def test_append_gate_passed(self, gate_adapter: GateEventAdapter) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        eid = gate_adapter.append_gate_event(task_id, "G1", True, session_id="s1")
        assert eid is not None

        gate_events = gate_adapter.query_gate_events(task_id)
        assert len(gate_events) == 1
        assert gate_events[0]["event_type"] == "GATE_PASSED"

    def test_append_gate_failed(self, gate_adapter: GateEventAdapter) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        gate_adapter.append_gate_event(task_id, "G7", False, details={"violations": ["missing test"]})

        gate_events = gate_adapter.query_gate_events(task_id)
        assert len(gate_events) == 1
        assert gate_events[0]["event_type"] == "GATE_FAILED"
        payload = json.loads(gate_events[0]["payload"])
        assert payload["gate_id"] == "G7"
        assert payload["details"]["violations"] == ["missing test"]

    def test_query_filters_non_gate(self, gate_adapter: GateEventAdapter, store: EventStore) -> None:
        task_id = f"DW-{uuid.uuid4().hex[:8]}"
        store.append_event(task_id, "CREATED", {"title": "Test"})
        gate_adapter.append_gate_event(task_id, "G1", True)

        gate_events = gate_adapter.query_gate_events(task_id)
        assert len(gate_events) == 1
        assert gate_events[0]["event_type"] == "GATE_PASSED"


class TestConcurrentWriters:
    def test_100_concurrent_writers(self, db_path: Path) -> None:
        SchemaManager.ensure_task_events_table(db_path)
        task_id = "DW-STRESS-001"
        num_writers = 100
        events_per_writer = 10
        total_expected = num_writers * events_per_writer

        def writer(worker_id: int) -> list[str]:
            store = EventStore(db_path, auto_init=False)
            event_ids: list[str] = []
            try:
                for i in range(events_per_writer):
                    eid = store.append_event(
                        task_id=task_id,
                        event_type="FIELD_UPDATED",
                        payload={"field": f"worker_{worker_id}_iter_{i}", "value": i},
                        session_id=f"worker-{worker_id}",
                    )
                    event_ids.append(eid)
            finally:
                store.close()
            return event_ids

        all_event_ids: list[str] = []
        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = {pool.submit(writer, w): w for w in range(num_writers)}
            for future in as_completed(futures):
                worker_id = futures[future]
                try:
                    ids = future.result(timeout=60)
                    all_event_ids.extend(ids)
                except Exception as exc:
                    pytest.fail(f"Worker {worker_id} failed: {exc}")

        assert len(all_event_ids) == total_expected

        store = EventStore(db_path, auto_init=False)
        try:
            events = store.replay_events(task_id)
            assert len(events) == total_expected

            result = store.verify_integrity(task_id)
            assert result["valid"] is True, f"Integrity errors: {result['errors']}"
            assert result["event_count"] == total_expected

            unique_ids = {ev.event_id for ev in events}
            assert len(unique_ids) == total_expected
        finally:
            store.close()

    def test_concurrent_different_tasks(self, db_path: Path) -> None:
        SchemaManager.ensure_task_events_table(db_path)
        num_tasks = 50
        events_per_task = 5

        def task_writer(task_idx: int) -> str:
            task_id = f"DW-CONC-{task_idx:04d}"
            store = EventStore(db_path, auto_init=False)
            try:
                store.append_event(task_id, "CREATED", {"title": f"Task {task_idx}"})
                for i in range(events_per_task - 1):
                    store.append_event(
                        task_id,
                        "FIELD_UPDATED",
                        {"field": f"field_{i}", "value": i},
                    )
            finally:
                store.close()
            return task_id

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(task_writer, i) for i in range(num_tasks)]
            task_ids = []
            for future in as_completed(futures):
                try:
                    tid = future.result(timeout=60)
                    task_ids.append(tid)
                except Exception as exc:
                    pytest.fail(f"Task writer failed: {exc}")

        assert len(task_ids) == num_tasks

        store = EventStore(db_path, auto_init=False)
        try:
            for task_id in task_ids:
                events = store.replay_events(task_id)
                assert len(events) == events_per_task
                assert events[0].event_type == "CREATED"
        finally:
            store.close()


class TestSchemaManager:
    def test_ensure_task_events_table(self, db_path: Path) -> None:
        SchemaManager.ensure_task_events_table(db_path)
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_events'")
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_idempotent(self, db_path: Path) -> None:
        SchemaManager.ensure_task_events_table(db_path)
        SchemaManager.ensure_task_events_table(db_path)
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_events'")
            assert cursor.fetchone() is not None
        finally:
            conn.close()
