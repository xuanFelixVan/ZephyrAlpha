# [A_test] module_id: SRC-TST-1824 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-454 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.audit_trail.test_audit_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: audit_core"""

import json
import os
import shutil
import tempfile

import pytest

from zephyr.gov_audit.models import (
    AuditEntryV1,
    AuditEventType,
    AuditMetrics,
    FileActionType,
    IntegrityReport,
    LamportClock,
    ProvenanceDepth,
    ProvenanceLevel,
    ProvenanceLight,
    ProvenanceStandard,
    TaskAuditSummary,
)
from zephyr.gov_audit.writer import AuditWriter


class TestAuditWriterCreation:
    @pytest.fixture()
    def tmp_dir(self):
        d = tempfile.mkdtemp(prefix="audit_test_")
        yield d
        shutil.rmtree(d, ignore_errors=True)

    def test_creation_creates_directory(self, tmp_dir):
        data_dir = os.path.join(tmp_dir, "audit_data")
        writer = AuditWriter(data_dir=data_dir)
        assert os.path.isdir(data_dir)

    def test_data_dir_property(self, tmp_dir):
        writer = AuditWriter(data_dir=tmp_dir)
        assert writer.data_dir == type(writer.data_dir)(tmp_dir)

    def test_initial_event_count_is_zero(self, tmp_dir):
        writer = AuditWriter(data_dir=tmp_dir)
        assert writer.event_count == 0

    def test_initial_lamport_time(self, tmp_dir):
        writer = AuditWriter(data_dir=tmp_dir, ide_source="test-ide")
        assert writer.lamport_time >= 0
        assert writer.ide_source == "test-ide"


