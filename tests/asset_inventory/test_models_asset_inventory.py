# [A_test] module_id: MOD-GOV_models_asset_inventory | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-234 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_models
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 asset inventory models."""

from datetime import UTC, datetime

from zephyr.infrastructure.asset_inventory.models import (
    AssetLayer,
    AssetStatus,
    AssetType,
    ClassifiedAsset,
    DashboardData,
    DriftEntry,
    DriftType,
    GhostEntry,
    HealthGrade,
    HealthScore,
    Priority,
    RawFileEntry,
    ReconciliationReport,
    RenameEvent,
    ScanResult,
    UnifiedAssetIndex,
)


class TestRawFileEntry:
    def test_create_valid(self) -> None:
        e = RawFileEntry(
            relative_path="src/zephyr/test.py",
            absolute_path="/abs/src/zephyr/test.py",
            file_name="test.py",
            extension=".py",
            size_bytes=1024,
            mtime_utc=datetime(2026, 5, 7, tzinfo=UTC),
            sha256="a" * 64,
        )
        assert e.relative_path == "src/zephyr/test.py"
        assert e.size_bytes == 1024
        assert not e.is_binary


class TestScanResult:
    def test_scan_result_defaults(self) -> None:
        sr = ScanResult(
            scan_id="SCAN-20260507-001",
            total_files=42,
            total_size_bytes=1000000,
        )
        assert sr.scan_id == "SCAN-20260507-001"
        assert sr.total_files == 42
        assert sr.scan_mode == "full"
        assert sr.errors == []
        assert sr.entries == []


class TestClassifiedAsset:
    def test_defaults(self) -> None:
        a = ClassifiedAsset(
            relative_path="a/b.py",
            asset_type=AssetType.MODULE,
            size_bytes=100,
            mtime_utc=datetime.now(UTC),
            sha256="b" * 64,
        )
        assert a.layer == AssetLayer.CROSS_LAYER
        assert a.status == AssetStatus.ACTIVE
        assert a.priority == Priority.P3
        assert a.tags == []
        assert a.custom_metadata == {}

    def test_tags_and_metadata(self) -> None:
        a = ClassifiedAsset(
            relative_path="a/b.py",
            asset_type=AssetType.MODULE,
            size_bytes=100,
            mtime_utc=datetime.now(UTC),
            sha256="b" * 64,
            tags=["v2-refactor", "high-risk"],
            custom_metadata={"owner": "ai", "review_date": "2026Q3"},
        )
        assert len(a.tags) == 2
        assert a.custom_metadata["owner"] == "ai"


class TestUnifiedAssetIndex:
    def test_default_schema_version(self) -> None:
        idx = UnifiedAssetIndex(total_assets=10)
        assert idx.schema_version == "1.0.0"

    def test_model_dump_json(self) -> None:
        idx = UnifiedAssetIndex(
            total_assets=100,
            health_score="A",
            health_score_numeric=95.0,
            orphan_rate_pct=1.5,
            by_type={"module": 60, "script": 30, "doc": 10},
        )
        data = idx.model_dump(mode="json")
        assert data["total_assets"] == 100
        assert data["health_score"] == "A"
        assert data["orphan_rate_pct"] == 1.5


class TestGhostEntry:
    def test_cleanup_candidate(self) -> None:
        g = GhostEntry(
            registry_id="REG-MOD-001",
            registry_path="src/old/deleted.py",
            registered_type=AssetType.MODULE,
            days_ghost=35.0,
            candidates_for_cleanup=True,
        )
        assert g.candidates_for_cleanup

    def test_not_cleanup_candidate(self) -> None:
        g = GhostEntry(
            registry_id="REG-MOD-001",
            registry_path="src/old/deleted.py",
            registered_type=AssetType.MODULE,
            days_ghost=5.0,
            candidates_for_cleanup=False,
        )
        assert not g.candidates_for_cleanup


class TestDriftEntry:
    def test_sha256_drift(self) -> None:
        d = DriftEntry(
            relative_path="src/module.py",
            registered_sha256="a" * 64,
            disk_sha256="b" * 64,
            drift_types=[DriftType.SHA256],
        )
        assert DriftType.SHA256 in d.drift_types


class TestRenameEvent:
    def test_high_confidence(self) -> None:
        r = RenameEvent(
            old_path="src/old.py",
            new_path="src/new.py",
            sha256="c" * 64,
            confidence=0.95,
        )
        assert r.confidence >= 0.95
        assert not r.auto_fixed


class TestReconciliationReport:
    def test_dry_run_default(self) -> None:
        report = ReconciliationReport(
            report_id="RECON-20260507-001",
            scan_id="SCAN-20260507-001",
        )
        assert report.dry_run
        assert report.matched == 0

    def test_with_data(self) -> None:
        report = ReconciliationReport(
            report_id="RECON-20260507-002",
            scan_id="SCAN-20260507-002",
            dry_run=False,
            matched=950,
            auto_fixed_count=3,
            orphan_rate_before=3.0,
            orphan_rate_after=1.0,
            summary_text="OK",
        )
        assert not report.dry_run
        assert report.matched == 950
        assert report.auto_fixed_count == 3


class TestDashboardData:
    def test_basic(self) -> None:
        d = DashboardData(
            dashboard_id="DASH-20260507-001",
            health_score="A",
            total_assets=1000,
            orphan_rate_pct=1.0,
            ghost_rate_pct=0.5,
            drift_rate_pct=2.0,
        )
        assert d.health_score == "A"
        assert d.alerts == []


class TestHealthScore:
    def test_grade_a(self) -> None:
        hs = HealthScore(grade=HealthGrade.A, numeric=95.0)
        assert hs.grade == HealthGrade.A

    def test_weights_sum(self) -> None:
        hs = HealthScore(
            grade=HealthGrade.B,
            numeric=80.0,
            orphan_subscore=90.0,
            ghost_subscore=95.0,
            drift_subscore=85.0,
            recency_subscore=80.0,
        )
        total = hs.orphan_weight + hs.ghost_weight + hs.drift_weight + hs.recency_weight
        assert abs(total - 1.0) < 0.01
