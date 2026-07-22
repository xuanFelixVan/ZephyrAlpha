# [A_test] module_id: MOD-GOV_s3_snapshot_lifecycle | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §6.12
# [MODULE] tests.test_s3_snapshot_lifecycle
# [INVARIANTS] S3SnapshotLifecycle must not corrupt manifests; purge must be dry-run safe
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from zephyr.infrastructure.rollback.s3_snapshot_lifecycle import (
    FastPurgeResult,
    LifecyclePolicy,
    S3SnapshotLifecycle,
    SnapshotExistenceCheck,
    SnapshotManifest,
)


class TestLifecyclePolicy:
    def test_default_values(self):
        p = LifecyclePolicy()
        assert p.transition_to_glacier_days == 90
        assert p.expiration_days == 365
        assert p.prefix == "db_snapshots/"
        assert p.enabled is True

    def test_to_dict_enabled(self):
        p = LifecyclePolicy(enabled=True)
        d = p.to_dict()
        assert d["Status"] == "Enabled"
        assert d["Filter"]["Prefix"] == "db_snapshots/"
        assert d["Transitions"][0]["StorageClass"] == "GLACIER"
        assert d["Expiration"]["Days"] == 365

    def test_to_dict_disabled(self):
        p = LifecyclePolicy(enabled=False)
        d = p.to_dict()
        assert d["Status"] == "Disabled"

    def test_custom_values(self):
        p = LifecyclePolicy(transition_to_glacier_days=30, expiration_days=180, bucket="my-bucket")
        d = p.to_dict()
        assert d["Transitions"][0]["Days"] == 30
        assert d["Expiration"]["Days"] == 180


class TestS3SnapshotLifecycleInit:
    def test_default_snapshot_dir(self):
        mgr = S3SnapshotLifecycle()
        assert mgr._snapshot_dir == Path("data/rollback/db_snapshots")

    def test_custom_snapshot_dir(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path / "snapshots")
        assert mgr._snapshot_dir == tmp_path / "snapshots"

    def test_manifest_dir_derived(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path / "snapshots")
        assert mgr._manifest_dir == tmp_path / "snapshots" / ".manifests"