class TestAuditWriterWrite:
    @pytest.fixture()
    def tmp_dir(self):
        d = tempfile.mkdtemp(prefix="audit_test_")
        yield d
        shutil.rmtree(d, ignore_errors=True)

    def test_write_returns_chain_hash(self, tmp_dir):
        writer = AuditWriter(data_dir=tmp_dir, enable_merkle=False)
        chain_hash = writer.write(
            {
                "event_type": "file_write",
                "agent_id": "test-agent",
                "operation": "write",
                "status": "success",
            }
        )
        assert isinstance(chain_hash, str)
        assert len(chain_hash) == 64

    def test_write_increments_event_count(self, tmp_dir):
        writer = AuditWriter(data_dir=tmp_dir, enable_merkle=False)
        writer.write({"event_type": "heartbeat", "agent_id": "a"})
        writer.write({"event_type": "heartbeat", "agent_id": "b"})
        assert writer.event_count == 2

    def test_write_increments_lamport_time(self, tmp_dir):
        writer = AuditWriter(data_dir=tmp_dir, enable_merkle=False)
        lt_before = writer.lamport_time
        writer.write({"event_type": "heartbeat", "agent_id": "a"})
        assert writer.lamport_time > lt_before

    def test_write_with_cot(self, tmp_dir):
        writer = AuditWriter(data_dir=tmp_dir, enable_merkle=False)
        result = writer.write_with_cot(
            {"event_type": "file_write", "agent_id": "a"},
            reasoning_trace="I decided to write because...",
        )
        assert "chain_hash" in result
        assert "cot_hash" in result

    def test_write_produces_jsonl(self, tmp_dir):
        writer = AuditWriter(data_dir=tmp_dir, enable_merkle=False)
        writer.write({"event_type": "file_write", "agent_id": "a"})
        writer.write({"event_type": "file_read", "agent_id": "b"})
        events_path = os.path.join(tmp_dir, "events.jsonl")
        assert os.path.exists(events_path)
        with open(events_path, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "entry_hash" in parsed

    def test_chain_hash_links_entries(self, tmp_dir):
        writer = AuditWriter(data_dir=tmp_dir, enable_merkle=False)
        writer.write({"event_type": "heartbeat", "agent_id": "a"})
        writer.write({"event_type": "heartbeat", "agent_id": "b"})
        events_path = os.path.join(tmp_dir, "events.jsonl")
        with open(events_path, encoding="utf-8") as f:
            lines = f.readlines()
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        assert second["prev_hash"] == first["entry_hash"]

    def test_merge_lamport(self, tmp_dir):
        writer = AuditWriter(data_dir=tmp_dir, enable_merkle=False)
        writer.write({"event_type": "heartbeat", "agent_id": "a"})
        current = writer.lamport_time
        new_lt = writer.merge_lamport(current + 10)
        assert new_lt == current + 11


class TestAuditModels:
    def test_audit_event_type_enum(self):
        assert AuditEventType.FILE_WRITE.value == "file_write"
        assert AuditEventType.FILE_READ.value == "file_read"
        assert AuditEventType.HEARTBEAT.value == "heartbeat"
        assert AuditEventType.UNKNOWN.value == "unknown"

    def test_provenance_depth_enum(self):
        assert ProvenanceDepth.LIGHT.value == "light"
        assert ProvenanceDepth.STANDARD.value == "standard"
        assert ProvenanceDepth.FULL.value == "full"

    def test_provenance_level_enum(self):
        assert ProvenanceLevel.DIRECT_AGENT.value == "direct_agent"
        assert ProvenanceLevel.DELEGATED.value == "delegated"

    def test_file_action_type_enum(self):
        assert FileActionType.READ.value == "read"
        assert FileActionType.WRITE.value == "write"
        assert FileActionType.CREATE.value == "create"
        assert FileActionType.DELETE.value == "delete"

    def test_provenance_light_creation(self):
        p = ProvenanceLight(
            agent_id="agent-1",
            timestamp="2026-01-01T00:00:00Z",
            action_type="write",
        )
        assert p.agent_id == "agent-1"

    def test_provenance_standard_creation(self):
        p = ProvenanceStandard(
            agent_id="agent-2",
            decision_basis=["rule-A", "rule-B"],
            guard_checks_passed=["G1"],
            guard_checks_failed=["G2"],
        )
        assert len(p.decision_basis) == 2
        assert len(p.guard_checks_failed) == 1

    def test_lamport_clock_tick(self):
        clock = LamportClock(ide_source="ide-A", counter=0)
        ide, counter = clock.tick()
        assert ide == "ide-A"
        assert counter == 1
        _, counter2 = clock.tick()
        assert counter2 == 2

    def test_lamport_clock_merge(self):
        clock = LamportClock(ide_source="ide-A", counter=5)
        result = clock.merge(("ide-B", 10))
        assert result == 11

    def test_lamport_clock_now(self):
        clock = LamportClock(ide_source="ide-A", counter=3)
        ide, counter = clock.now()
        assert ide == "ide-A"
        assert counter == 3

    def test_audit_entry_v1_defaults(self):
        entry = AuditEntryV1()
        assert entry.schema_version == "1.1.0"
        assert entry.event_type == AuditEventType.UNKNOWN
        assert entry.provenance == ProvenanceLevel.DIRECT_AGENT
        assert entry.dry_run is False

    def test_audit_entry_v1_custom(self):
        entry = AuditEntryV1(
            event_type=AuditEventType.FILE_WRITE,
            agent_id="test-agent",
            session_id="session-001",
            operation="write_file",
            status="success",
            target_path="/test/path.py",
        )
        assert entry.event_type == AuditEventType.FILE_WRITE
        assert entry.agent_id == "test-agent"

    def test_task_audit_summary_defaults(self):
        summary = TaskAuditSummary()
        assert summary.event_id == ""
        assert summary.provenance_depth == ProvenanceDepth.LIGHT

    def test_integrity_report_defaults(self):
        report = IntegrityReport()
        assert report.is_valid is True
        assert report.total_entries == 0
        assert report.hash_chain_breaks == []

    def test_audit_metrics_defaults(self):
        metrics = AuditMetrics()
        assert metrics.total_entries == 0
        assert metrics.write_events == 0
