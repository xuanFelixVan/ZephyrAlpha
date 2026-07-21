# [A_test] module_id: MOD-GOV_event_store | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §event_store
# [MODULE] tests.test_event_store
# [INVARIANTS] EventStore.record必须返回event_id; StoredEvent.to_row/from_row必须可逆
# [MODIFY-GUARD] 仅当event_store公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_event_store.py -q
# [TTL] task_bound


from zephyr.infrastructure.event_store import (
    EVENT_STORE_SCHEMA,
    EventLevel,
    EventStore,
    StoredEvent,
)


class TestEventLevel:
    def test_values(self):
        assert EventLevel.DEBUG.value == "debug"
        assert EventLevel.INFO.value == "info"
        assert EventLevel.WARNING.value == "warning"
        assert EventLevel.ERROR.value == "error"
        assert EventLevel.CRITICAL.value == "critical"


class TestStoredEvent:
    def test_default_construction(self):
        event = StoredEvent(event_id="EVT-001")
        assert event.event_id == "EVT-001"
        assert event.level == EventLevel.INFO
        assert event.component == ""
        assert event.event_type == ""
        assert event.payload == {}
        assert event.metadata == {}

    def test_to_row_returns_tuple(self):
        event = StoredEvent(
            event_id="EVT-002",
            level=EventLevel.ERROR,
            component="gate_engine",
            event_type="validation_failed",
            payload={"key": "value"},
        )
        row = event.to_row()
        assert isinstance(row, tuple)
        assert row[0] == "EVT-002"
        assert row[2] == "error"
        assert row[3] == "gate_engine"

    def test_to_row_checksum(self):
        event = StoredEvent(event_id="EVT-003", payload={"data": "test"})
        row = event.to_row()
        assert row[7] != ""

    def test_from_row_roundtrip(self):
        original = StoredEvent(
            event_id="EVT-004",
            level=EventLevel.WARNING,
            component="test_comp",
            event_type="test_type",
            payload={"x": 1},
            metadata={"meta": True},
        )
        row = original.to_row()
        row_dict = {
            "event_id": row[0],
            "timestamp": row[1],
            "level": row[2],
            "component": row[3],
            "event_type": row[4],
            "payload": row[5],
            "metadata": row[6],
        }
        restored = StoredEvent.from_row(row_dict)
        assert restored.event_id == original.event_id
        assert restored.level == original.level
        assert restored.component == original.component
        assert restored.event_type == original.event_type
        assert restored.payload == original.payload
        assert restored.metadata == original.metadata


class TestEventStore:
    def test_instantiation(self, tmp_path):
        db = tmp_path / "test_events.db"
        store = EventStore(db_path=str(db))
        assert store is not None
        store.close()

    def test_record_and_query(self, tmp_path):
        db = tmp_path / "test_events.db"
        store = EventStore(db_path=str(db))
        event = StoredEvent(
            event_id="EVT-100",
            level=EventLevel.INFO,
            component="test",
            event_type="unit_test",
            payload={"action": "test"},
        )
        eid = store.record(event)
        assert eid == "EVT-100"
        results = store.query(component="test")
        assert len(results) == 1
        assert results[0].event_id == "EVT-100"
        store.close()

    def test_record_batch(self, tmp_path):
        db = tmp_path / "test_events.db"
        store = EventStore(db_path=str(db))
        events = [StoredEvent(event_id=f"EVT-B{i}", component="batch", event_type="test") for i in range(5)]
        count = store.record_batch(events)
        assert count == 5
        results = store.query(component="batch")
        assert len(results) == 5
        store.close()

    def test_record_batch_empty(self, tmp_path):
        db = tmp_path / "test_events.db"
        store = EventStore(db_path=str(db))
        count = store.record_batch([])
        assert count == 0
        store.close()

    def test_query_by_level(self, tmp_path):
        db = tmp_path / "test_events.db"
        store = EventStore(db_path=str(db))
        store.record(StoredEvent(event_id="EVT-L1", level=EventLevel.ERROR, component="c1"))
        store.record(StoredEvent(event_id="EVT-L2", level=EventLevel.INFO, component="c1"))
        results = store.query(level=EventLevel.ERROR)
        assert len(results) == 1
        assert results[0].event_id == "EVT-L1"
        store.close()

    def test_query_by_event_type(self, tmp_path):
        db = tmp_path / "test_events.db"
        store = EventStore(db_path=str(db))
        store.record(StoredEvent(event_id="EVT-T1", event_type="deploy", component="c2"))
        store.record(StoredEvent(event_id="EVT-T2", event_type="rollback", component="c2"))
        results = store.query(event_type="deploy")
        assert len(results) == 1
        store.close()

    def test_count(self, tmp_path):
        db = tmp_path / "test_events.db"
        store = EventStore(db_path=str(db))
        store.record(StoredEvent(event_id="EVT-C1", component="counter"))
        store.record(StoredEvent(event_id="EVT-C2", component="counter"))
        store.record(StoredEvent(event_id="EVT-C3", component="other"))
        assert store.count() == 3
        assert store.count(component="counter") == 2
        store.close()

    def test_verify_integrity(self, tmp_path):
        db = tmp_path / "test_events.db"
        store = EventStore(db_path=str(db))
        store.record(StoredEvent(event_id="EVT-V1", payload={"check": True}))
        assert store.verify_integrity("EVT-V1") is True
        assert store.verify_integrity("NONEXISTENT") is False
        store.close()

    def test_query_with_limit_and_offset(self, tmp_path):
        db = tmp_path / "test_events.db"
        store = EventStore(db_path=str(db))
        for i in range(10):
            store.record(StoredEvent(event_id=f"EVT-LO{i}", component="paged"))
        results = store.query(component="paged", limit=3, offset=0)
        assert len(results) == 3
        store.close()

    def test_schema_is_valid_sql(self):
        assert "CREATE TABLE" in EVENT_STORE_SCHEMA
        assert "events" in EVENT_STORE_SCHEMA