class TestApplyLifecyclePolicy:
    def test_writes_policy_file(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        policy = mgr.apply_lifecycle_policy()
        policy_path = tmp_path / ".manifests" / "lifecycle_policy.json"
        assert policy_path.exists()
        data = json.loads(policy_path.read_text(encoding="utf-8"))
        assert data["Status"] == "Enabled"
        assert isinstance(policy, LifecyclePolicy)

    def test_idempotent_write(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        mgr.apply_lifecycle_policy()
        mgr.apply_lifecycle_policy()
        policy_path = tmp_path / ".manifests" / "lifecycle_policy.json"
        assert policy_path.exists()


class TestClassifySnapshots:
    def test_empty_dir_returns_empty(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        result = mgr.classify_snapshots()
        assert result == {"hot": [], "warm": [], "cold": [], "expired": []}

    def test_hot_snapshot(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        now = datetime.now(UTC)
        manifest = SnapshotManifest(
            snapshot_key="snap1",
            created_at=now - timedelta(days=5),
            last_referenced_at=now - timedelta(days=5),
            size_bytes=1024,
            sha256="abc",
            commit_sha="def",
        )
        mgr._save_manifest(manifest)
        result = mgr.classify_snapshots()
        assert len(result["hot"]) == 1
        assert result["hot"][0].snapshot_key == "snap1"

    def test_expired_snapshot(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        old = datetime.now(UTC) - timedelta(days=400)
        manifest = SnapshotManifest(
            snapshot_key="snap_old",
            created_at=old,
            last_referenced_at=old,
            size_bytes=1024,
            sha256="abc",
            commit_sha="def",
        )
        mgr._save_manifest(manifest)
        result = mgr.classify_snapshots()
        assert len(result["expired"]) == 1

    def test_warm_snapshot(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        now = datetime.now(UTC)
        manifest = SnapshotManifest(
            snapshot_key="snap_warm",
            created_at=now - timedelta(days=10),
            last_referenced_at=now - timedelta(days=45),
            size_bytes=512,
            sha256="abc",
            commit_sha="def",
        )
        mgr._save_manifest(manifest)
        result = mgr.classify_snapshots()
        assert len(result["warm"]) == 1

    def test_cold_snapshot_by_age(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        now = datetime.now(UTC)
        manifest = SnapshotManifest(
            snapshot_key="snap_cold",
            created_at=now - timedelta(days=100),
            last_referenced_at=now - timedelta(days=10),
            size_bytes=256,
            sha256="abc",
            commit_sha="def",
        )
        mgr._save_manifest(manifest)
        result = mgr.classify_snapshots()
        assert len(result["cold"]) == 1


class TestFastPurge:
    def test_dry_run_no_deletion(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        now = datetime.now(UTC)
        manifest = SnapshotManifest(
            snapshot_key="snap_purge",
            created_at=now - timedelta(days=200),
            last_referenced_at=now - timedelta(days=200),
            size_bytes=128,
            sha256="abc",
            commit_sha="def",
        )
        mgr._save_manifest(manifest)
        result = mgr.fast_purge(max_age_days=90, dry_run=True)
        assert isinstance(result, FastPurgeResult)
        assert result.purged_count == 1
        assert "snap_purge" in result.purged_keys
        manifest_path = tmp_path / ".manifests" / "snap_purge.manifest.json"
        assert manifest_path.exists()

    def test_actual_purge_deletes(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        now = datetime.now(UTC)
        manifest = SnapshotManifest(
            snapshot_key="snap_del",
            created_at=now - timedelta(days=200),
            last_referenced_at=now - timedelta(days=200),
            size_bytes=64,
            sha256="abc",
            commit_sha="def",
        )
        mgr._save_manifest(manifest)
        result = mgr.fast_purge(max_age_days=90, dry_run=False)
        assert result.purged_count == 1
        manifest_path = tmp_path / ".manifests" / "snap_del.manifest.json"
        assert not manifest_path.exists()

    def test_purge_nothing_recent(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        now = datetime.now(UTC)
        manifest = SnapshotManifest(
            snapshot_key="snap_recent",
            created_at=now - timedelta(days=1),
            last_referenced_at=now - timedelta(days=1),
            size_bytes=32,
            sha256="abc",
            commit_sha="def",
        )
        mgr._save_manifest(manifest)
        result = mgr.fast_purge(max_age_days=90, dry_run=False)
        assert result.purged_count == 0

    def test_purge_empty_dir(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        result = mgr.fast_purge()
        assert result.purged_count == 0
        assert result.errors == []


class TestCheckSnapshotExists:
    def test_existing_snapshot(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        snap_file = tmp_path / "db1.sql"
        snap_file.write_text("data", encoding="utf-8")
        result = mgr.check_snapshot_exists("db1.sql")
        assert isinstance(result, SnapshotExistenceCheck)
        assert result.exists is True
        assert result.key == "db1.sql"
        assert result.last_modified != ""

    def test_nonexistent_snapshot(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        result = mgr.check_snapshot_exists("missing.sql")
        assert result.exists is False
        assert "not found" in result.error

    def test_empty_key_resolves_to_dir(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        result = mgr.check_snapshot_exists("")
        assert result.key == ""


class TestRegisterSnapshot:
    def test_register_creates_manifest(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        snap_file = tmp_path / "new_snap.sql"
        snap_file.write_text("content", encoding="utf-8")
        manifest = mgr.register_snapshot("new_snap.sql", commit_sha="abc123", sha256_hash="deadbeef")
        assert isinstance(manifest, SnapshotManifest)
        assert manifest.snapshot_key == "new_snap.sql"
        assert manifest.commit_sha == "abc123"
        assert manifest.sha256 == "deadbeef"
        assert manifest.size_bytes > 0
        manifest_path = tmp_path / ".manifests" / "new_snap.sql.manifest.json"
        assert manifest_path.exists()

    def test_register_nonexistent_file_zero_size(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        manifest = mgr.register_snapshot("ghost.sql", commit_sha="def456")
        assert manifest.size_bytes == 0


class TestTouchReference:
    def test_touch_updates_reference_time(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        now = datetime.now(UTC)
        old_time = now - timedelta(days=100)
        manifest = SnapshotManifest(
            snapshot_key="touch_me",
            created_at=old_time,
            last_referenced_at=old_time,
            size_bytes=64,
            sha256="abc",
            commit_sha="def",
        )
        mgr._save_manifest(manifest)
        mgr.touch_reference("touch_me")
        updated = mgr._load_manifests()
        assert len(updated) == 1
        assert updated[0].last_referenced_at > old_time

    def test_touch_nonexistent_key_no_error(self, tmp_path):
        mgr = S3SnapshotLifecycle(snapshot_dir=tmp_path)
        mgr.touch_reference("no_such_key")
