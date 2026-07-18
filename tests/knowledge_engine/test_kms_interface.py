# [A_test] module_id: SRC-TST-1190 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-400 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_kms_interface
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_kms_interface.py
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

from zephyr.shared.knowledge.kms_interface import (
    TASK_KE_LIFECYCLE,
    KERecord,
    KMSInterface,
    TaskStateAssociation,
)


class TestKERecord:
    def test_creation_defaults(self):
        rec = KERecord(
            task_id="T-1",
            ke_type="insight",
            content_snippet="text",
            source_file="a.py",
            priority="P2",
            created_at="2026-01-01T00:00:00Z",
        )
        assert rec.lifecycle_phase == "active"

    def test_creation_custom_lifecycle(self):
        rec = KERecord(
            task_id="T-1",
            ke_type="insight",
            content_snippet="text",
            source_file="a.py",
            priority="P2",
            created_at="2026-01-01T00:00:00Z",
            lifecycle_phase="draft",
        )
        assert rec.lifecycle_phase == "draft"


class TestTaskStateAssociation:
    def test_creation(self):
        assoc = TaskStateAssociation(task_status="in_progress", ke_lifecycle="active", action="KE active")
        assert assoc.task_status == "in_progress"
        assert assoc.ke_lifecycle == "active"
        assert assoc.action == "KE active"


class TestTaskKELifecycle:
    def test_all_expected_mappings(self):
        assert TASK_KE_LIFECYCLE["created"] == "draft"
        assert TASK_KE_LIFECYCLE["locked"] == "draft"
        assert TASK_KE_LIFECYCLE["assigned"] == "pending_review"
        assert TASK_KE_LIFECYCLE["in_progress"] == "active"
        assert TASK_KE_LIFECYCLE["reviewing"] == "active"
        assert TASK_KE_LIFECYCLE["completed"] == "finalized"
        assert TASK_KE_LIFECYCLE["failed"] == "archived"


class TestKMSInterfaceInit:
    def test_init_default_data_dir(self):
        kms = KMSInterface()
        assert kms._data_dir == Path("data/knowledge")

    def test_init_custom_data_dir(self, tmp_path):
        kms = KMSInterface(data_dir=tmp_path)
        assert kms._data_dir == tmp_path


class TestKMSInterfacePushKE:
    def test_push_ke_basic(self, tmp_path):
        kms = KMSInterface(data_dir=tmp_path)
        record = kms.push_ke("TASK-1", "insight", "learned something", "a.py", "P1")
        assert record.task_id == "TASK-1"
        assert record.ke_type == "insight"
        assert record.content_snippet == "learned something"
        assert record.source_file == "a.py"
        assert record.priority == "P1"
        assert record.lifecycle_phase == "active"
        assert "T" in record.created_at

    def test_push_ke_truncates_long_content(self, tmp_path):
        kms = KMSInterface(data_dir=tmp_path)
        long_content = "x" * 600
        record = kms.push_ke("TASK-2", "insight", long_content)
        assert len(record.content_snippet) == 500

    def test_push_ke_defaults(self, tmp_path):
        kms = KMSInterface(data_dir=tmp_path)
        record = kms.push_ke("TASK-3", "failure", "bug found")
        assert record.source_file == ""
        assert record.priority == "P2"

    def test_push_ke_creates_directory(self, tmp_path):
        nested = tmp_path / "sub" / "dir"
        kms = KMSInterface(data_dir=nested)
        kms.push_ke("T-1", "insight", "test")
        assert nested.exists()

    def test_push_ke_writes_to_log(self, tmp_path):
        kms = KMSInterface(data_dir=tmp_path)
        kms.push_ke("TASK-10", "insight", "data", "f.py", "P0")
        lines = kms._push_log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["task_id"] == "TASK-10"
        assert data["ke_type"] == "insight"
        assert data["priority"] == "P0"

    def test_push_ke_empty_strings(self, tmp_path):
        kms = KMSInterface(data_dir=tmp_path)
        record = kms.push_ke("", "", "")
        assert record.task_id == ""
        assert record.ke_type == ""
        assert record.content_snippet == ""


