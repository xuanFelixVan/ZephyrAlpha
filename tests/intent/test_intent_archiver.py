# [A_test] module_id: MOD-GOV_intent_archiver | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_intent_archiver
# [INVARIANTS] IntentArchiver.EXIT_CODE_INTENT_PRUNE==46
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import hashlib
from pathlib import Path

from zephyr.infrastructure.rollback.intent_archiver import (
    IntentArchiver,
    IntentRecord,
)


class TestIntentRecord:
    def test_fields(self):
        rec = IntentRecord(
            intent_id="INTENT-001",
            operation_id="OP-001",
            intent_text="rollback due to bug",
            author="agent",
            archived_at="2026-01-01T00:00:00Z",
            content_hash="abc123",
        )
        assert rec.intent_id == "INTENT-001"
        assert rec.operation_id == "OP-001"
        assert rec.intent_text == "rollback due to bug"


class TestIntentArchiverInstantiation:
    def test_default_project_root(self):
        archiver = IntentArchiver()
        assert archiver.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        assert archiver.project_root == tmp_path
        assert archiver.archive_dir.exists()

    def test_archive_dir_created(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        expected_dir = tmp_path / ".zephyr/intent_archive"
        assert expected_dir.exists()


class TestArchive:
    def test_archive_creates_record(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        record = archiver.archive("OP-001", "Fix critical bug in module X", author="agent-1")
        assert record.intent_id.startswith("INTENT-")
        assert record.operation_id == "OP-001"
        assert record.intent_text == "Fix critical bug in module X"
        assert record.author == "agent-1"
        assert record.content_hash == hashlib.sha256(b"Fix critical bug in module X").hexdigest()

    def test_archive_creates_file(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        record = archiver.archive("OP-002", "Rollback config change")
        intent_file = archiver.archive_dir / f"{record.intent_id}.txt"
        assert intent_file.exists()
        content = intent_file.read_text(encoding="utf-8")
        assert "OP-002" in content
        assert "Rollback config change" in content

    def test_archive_appends_manifest(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        archiver.archive("OP-003", "Intent A")
        archiver.archive("OP-004", "Intent B")

        manifest = archiver.manifest_path.read_text(encoding="utf-8")
        lines = [l for l in manifest.strip().splitlines() if l.strip()]
        assert len(lines) == 2

    def test_archive_empty_intent_text(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        record = archiver.archive("OP-005", "")
        assert record.intent_text == ""
        assert record.content_hash == hashlib.sha256(b"").hexdigest()

    def test_archive_empty_author(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        record = archiver.archive("OP-006", "Some intent", author="")
        assert record.author == ""


class TestVerifyIntegrity:
    def test_empty_manifest_passes(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        status = archiver.verify_integrity()
        assert status.integrity_pass is True
        assert status.total_entries == 0
        assert status.exit_code == 0

    def test_intact_archive_passes(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        archiver.archive("OP-010", "Good intent")
        status = archiver.verify_integrity()
        assert status.integrity_pass is True
        assert status.total_entries == 1
        assert status.exit_code == 0

    def test_pruned_file_fails(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        record = archiver.archive("OP-011", "Will be pruned")
        intent_file = archiver.archive_dir / f"{record.intent_id}.txt"
        intent_file.unlink()

        status = archiver.verify_integrity()
        assert status.integrity_pass is False
        assert status.pruned_count == 1
        assert status.exit_code == 46

    def test_no_manifest_returns_pass(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        archiver.manifest_path.unlink(missing_ok=True)
        status = archiver.verify_integrity()
        assert status.integrity_pass is True
        assert status.total_entries == 0


class TestGetIntent:
    def test_returns_intent_text(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        archiver.archive("OP-020", "Original intent text here")
        result = archiver.get_intent("OP-020")
        assert result == "Original intent text here"

    def test_returns_none_for_missing(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        result = archiver.get_intent("NONEXISTENT")
        assert result is None

    def test_returns_none_when_no_manifest(self, tmp_path):
        archiver = IntentArchiver(project_root=tmp_path)
        archiver.manifest_path.unlink(missing_ok=True)
        result = archiver.get_intent("OP-999")
        assert result is None

    def test_multiple_archives_returns_correct(self, tmp_path):
        import time

        archiver = IntentArchiver(project_root=tmp_path)
        archiver.archive("OP-030", "First intent")
        time.sleep(0.01)
        archiver.archive("OP-031", "Second intent")
        assert archiver.get_intent("OP-030") == "First intent"
        assert archiver.get_intent("OP-031") == "Second intent"
