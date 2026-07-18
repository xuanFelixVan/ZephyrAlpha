# [A_test] module_id: SRC-TST-0079 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-237 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_reconciler
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 Reconciler module."""

from datetime import UTC, datetime

from zephyr.infrastructure.asset_inventory.models import (
    AssetType,
    ClassificationResult,
    ClassifiedAsset,
    RawFileEntry,
    ScanResult,
    UnifiedAssetIndex,
)
from zephyr.infrastructure.asset_inventory.reconciler import Reconciler


def _entry(path: str, sha: str = "a" * 64, mtime: datetime | None = None) -> RawFileEntry:
    return RawFileEntry(
        relative_path=path,
        absolute_path=f"/abs/{path}",
        file_name=path.split("/")[-1],
        extension="." + path.rsplit(".", 1)[-1],
        size_bytes=100,
        mtime_utc=mtime or datetime.now(UTC),
        sha256=sha,
    )


def _asset(path: str, sha: str = "a" * 64) -> ClassifiedAsset:
    return ClassifiedAsset(
        relative_path=path,
        asset_type=AssetType.MODULE,
        size_bytes=100,
        mtime_utc=datetime.now(UTC),
        sha256=sha,
    )


class TestReconciler:
    def test_all_matched(self) -> None:
        e = _entry("src/a.py")
        scan = ScanResult(scan_id="S-001", total_files=1, total_size_bytes=100, entries=[e])

        a = _asset("src/a.py")
        classified = ClassificationResult(
            classification_id="C-001",
            source_scan_id="S-001",
            total_classified=1,
            assets=[a],
        )

        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        r = Reconciler(orphan_tolerance_hours=0)
        report = r.reconcile(scan, classified, existing_index=index, dry_run=True)
        assert report.matched == 1
        assert len(report.orphans) == 0
        assert len(report.ghosts) == 0
        assert len(report.drifts) == 0

    def test_detect_orphan(self) -> None:
        e = _entry("src/new.py")
        scan = ScanResult(scan_id="S-002", total_files=1, total_size_bytes=100, entries=[e])

        a = _asset("src/new.py")
        classified = ClassificationResult(
            classification_id="C-002",
            source_scan_id="S-002",
            total_classified=1,
            assets=[a],
        )

        index = UnifiedAssetIndex(total_assets=0)

        r = Reconciler(orphan_tolerance_hours=0)
        report = r.reconcile(scan, classified, existing_index=index, dry_run=True)
        assert len(report.orphans) == 1

    def test_detect_ghost(self) -> None:
        scan = ScanResult(scan_id="S-003", total_files=0, total_size_bytes=0)

        classified = ClassificationResult(
            classification_id="C-003",
            source_scan_id="S-003",
            total_classified=0,
        )

        old = _asset("src/deleted.py")
        index = UnifiedAssetIndex(total_assets=1, assets=[old])

        r = Reconciler()
        report = r.reconcile(scan, classified, existing_index=index, dry_run=True)
        assert len(report.ghosts) == 1
        assert report.ghosts[0].registry_path == "src/deleted.py"

    def test_detect_drift(self) -> None:
        e = _entry("src/a.py", sha="b" * 64)
        scan = ScanResult(scan_id="S-004", total_files=1, total_size_bytes=100, entries=[e])

        a = _asset("src/a.py", sha="b" * 64)
        classified = ClassificationResult(
            classification_id="C-004",
            source_scan_id="S-004",
            total_classified=1,
            assets=[a],
        )

        old = _asset("src/a.py", sha="a" * 64)
        index = UnifiedAssetIndex(total_assets=1, assets=[old])

        r = Reconciler()
        report = r.reconcile(scan, classified, existing_index=index, dry_run=True)
        assert len(report.drifts) == 1
        assert report.drifts[0].registered_sha256 == "a" * 64
        assert report.drifts[0].disk_sha256 == "b" * 64

    def test_rename_detection(self) -> None:
        sha = "c" * 64
        e = _entry("src/new_name.py", sha=sha)
        scan = ScanResult(scan_id="S-005", total_files=1, total_size_bytes=100, entries=[e])

        a = _asset("src/new_name.py", sha=sha)
        classified = ClassificationResult(
            classification_id="C-005",
            source_scan_id="S-005",
            total_classified=1,
            assets=[a],
        )

        old = _asset("src/old_name.py", sha=sha)
        index = UnifiedAssetIndex(total_assets=1, assets=[old])

        r = Reconciler(orphan_tolerance_hours=0)
        report = r.reconcile(scan, classified, existing_index=index, dry_run=True)
        assert len(report.renames) > 0
        assert len(report.orphans) == 0
        assert len(report.ghosts) == 0
