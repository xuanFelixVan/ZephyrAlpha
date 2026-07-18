# [A_test] module_id: SRC-TST-0434 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-351 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §

# [MODULE] tests.test_blueprint_code_sync

# [INVARIANTS] test coverage for zephyr.infrastructure.shared_services.blueprint_code_sync

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] none

# [TESTS] python -m pytest tests/test_blueprint_code_sync.py -q
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.infrastructure.blueprint_code_sync import BlueprintCodeSync, SyncEntry, SyncReport
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

PROJECT_ROOT = REPO_ROOT  # alias 真源


class TestSyncEntry:
    def test_default_fields(self):
        entry = SyncEntry(blueprint_path="a.md", code_path="b.py", status="PENDING")
        assert entry.blueprint_path == "a.md"
        assert entry.code_path == "b.py"
        assert entry.status == "PENDING"
        assert entry.last_synced == ""

    def test_custom_last_synced(self):
        entry = SyncEntry(
            blueprint_path="a.md",
            code_path="b.py",
            status="SYNCED",
            last_synced="2026-01-01T00:00:00+00:00",
        )
        assert entry.last_synced == "2026-01-01T00:00:00+00:00"


class TestSyncReport:
    def test_fields(self):
        entries = [SyncEntry("a.md", "b.py", "SYNCED")]
        report = SyncReport(
            total_entries=1,
            synced=1,
            missing=0,
            stale=0,
            entries=entries,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert report.total_entries == 1
        assert report.synced == 1
        assert report.missing == 0
        assert report.stale == 0
        assert len(report.entries) == 1
        assert report.timestamp_utc == "2026-01-01T00:00:00+00:00"

    def test_empty_report(self):
        report = SyncReport(
            total_entries=0,
            synced=0,
            missing=0,
            stale=0,
            entries=[],
            timestamp_utc="",
        )
        assert report.total_entries == 0
        assert report.entries == []


class TestBlueprintCodeSyncInit:
    def test_init_with_explicit_root(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        assert sync._project_root == PROJECT_ROOT

    def test_init_with_none_falls_back_to_cwd(self):
        sync = BlueprintCodeSync(project_root=None)
        assert sync._project_root == Path.cwd()

    def test_registry_path_constructed(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        expected = PROJECT_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"
        assert sync._registry_path == expected


class TestVerifySync:
    def test_verify_sync_returns_sync_report(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        report = sync.verify_sync()
        assert isinstance(report, SyncReport)
        assert isinstance(report.timestamp_utc, str)
        assert len(report.timestamp_utc) > 0

    def test_verify_sync_empty_entries(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        report = sync.verify_sync()
        assert report.total_entries == 0
        assert report.synced == 0
        assert report.missing == 0
        assert report.stale == 0

    def test_verify_sync_with_mocked_entries(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        mock_entries = [
            SyncEntry(
                blueprint_path="docs/03_modules/blueprint_registry.yaml",
                code_path="src/zephyr/core/blueprint_code_sync.py",
                status="PENDING",
            ),
            SyncEntry(
                blueprint_path="docs/nonexistent_blueprint.md",
                code_path="src/zephyr/core/blueprint_code_sync.py",
                status="PENDING",
            ),
            SyncEntry(
                blueprint_path="docs/03_modules/blueprint_registry.yaml",
                code_path="src/zephyr/core/nonexistent_code.py",
                status="PENDING",
            ),
        ]
        with patch.object(sync, "_collect_entries", return_value=mock_entries):
            report = sync.verify_sync()
        assert report.total_entries == 3
        assert report.synced == 1
        assert report.stale == 1
        assert report.missing == 1

    def test_verify_sync_entry_statuses_updated(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        mock_entries = [
            SyncEntry(
                blueprint_path="docs/03_modules/blueprint_registry.yaml",
                code_path="src/zephyr/core/blueprint_code_sync.py",
                status="PENDING",
            ),
        ]
        with patch.object(sync, "_collect_entries", return_value=mock_entries):
            report = sync.verify_sync()
        assert report.entries[0].status == "SYNCED"


class TestValidateTaskCard:
    def test_valid_task_card_with_existing_path(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        task_card = {
            "downstream_outputs": [
                {"path": "src/zephyr/core/blueprint_code_sync.py"},
            ],
        }
        result, msg = sync.validate_task_card(task_card)
        assert result is True
        assert "verified" in msg.lower()

    def test_invalid_task_card_with_nonexistent_path(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        task_card = {
            "downstream_outputs": [
                {"path": "src/zephyr/core/does_not_exist_at_all.py"},
            ],
        }
        result, msg = sync.validate_task_card(task_card)
        assert result is False
        assert "not found" in msg.lower()
        assert "does_not_exist_at_all.py" in msg

    def test_task_card_with_empty_downstream_outputs(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        task_card = {"downstream_outputs": []}
        result, msg = sync.validate_task_card(task_card)
        assert result is True

    def test_task_card_missing_downstream_outputs_key(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        task_card = {"title": "some task"}
        result, msg = sync.validate_task_card(task_card)
        assert result is True

    def test_task_card_with_empty_path_string(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        task_card = {
            "downstream_outputs": [
                {"path": ""},
            ],
        }
        result, msg = sync.validate_task_card(task_card)
        assert result is True

    def test_task_card_with_none_input(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        with pytest.raises((TypeError, AttributeError)):
            sync.validate_task_card(None)

    def test_mixed_existing_and_nonexisting_paths(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        task_card = {
            "downstream_outputs": [
                {"path": "src/zephyr/core/blueprint_code_sync.py"},
                {"path": "src/zephyr/core/phantom_module.py"},
            ],
        }
        result, msg = sync.validate_task_card(task_card)
        assert result is False
        assert "phantom_module.py" in msg


class TestCollectEntries:
    def test_collect_entries_returns_list(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        entries = sync._collect_entries()
        assert isinstance(entries, list)

    def test_collect_entries_with_nonexistent_dir(self):
        sync = BlueprintCodeSync(project_root=Path(r"C:\nonexistent_project_root_xyz"))
        entries = sync._collect_entries()
        assert entries == []

    def test_collect_entries_with_mocked_glob(self):
        sync = BlueprintCodeSync(project_root=PROJECT_ROOT)
        fake_card = (
            PROJECT_ROOT
            / "docs"
            / "03_modules"
            / "l01-infrastructure"
            / "task-system"
            / "changes"
            / "MOD-INF-039"
            / "TASK-INF-0999.md"
        )
        with patch.object(Path, "glob", return_value=[fake_card]):
            with patch.object(Path, "exists", return_value=True):
                entries = sync._collect_entries()
        assert len(entries) >= 1
        assert entries[0].status == "PENDING"
