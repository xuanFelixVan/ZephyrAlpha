# [A_test] module_id: MOD-GOV_rollback_audit_nexus | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_audit_nexus
# [INVARIANTS] audit_log不可变追加;event_id唯一;success_rate=success/total
# [MODIFY-GUARD] blueprint.md §4;src/zephyr/rollback/__init__.py
# [CONSUMERS] CI;pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError;json.JSONDecodeError;OSError
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

from zephyr.infrastructure.rollback.rollback_audit_nexus import (
    AuditEvent,
    RollbackAuditNexus,
)


class TestAuditEvent:
    def test_instantiation(self):
        e = AuditEvent(
            event_id="RB-AUDIT-001",
            event_type="rollback",
            timestamp_utc="2026-01-01T00:00:00",
            operator="agent-1",
            module="MOD-INF-021",
            target_commit="abc123",
            result_commit="def456",
            success=True,
        )
        assert e.event_id == "RB-AUDIT-001"
        assert e.event_type == "rollback"
        assert e.success is True
        assert e.details == {}

    def test_instantiation_with_details(self):
        e = AuditEvent(
            event_id="RB-AUDIT-002",
            event_type="rollback",
            timestamp_utc="2026-01-01T00:00:00",
            operator="agent-2",
            module="MOD-INF-021",
            target_commit="aaa",
            result_commit="bbb",
            success=False,
            details={"error": "timeout", "files": ["a.py"]},
        )
        assert e.details["error"] == "timeout"
        assert e.success is False


class TestRollbackAuditNexus:
    def test_instantiation_with_path(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        assert nexus._project_root == tmp_path
        assert nexus._nexus_log.parent.exists()

    def test_instantiation_default(self):
        nexus = RollbackAuditNexus()
        assert nexus._project_root == Path.cwd()

    def test_publish_creates_log_file(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        event = AuditEvent(
            event_id="RB-001",
            event_type="rollback",
            timestamp_utc="2026-01-01T00:00:00",
            operator="agent-1",
            module="MOD-INF-021",
            target_commit="abc",
            result_commit="def",
            success=True,
        )
        nexus.publish(event)
        assert nexus._nexus_log.exists()
        lines = nexus._nexus_log.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["event_id"] == "RB-001"
        assert record["success"] is True

    def test_publish_appends_multiple(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        for i in range(3):
            event = AuditEvent(
                event_id=f"RB-{i:03d}",
                event_type="rollback",
                timestamp_utc="2026-01-01T00:00:00",
                operator="agent-1",
                module="MOD-INF-021",
                target_commit="abc",
                result_commit="def",
                success=True,
            )
            nexus.publish(event)
        lines = nexus._nexus_log.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3

    def test_create_event(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        event = nexus.create_event(
            event_type="rollback",
            operator="agent-1",
            target_commit="abc123",
            result_commit="def456",
            success=True,
            details={"reason": "test"},
        )
        assert event.event_id.startswith("RB-AUDIT-")
        assert event.event_type == "rollback"
        assert event.operator == "agent-1"
        assert event.success is True
        assert event.details == {"reason": "test"}
        assert nexus._nexus_log.exists()

    def test_create_event_default_details(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        event = nexus.create_event(
            event_type="rollback",
            operator="agent-2",
            target_commit="aaa",
            result_commit="bbb",
            success=False,
        )
        assert event.details == {}
        assert event.success is False

    def test_generate_summary_empty(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        summary = nexus.generate_summary()
        assert summary["total_events"] == 0
        assert summary["success_rate"] == 0.0

    def test_generate_summary_with_events(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        nexus.create_event("rollback", "a1", "c1", "c2", success=True)
        nexus.create_event("rollback", "a2", "c3", "c4", success=False)
        nexus.create_event("rollback", "a3", "c5", "c6", success=True)
        summary = nexus.generate_summary()
        assert summary["total_events"] == 3
        assert summary["success_count"] == 2
        assert abs(summary["success_rate"] - 2.0 / 3.0) < 1e-9
        assert "rollback" in summary["events_by_type"]
        assert summary["events_by_type"]["rollback"] == 3

    def test_generate_summary_writes_file(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        nexus.create_event("rollback", "a1", "c1", "c2", success=True)
        nexus.generate_summary()
        assert nexus._nexus_summary.exists()
        data = json.loads(nexus._nexus_summary.read_text(encoding="utf-8"))
        assert data["total_events"] == 1

    def test_get_recent_events_empty(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        events = nexus.get_recent_events()
        assert events == []

    def test_get_recent_events_returns_latest(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        for i in range(5):
            nexus.create_event("rollback", f"a{i}", f"c{i}", f"r{i}", success=True)
        events = nexus.get_recent_events(limit=3)
        assert len(events) == 3
        ids = [e["event_id"] for e in events]
        assert ids == sorted(ids)[-3:]

    def test_get_recent_events_limit_default(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        for i in range(15):
            nexus.create_event("rollback", f"a{i}", f"c{i}", f"r{i}", success=True)
        events = nexus.get_recent_events()
        assert len(events) == 10

    def test_malformed_log_lines_skipped(self, tmp_path):
        nexus = RollbackAuditNexus(project_root=tmp_path)
        nexus._nexus_log.parent.mkdir(parents=True, exist_ok=True)
        with open(nexus._nexus_log, "a", encoding="utf-8") as f:
            f.write("bad json line\n")
            f.write("\n")
        nexus.create_event("rollback", "a1", "c1", "c2", success=True)
        summary = nexus.generate_summary()
        assert summary["total_events"] == 1
