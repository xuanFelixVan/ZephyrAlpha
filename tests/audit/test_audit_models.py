# [A_test] module_id: SRC-TST-0358 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_models
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_audit.models import (
    AuditChain,
    AuditEntryV1,
    AuditEventType,
    AuditMetrics,
    FileActionType,
    FileAuditDetail,
    IntegrityRecord,
    IntegrityReport,
    LamportClock,
    ProvenanceDepth,
    ProvenanceFull,
    ProvenanceLevel,
    ProvenanceLight,
    ProvenanceStandard,
    TaskAuditSummary,
    _generate_entry_id,
    audit_entry_sort_key,
)


class TestAuditEventType:
    def test_enum_values(self):
        assert AuditEventType.FILE_WRITE.value == "file_write"
        assert AuditEventType.ANOMALY_DETECTED.value == "anomaly_detected"
        assert AuditEventType.UNKNOWN.value == "unknown"

    def test_enum_count(self):
        assert len(AuditEventType) >= 29


class TestProvenanceDepth:
    def test_values(self):
        assert ProvenanceDepth.LIGHT.value == "light"
        assert ProvenanceDepth.STANDARD.value == "standard"
        assert ProvenanceDepth.FULL.value == "full"


class TestProvenanceLevel:
    def test_values(self):
        assert ProvenanceLevel.DIRECT_AGENT.value == "direct_agent"
        assert ProvenanceLevel.DELEGATED.value == "delegated"
        assert ProvenanceLevel.INDIRECT.value == "indirect"


class TestProvenanceLight:
    def test_create(self):
        p = ProvenanceLight(agent_id="a1", timestamp="2026-01-01", action_type="write")
        assert p.agent_id == "a1"
        assert p.action_type == "write"

    def test_defaults(self):
        p = ProvenanceLight()
        assert p.agent_id == ""
        assert p.ide_source == ""


class TestProvenanceStandard:
    def test_create(self):
        p = ProvenanceStandard(
            agent_id="a1",
            timestamp="2026-01-01",
            decision_basis=["rule1"],
            guard_checks_passed=["g1"],
            guard_checks_failed=["g2"],
        )
        assert p.decision_basis == ["rule1"]
        assert p.guard_checks_passed == ["g1"]
        assert p.guard_checks_failed == ["g2"]


class TestProvenanceFull:
    def test_create(self):
        p = ProvenanceFull(
            agent_id="a1",
            blocked_reason="unauthorized",
            escalation_triggered=True,
        )
        assert p.blocked_reason == "unauthorized"
        assert p.escalation_triggered is True


class TestFileActionType:
    def test_values(self):
        assert FileActionType.READ.value == "read"
        assert FileActionType.WRITE.value == "write"
        assert FileActionType.CREATE.value == "create"
        assert FileActionType.DELETE.value == "delete"


class TestTaskAuditSummary:
    def test_create(self):
        t = TaskAuditSummary(event_id="E1", agent_id="a1", task_id="T1")
        assert t.event_id == "E1"
        assert t.agent_id == "a1"

    def test_frozen(self):
        t = TaskAuditSummary(event_id="E1")
        with pytest.raises(Exception):
            t.event_id = "E2"

    def test_default_provenance_depth(self):
        t = TaskAuditSummary()
        assert t.provenance_depth == ProvenanceDepth.LIGHT


class TestFileAuditDetail:
    def test_create(self):
        f = FileAuditDetail(event_id="F1", file_path="/tmp/test.py", action_type=FileActionType.WRITE)
        assert f.file_path == "/tmp/test.py"
        assert f.action_type == FileActionType.WRITE

    def test_frozen(self):
        f = FileAuditDetail(event_id="F1")
        with pytest.raises(Exception):
            f.event_id = "F2"


class TestLamportClock:
    def test_tick(self):
        clock = LamportClock(ide_source="ide-1")
        ide, counter = clock.tick()
        assert ide == "ide-1"
        assert counter == 1
        _, counter2 = clock.tick()
        assert counter2 == 2

    def test_merge(self):
        clock = LamportClock(ide_source="ide-1", counter=5)
        result = clock.merge(("ide-2", 10))
        assert result == 11

    def test_now(self):
        clock = LamportClock(ide_source="ide-1", counter=3)
        ide, counter = clock.now()
        assert ide == "ide-1"
        assert counter == 3

    def test_merge_lower_received(self):
        clock = LamportClock(ide_source="ide-1", counter=10)
        result = clock.merge(("ide-2", 3))
        assert result == 11


class TestAuditEntryV1:
    def test_create_default(self):
        entry = AuditEntryV1()
        assert entry.schema_version == "1.1.0"
        assert entry.event_type == AuditEventType.UNKNOWN
        assert entry.provenance == ProvenanceLevel.DIRECT_AGENT

    def test_create_with_fields(self):
        entry = AuditEntryV1(
            agent_id="a1",
            event_type=AuditEventType.FILE_WRITE,
            target_path="/tmp/test.py",
        )
        assert entry.agent_id == "a1"
        assert entry.event_type == AuditEventType.FILE_WRITE

    def test_frozen(self):
        entry = AuditEntryV1()
        with pytest.raises(Exception):
            entry.agent_id = "modified"


class TestGenerateEntryId:
    def test_generates_id(self):
        eid = _generate_entry_id("AUD-T", 0)
        assert eid.startswith("AUD-T-")
        assert eid.endswith("-0000")

    def test_different_seq(self):
        eid = _generate_entry_id("AUD-F", 5)
        assert eid.endswith("-0005")


class TestAuditEntrySortKey:
    def test_sort_order(self):
        key1 = audit_entry_sort_key(("ide-1", 1))
        key2 = audit_entry_sort_key(("ide-1", 2))
        assert key1 < key2


class TestIntegrityReport:
    def test_defaults(self):
        report = IntegrityReport()
        assert report.is_valid is True
        assert report.total_entries == 0
        assert report.hash_chain_breaks == []


class TestAuditChain:
    def test_create(self):
        chain = AuditChain(chain_hash="abc", entry_count=5)
        assert chain.chain_hash == "abc"
        assert chain.entry_count == 5


class TestIntegrityRecord:
    def test_create(self):
        rec = IntegrityRecord(record_id="R1", chain_hash="abc")
        assert rec.record_id == "R1"


class TestAuditMetrics:
    def test_defaults(self):
        metrics = AuditMetrics()
        assert metrics.total_entries == 0
        assert metrics.write_events == 0
