# [A_test] module_id: SRC-TST-1054 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_git_infra_snapshot
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.infrastructure.rollback.git_infra_snapshot import GitInfraSnapshot, InfraCheckResult


@pytest.fixture
def tmp_project(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n\trepositoryformatversion = 0\n", encoding="utf-8")
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir()
    (hooks_dir / "pre-commit").write_text("#!/bin/sh\necho check\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def snapshot(tmp_project):
    return GitInfraSnapshot(project_root=tmp_project)


class TestGitInfraSnapshotInstantiation:
    def test_default_project_root(self):
        s = GitInfraSnapshot()
        assert s.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_project):
        s = GitInfraSnapshot(project_root=tmp_project)
        assert s.project_root == tmp_project

    def test_snapshot_dir_set(self, tmp_project):
        s = GitInfraSnapshot(project_root=tmp_project)
        expected = tmp_project / ".zephyr" / "git_infra_snapshot"
        assert s.snapshot_dir == expected


class TestCreateSnapshot:
    def test_creates_snapshot(self, snapshot, tmp_project):
        result = snapshot.create_snapshot()
        assert result is True
        assert snapshot.snapshot_dir.exists()
        assert (snapshot.snapshot_dir / "config").exists()
        assert (snapshot.snapshot_dir / "hooks" / "pre-commit").exists()

    def test_manifest_created(self, snapshot):
        snapshot.create_snapshot()
        manifest_path = snapshot.snapshot_dir / "manifest.json"
        assert manifest_path.exists()
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert "snapshot_at" in data
        assert "files" in data

    def test_no_git_dir_returns_false(self, tmp_path):
        s = GitInfraSnapshot(project_root=tmp_path)
        assert s.create_snapshot() is False

    def test_overwrites_existing_snapshot(self, snapshot):
        snapshot.create_snapshot()
        result = snapshot.create_snapshot()
        assert result is True


class TestCheckIntegrity:
    def test_intact_after_snapshot(self, snapshot):
        snapshot.create_snapshot()
        result = snapshot.check_integrity()
        assert isinstance(result, InfraCheckResult)
        assert result.intact is True
        assert result.tampered_files == []

    def test_no_snapshot_returns_intact(self, tmp_project):
        s = GitInfraSnapshot(project_root=tmp_project)
        result = s.check_integrity()
        assert result.intact is True
        assert "No snapshot available" in result.details

    def test_detects_config_tamper(self, snapshot, tmp_project):
        snapshot.create_snapshot()
        (tmp_project / ".git" / "config").write_text("[core]\n\tmodified = true\n", encoding="utf-8")
        result = snapshot.check_integrity()
        assert result.intact is False
        assert ".git/config" in result.tampered_files

    def test_detects_hook_tamper(self, snapshot, tmp_project):
        snapshot.create_snapshot()
        (tmp_project / ".git" / "hooks" / "pre-commit").write_text("#!/bin/sh\nevil_code\n", encoding="utf-8")
        result = snapshot.check_integrity()
        assert result.intact is False
        assert any("pre-commit" in f for f in result.tampered_files)


class TestRestoreFromSnapshot:
    def test_restore_config(self, snapshot, tmp_project):
        snapshot.create_snapshot()
        original = (tmp_project / ".git" / "config").read_text(encoding="utf-8")
        (tmp_project / ".git" / "config").write_text("[core]\n\tmodified = true\n", encoding="utf-8")
        result = snapshot.restore_from_snapshot()
        assert result.intact is True
        assert ".git/config" in result.restored_files
        restored = (tmp_project / ".git" / "config").read_text(encoding="utf-8")
        assert restored == original

    def test_restore_hook(self, snapshot, tmp_project):
        snapshot.create_snapshot()
        original = (tmp_project / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8")
        (tmp_project / ".git" / "hooks" / "pre-commit").write_text("#!/bin/sh\nevil\n", encoding="utf-8")
        result = snapshot.restore_from_snapshot()
        assert result.intact is True
        assert any("pre-commit" in f for f in result.restored_files)
        restored = (tmp_project / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8")
        assert restored == original

    def test_no_restore_needed(self, snapshot):
        snapshot.create_snapshot()
        result = snapshot.restore_from_snapshot()
        assert result.intact is True
        assert result.restored_files == []

    def test_restore_returns_tampered_list(self, snapshot, tmp_project):
        snapshot.create_snapshot()
        (tmp_project / ".git" / "config").write_text("tampered", encoding="utf-8")
        result = snapshot.restore_from_snapshot()
        assert ".git/config" in result.tampered_files
        assert ".git/config" in result.restored_files


class TestInfraCheckResult:
    def test_dataclass_fields(self):
        r = InfraCheckResult(intact=True, tampered_files=[], restored_files=[], details=["ok"])
        assert r.intact is True
        assert r.tampered_files == []
        assert r.restored_files == []
        assert r.details == ["ok"]

    def test_default_details(self):
        r = InfraCheckResult(intact=False, tampered_files=["f1"], restored_files=[])
        assert r.details == []