class TestKMSInterfaceUpdateKELifecycle:
    def test_known_statuses(self):
        kms = KMSInterface(data_dir=Path("dummy"))
        assert kms.update_ke_lifecycle("T-1", "created") == "draft"
        assert kms.update_ke_lifecycle("T-1", "in_progress") == "active"
        assert kms.update_ke_lifecycle("T-1", "completed") == "finalized"
        assert kms.update_ke_lifecycle("T-1", "failed") == "archived"

    def test_unknown_status_defaults_to_draft(self):
        kms = KMSInterface(data_dir=Path("dummy"))
        result = kms.update_ke_lifecycle("T-1", "nonexistent_status")
        assert result == "draft"

    def test_empty_status(self):
        kms = KMSInterface(data_dir=Path("dummy"))
        result = kms.update_ke_lifecycle("T-1", "")
        assert result == "draft"


class TestKMSInterfaceGetTaskAssociation:
    def test_in_progress(self):
        kms = KMSInterface(data_dir=Path("dummy"))
        assoc = kms.get_task_association("in_progress")
        assert assoc.task_status == "in_progress"
        assert assoc.ke_lifecycle == "active"
        assert "active" in assoc.action.lower()

    def test_completed(self):
        kms = KMSInterface(data_dir=Path("dummy"))
        assoc = kms.get_task_association("completed")
        assert assoc.ke_lifecycle == "finalized"
        assert "immutable" in assoc.action.lower()

    def test_failed(self):
        kms = KMSInterface(data_dir=Path("dummy"))
        assoc = kms.get_task_association("failed")
        assert assoc.ke_lifecycle == "archived"

    def test_unknown_status(self):
        kms = KMSInterface(data_dir=Path("dummy"))
        assoc = kms.get_task_association("unknown")
        assert assoc.ke_lifecycle == "draft"
        assert assoc.action == "Unknown"


class TestKMSInterfaceGetKEPushesForTask:
    def test_no_log_file(self, tmp_path):
        kms = KMSInterface(data_dir=tmp_path)
        results = kms.get_ke_pushes_for_task("TASK-1")
        assert results == []

    def test_returns_matching_pushes(self, tmp_path):
        kms = KMSInterface(data_dir=tmp_path)
        kms.push_ke("TASK-1", "insight", "first", "a.py")
        kms.push_ke("TASK-2", "failure", "second", "b.py")
        kms.push_ke("TASK-1", "pattern", "third", "c.py")
        results = kms.get_ke_pushes_for_task("TASK-1")
        assert len(results) == 2
        assert all(r["task_id"] == "TASK-1" for r in results)

    def test_no_matching_task(self, tmp_path):
        kms = KMSInterface(data_dir=tmp_path)
        kms.push_ke("TASK-1", "insight", "test", "a.py")
        results = kms.get_ke_pushes_for_task("TASK-999")
        assert results == []

    def test_corrupt_log_file(self, tmp_path):
        kms = KMSInterface(data_dir=tmp_path)
        kms._data_dir.mkdir(parents=True, exist_ok=True)
        with open(kms._push_log_path, "w", encoding="utf-8") as f:
            f.write("bad json line\n")
        results = kms.get_ke_pushes_for_task("TASK-1")
        assert results == []


class TestKMSInterfaceGetContractSpec:
    def test_contract_spec_structure(self):
        kms = KMSInterface(data_dir=Path("dummy"))
        spec = kms.get_contract_spec()
        assert spec["contract_id"] == "KMS-IF-001"
        assert spec["version"] == "0.6.0"
        assert "push_format" in spec
        assert "lifecycle_map" in spec
        assert spec["max_content_length"] == 500
        assert len(spec["supported_ke_types"]) == 5

    def test_contract_spec_lifecycle_map_matches_constant(self):
        kms = KMSInterface(data_dir=Path("dummy"))
        spec = kms.get_contract_spec()
        assert spec["lifecycle_map"] == TASK_KE_LIFECYCLE
