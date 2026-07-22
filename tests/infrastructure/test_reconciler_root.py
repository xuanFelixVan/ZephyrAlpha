# [A_test] module_id: MOD-GOV_reconciler_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.test_reconciler
# [INVARIANTS] Reconciler.reconcile returns ReconciliationReport; detects orphans/ghosts/drifts
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_reconciler_root.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from zephyr.infrastructure.asset_inventory.models import (
    AssetType,
    ClassificationResult,
    ClassifiedAsset,
    RawFileEntry,
    ReconciliationReport,
    ScanResult,
    UnifiedAssetIndex,
)
from zephyr.infrastructure.asset_inventory.reconciler import Reconciler, _generate_report_id


def _make_entry(**overrides) -> RawFileEntry:
    defaults = dict(
        relative_path="src/zephyr/test.py",
        absolute_path="/abs/test.py",
        file_name="test.py",
        extension=".py",
        size_bytes=100,
        mtime_utc=datetime.now(UTC),
        sha256="abc123",
        is_binary=False,
    )
    defaults.update(overrides)
    return RawFileEntry(**defaults)


def _make_asset(**overrides) -> ClassifiedAsset:
    defaults = dict(
        relative_path="src/zephyr/test.py",
        asset_type=AssetType.MODULE,
        size_bytes=100,
        mtime_utc=datetime.now(UTC),
        sha256="abc123",
    )
    defaults.update(overrides)
    return ClassifiedAsset(**defaults)


def _make_scan(entries=None) -> ScanResult:
    if entries is None:
        entries = [_make_entry()]
    return ScanResult(
        scan_id="SCAN-001",
        scanned_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
        total_files=len(entries),
        total_size_bytes=sum(e.size_bytes for e in entries),
        scan_mode="full",
        entries=entries,
    )


def _make_classified(assets=None) -> ClassificationResult:
    if assets is None:
        assets = [_make_asset()]
    return ClassificationResult(
        classification_id="CLS-001",
        source_scan_id="SCAN-001",
        total_classified=len(assets),
        assets=assets,
    )


class TestReconcilerInstantiation:
    def test_default(self):
        r = Reconciler()
        assert r.orphan_tolerance_hours == 24
        assert r.ghost_max_age_days == 30

    def test_custom(self, tmp_path):
        r = Reconciler(orphan_tolerance_hours=48, ghost_max_age_days=60, root=tmp_path)
        assert r.orphan_tolerance_hours == 48
        assert r.root == tmp_path


class TestReconcilerReconcile:
    def test_basic_reconcile(self):
        r = Reconciler()
        scan = _make_scan()
        classified = _make_classified()
        report = r.reconcile(scan, classified)
        assert isinstance(report, ReconciliationReport)
        assert report.scan_id == "SCAN-001"

    def test_detect_drift(self):
        r = Reconciler()
        old_time = datetime.now(UTC) - timedelta(hours=48)
        scan_entry = _make_entry(sha256="new_sha", size_bytes=200)
        scan = _make_scan(entries=[scan_entry])
        asset = _make_asset(sha256="old_sha", size_bytes=100, relative_path="src/zephyr/test.py")
        classified = _make_classified(assets=[asset])
        index = UnifiedAssetIndex(
            total_assets=1,
            assets=[_make_asset(sha256="old_sha", size_bytes=100, relative_path="src/zephyr/test.py")],
        )
        report = r.reconcile(scan, classified, existing_index=index)
        assert len(report.drifts) >= 1

    def test_detect_ghost(self):
        scan = _make_scan(entries=[])
        classified = _make_classified(assets=[])
        index = UnifiedAssetIndex(
            total_assets=1,
            last_reconciliation_at=datetime.now(UTC) - timedelta(days=5),
            assets=[_make_asset(relative_path="src/zephyr/ghost.py")],
        )
        r = Reconciler()
        report = r.reconcile(scan, classified, existing_index=index)
        assert len(report.ghosts) >= 1

    def test_dry_run_default(self):
        r = Reconciler()
        scan = _make_scan()
        classified = _make_classified()
        report = r.reconcile(scan, classified)
        assert report.dry_run is True

    def test_dry_run_false(self):
        r = Reconciler()
        scan = _make_scan()
        classified = _make_classified()
        report = r.reconcile(scan, classified, dry_run=False)
        assert report.dry_run is False


class TestReconcilerSave:
    def test_save_creates_file(self, tmp_path):
        r = Reconciler(root=tmp_path)
        scan = _make_scan()
        classified = _make_classified()
        report = r.reconcile(scan, classified)
        out = r.save(report, output_path=tmp_path / "report.md")
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "资产对账报告" in content


class TestGenerateReportId:
    def test_format(self):
        rid = _generate_report_id()
        assert rid.startswith("RECON-")
