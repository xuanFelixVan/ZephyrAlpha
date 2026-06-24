# [A_test] module_id: SRC-TST-0436 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-353 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_blueprint_code_sync_sync
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] pytest tests/test_blueprint_code_sync_sync.py

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.blueprint_code_sync import (
    BlueprintCodeSyncService,
    SyncPair,
    SyncVerification,
)


class TestSyncPairDataclass:
    def test_fields(self):
        pair = SyncPair(
            blueprint_section="§2.2",
            code_path="src/foo.py",
            synced=True,
            checksum="abc123",
            last_verified="2026-01-01T00:00:00+00:00",
        )
        assert pair.blueprint_section == "§2.2"
        assert pair.synced is True
        assert pair.checksum == "abc123"


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
        assert v.passed is False
        assert v.stale_count == 1


class TestBlueprintCodeSyncService:
    def test_instantiation_with_path(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        assert svc._project_root == tmp_path

    def test_instantiation_default(self):
        svc = BlueprintCodeSyncService()
        assert svc._project_root == Path.cwd()

    def test_verify_sync_all_exist(self, tmp_path):
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
        assert result.pairs[0].synced is True
        assert result.pairs[0].checksum != ""

    def test_verify_sync_some_missing(self, tmp_path):
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
        assert result.pairs[0].synced is True
        assert result.pairs[1].synced is False
        assert result.pairs[1].checksum == ""

    def test_verify_sync_empty_pairs(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        result = svc.verify_sync([])
        assert result.total_pairs == 0
        assert result.synced_count == 0
        assert result.stale_count == 0
        assert result.passed is True

    def test_verify_sync_pair_missing_keys(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        result = svc.verify_sync([{"section": "", "code_path": "nonexistent/path.py"}])
        assert result.total_pairs == 1
        assert result.stale_count == 1
        assert result.pairs[0].blueprint_section == ""
        assert result.pairs[0].code_path == "nonexistent/path.py"

    def test_verify_sync_checksum_stable(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "stable.py").write_text("x = 42", encoding="utf-8")

        pairs = [{"section": "§1", "code_path": "src/stable.py"}]
        r1 = svc.verify_sync(pairs)
        r2 = svc.verify_sync(pairs)
        assert r1.pairs[0].checksum == r2.pairs[0].checksum

    def test_check_sync_consistency(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        result = svc.check_sync_consistency()
        assert "synced" in result
        assert "coverage" in result
        assert "stale_files" in result
        assert isinstance(result["stale_files"], list)

    def test_check_sync_consistency_all_present(self, tmp_path):
        svc = BlueprintCodeSyncService(project_root=tmp_path)
        for path_str in [
            "src/zephyr/core/models.py",
            "src/zephyr/core/blueprint_decomposer.py",
            "src/zephyr/mcp/task_manager_server.py",
            "src/zephyr/core/lifecycle/task_lifecycle_manager.py",
        ]:
            p = tmp_path / path_str
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# module", encoding="utf-8")

        result = svc.check_sync_consistency()
        assert result["synced"] is True
        assert result["stale_files"] == []
