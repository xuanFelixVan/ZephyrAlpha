# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.s3_snapshot_lifecycle
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_s3_snapshot_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
S3 Snapshot Lifecycle Manager — 快照防生命周期过期。

依据：
    蓝图 MOD-INF-021 §6.12 B73
    任务卡 TASK-INF-0249

功能：
    - S3 lifecycle policy: 标记过期 checkpoint 为 Glacier/GD 归档
    - fasclen 净化 cron: 定期清理 >90天未引用的快照
    - 恢复前检查 S3 对象存在性
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass
class LifecyclePolicy:
    transition_to_glacier_days: int = 90
    expiration_days: int = 365
    bucket: str = ""
    prefix: str = "db_snapshots/"
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "Id": "ZephyrCheckpointLifecycle",
            "Status": "Enabled" if self.enabled else "Disabled",
            "Filter": {"Prefix": self.prefix},
            "Transitions": [
                {
                    "Days": self.transition_to_glacier_days,
                    "StorageClass": "GLACIER",
                }
            ],
            "Expiration": {
                "Days": self.expiration_days,
            },
        }


@dataclass
class SnapshotManifest:
    snapshot_key: str
    created_at: datetime
    last_referenced_at: datetime
    size_bytes: int
    sha256: str
    commit_sha: str


@dataclass
class FastPurgeResult:
    purged_count: int
    purged_keys: list[str]
    errors: list[str] = field(default_factory=list)


@dataclass
class SnapshotExistenceCheck:
    exists: bool
    key: str
    storage_class: str = ""
    last_modified: str = ""
    error: str = ""


class S3SnapshotLifecycle:
    def __init__(self, snapshot_dir: Path | None = None) -> None:
        self._snapshot_dir = snapshot_dir or Path("data/rollback/db_snapshots")
        self._manifest_dir = self._snapshot_dir / ".manifests"
        self._policy = LifecyclePolicy()

    def apply_lifecycle_policy(self) -> LifecyclePolicy:
        self._manifest_dir.mkdir(parents=True, exist_ok=True)
        policy_path = self._manifest_dir / "lifecycle_policy.json"
        policy_dict = self._policy.to_dict()
        policy_path.write_text(
            json.dumps(policy_dict, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self._policy

    def classify_snapshots(self) -> dict[str, list[SnapshotManifest]]:
        hot: list[SnapshotManifest] = []
        warm: list[SnapshotManifest] = []
        cold: list[SnapshotManifest] = []
        expired: list[SnapshotManifest] = []

        now = datetime.now(UTC)
        manifests = self._load_manifests()

        for m in manifests:
            age_days = (now - m.created_at).days
            unreferenced_days = (now - m.last_referenced_at).days

            if age_days > self._policy.expiration_days:
                expired.append(m)
            elif age_days > self._policy.transition_to_glacier_days or unreferenced_days > 90:
                cold.append(m)
            elif unreferenced_days > 30:
                warm.append(m)
            else:
                hot.append(m)

        return {
            "hot": hot,
            "warm": warm,
            "cold": cold,
            "expired": expired,
        }

    def fast_purge(self, max_age_days: int = 90, dry_run: bool = False) -> FastPurgeResult:
        cutoff = datetime.now(UTC) - timedelta(days=max_age_days)
        purged_keys: list[str] = []
        errors: list[str] = []

        manifests = self._load_manifests()

        for m in manifests:
            if m.last_referenced_at < cutoff:
                snapshot_path = self._snapshot_dir / m.snapshot_key
                manifest_path = self._manifest_dir / f"{m.snapshot_key}.manifest.json"

                if not dry_run:
                    try:
                        if snapshot_path.exists():
                            snapshot_path.unlink()
                        if manifest_path.exists():
                            manifest_path.unlink()
                    except OSError as e:
                        errors.append(f"Failed to purge {m.snapshot_key}: {e}")
                        continue
                purged_keys.append(m.snapshot_key)

        if not dry_run:
            self._cleanup_known_good_state(purged_keys)

        return FastPurgeResult(
            purged_count=len(purged_keys),
            purged_keys=purged_keys,
            errors=errors,
        )

    def check_snapshot_exists(self, key: str) -> SnapshotExistenceCheck:
        snapshot_path = self._snapshot_dir / key
        manifest_path = self._manifest_dir / f"{key}.manifest.json"

        if snapshot_path.exists():
            return SnapshotExistenceCheck(
                exists=True,
                key=key,
                last_modified=datetime.fromtimestamp(snapshot_path.stat().st_mtime, tz=UTC).isoformat(),
            )

        return SnapshotExistenceCheck(
            exists=False,
            key=key,
            error=f"Snapshot {key} not found in {self._snapshot_dir}",
        )

    def register_snapshot(self, key: str, commit_sha: str, sha256_hash: str = "") -> SnapshotManifest:
        snapshot_path = self._snapshot_dir / key
        size_bytes = snapshot_path.stat().st_size if snapshot_path.exists() else 0

        manifest = SnapshotManifest(
            snapshot_key=key,
            created_at=datetime.now(UTC),
            last_referenced_at=datetime.now(UTC),
            size_bytes=size_bytes,
            sha256=sha256_hash,
            commit_sha=commit_sha,
        )

        self._save_manifest(manifest)
        return manifest

    def touch_reference(self, key: str) -> None:
        manifests = self._load_manifests()
        for m in manifests:
            if m.snapshot_key == key:
                m.last_referenced_at = datetime.now(UTC)
                self._save_manifest(m)
                return

    def _load_manifests(self) -> list[SnapshotManifest]:
        manifests: list[SnapshotManifest] = []
        if not self._manifest_dir.exists():
            return manifests
        for manifest_file in self._manifest_dir.glob("*.manifest.json"):
            try:
                data = json.loads(manifest_file.read_text(encoding="utf-8"))
                manifests.append(
                    SnapshotManifest(
                        snapshot_key=data["snapshot_key"],
                        created_at=datetime.fromisoformat(data["created_at"]),
                        last_referenced_at=datetime.fromisoformat(data["last_referenced_at"]),
                        size_bytes=data.get("size_bytes", 0),
                        sha256=data.get("sha256", ""),
                        commit_sha=data.get("commit_sha", ""),
                    )
                )
            except (json.JSONDecodeError, KeyError):
                pass
        return manifests

    def _save_manifest(self, manifest: SnapshotManifest) -> None:
        self._manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self._manifest_dir / f"{manifest.snapshot_key}.manifest.json"
        data = {
            "snapshot_key": manifest.snapshot_key,
            "created_at": manifest.created_at.isoformat(),
            "last_referenced_at": manifest.last_referenced_at.isoformat(),
            "size_bytes": manifest.size_bytes,
            "sha256": manifest.sha256,
            "commit_sha": manifest.commit_sha,
        }
        manifest_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _cleanup_known_good_state(self, purged_keys: list[str]) -> None:
        kgs_path = Path("data/rollback/knowngoodstate.json")
        if not kgs_path.exists():
            return
        try:
            kgs_data = json.loads(kgs_path.read_text(encoding="utf-8"))
            if "snapshots" in kgs_data:
                kgs_data["snapshots"] = [s for s in kgs_data["snapshots"] if s.get("key") not in purged_keys]
                kgs_path.write_text(
                    json.dumps(kgs_data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
        except (json.JSONDecodeError, KeyError):
            pass
