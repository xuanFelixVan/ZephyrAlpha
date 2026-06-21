# [A_test] module_id: SRC-TST-0435 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-352 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md | §
# [MODULE] tests.test_blueprint_code_sync_core
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.infrastructure.blueprint_code_sync import (
    SyncPair,
    SyncVerification,
    BlueprintCodeSyncService,
)


class TestSyncPairDataclass:
    def test_fields(self):
        p = SyncPair(
            blueprint_section="§2.2",
            code_path="src/foo.py",
            synced=True,
            checksum="abc123",
            last_verified="2026-01-01T00:00:00+00:00",
        )
        assert p.blueprint_section == "§2.2"
        assert p.synced is True
        assert p.checksum == "abc123"

    def test_not_synced(self):
        p = SyncPair(
            blueprint_section="§3.1",
            code_path="src/missing.py",
            synced=False,
            checksum="",
            last_verified="2026-01-01T00:00:00+00:00",
        )
        assert p.synced is False
        assert p.checksum == ""


class TestSyncVerificationDataclass:
    def test_fields(self):
        v = SyncVerification(
            total_pairs=2,
            synced_count=1,
            stale_count=1,
            pairs=[],
            passed=False,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert v.total_pairs == 2
        assert v.passed is False


class TestBlueprintCodeSyncService:
    def test_init_with_project_root(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        assert svc._project_root == tmp_path

    def test_init_default_root(self):
        svc = BlueprintCodeSyncService()
        assert svc._project_root == Path.cwd()

    def test_verify_sync_all_synced(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "foo.py").write_text("print('hello')", encoding="utf-8")
        (tmp_path / "src").mkdir(exist_ok=True)
        (tmp_path / "src" / "bar.py").write_text("print('world')", encoding="utf-8")

        pairs = [
            {"section": "§1", "code_path": "src/foo.py"},
            {"section": "§2", "code_path": "src/bar.py"},
        ]
        result = svc.verify_sync(pairs)
        assert result.total_pairs == 2
        assert result.synced_count == 2
        assert result.stale_count == 0
        assert result.passed is True
        assert len(result.pairs) == 2
        assert all(p.synced for p in result.pairs)
        assert all(p.checksum != "" for p in result.pairs)

    def test_verify_sync_all_stale(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        pairs = [
            {"section": "§1", "code_path": "nonexistent.py"},
            {"section": "§2", "code_path": "also_missing.py"},
        ]
        result = svc.verify_sync(pairs)
        assert result.total_pairs == 2
        assert result.synced_count == 0
        assert result.stale_count == 2
        assert result.passed is False
        assert all(not p.synced for p in result.pairs)
        assert all(p.checksum == "" for p in result.pairs)

    def test_verify_sync_mixed(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "exists.py").write_text("x = 1", encoding="utf-8")

        pairs = [
            {"section": "§1", "code_path": "src/exists.py"},
            {"section": "§2", "code_path": "src/missing.py"},
        ]
        result = svc.verify_sync(pairs)
        assert result.synced_count == 1
        assert result.stale_count == 1
        assert result.passed is False

    def test_verify_sync_empty_pairs(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        result = svc.verify_sync([])
        assert result.total_pairs == 0
        assert result.synced_count == 0
        assert result.stale_count == 0
        assert result.passed is True

    def test_verify_sync_checksum_stable(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        (tmp_path / "src").mkdir()
        code_file = tmp_path / "src" / "stable.py"
        code_file.write_text("stable content", encoding="utf-8")

        pairs = [{"section": "§1", "code_path": "src/stable.py"}]
        r1 = svc.verify_sync(pairs)
        r2 = svc.verify_sync(pairs)
        assert r1.pairs[0].checksum == r2.pairs[0].checksum

    def test_verify_sync_pair_missing_keys(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        pairs = [{"section": "", "code_path": "nonexistent_file.py"}]
        result = svc.verify_sync(pairs)
        assert result.total_pairs == 1
        assert result.stale_count == 1
        assert result.pairs[0].blueprint_section == ""
        assert result.pairs[0].code_path == "nonexistent_file.py"

    def test_check_sync_consistency(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        result = svc.check_sync_consistency()
        assert "synced" in result
        assert "coverage" in result
        assert "stale_files" in result
        assert isinstance(result["stale_files"], list)

    def test_check_sync_consistency_all_exist(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        (tmp_path / "src" / "zephyr" / "core").mkdir(parents=True, exist_ok=True)
        (tmp_path / "src" / "zephyr" / "mcp").mkdir(parents=True, exist_ok=True)
        (tmp_path / "src" / "zephyr" / "core" / "lifecycle").mkdir(parents=True, exist_ok=True)

        (tmp_path / "src" / "zephyr" / "core" / "models.py").write_text("x=1", encoding="utf-8")
        (tmp_path / "src" / "zephyr" / "core" / "blueprint_decomposer.py").write_text("x=2", encoding="utf-8")
        (tmp_path / "src" / "zephyr" / "mcp" / "task_manager_server.py").write_text("x=3", encoding="utf-8")
        (tmp_path / "src" / "zephyr" / "core" / "lifecycle" / "task_lifecycle_manager.py").write_text("x=4", encoding="utf-8")

        result = svc.check_sync_consistency()
        assert result["synced"] is True
        assert result["stale_files"] == []

    def test_check_sync_consistency_none_exist(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        result = svc.check_sync_consistency()
        assert result["synced"] is False
        assert len(result["stale_files"]) > 0
