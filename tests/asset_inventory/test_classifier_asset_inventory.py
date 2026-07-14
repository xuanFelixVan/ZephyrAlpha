# [A_test] module_id: SRC-TST-0067 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-225 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_classifier
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 Classifier module."""

from datetime import UTC, datetime

from zephyr.infrastructure.asset_inventory.classifier import Classifier
from zephyr.infrastructure.asset_inventory.models import (
    AssetType,
    RawFileEntry,
    ScanResult,
)


def _make_entry(path: str, ext: str = ".py", size: int = 100) -> RawFileEntry:
    return RawFileEntry(
        relative_path=path,
        absolute_path=f"/abs/{path}",
        file_name=path.split("/")[-1],
        extension=ext,
        size_bytes=size,
        mtime_utc=datetime.now(UTC),
        sha256="d" * 64,
    )


class TestClassifier:
    def test_classify_module(self) -> None:
        c = Classifier()
        entry = _make_entry("src/zephyr/asset-inventory/scanner.py")
        scan = ScanResult(scan_id="S-001", total_files=1, total_size_bytes=100, entries=[entry])
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.MODULE

    def test_classify_gate(self) -> None:
        c = Classifier()
        entry = _make_entry("src/zephyr/gov_enforcement/rule_enforcement/g1_ingest.yaml", ext=".yaml")
        scan = ScanResult(scan_id="S-002", total_files=1, total_size_bytes=100, entries=[entry])
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.GATE

    def test_classify_script(self) -> None:
        c = Classifier()
        entry = _make_entry("scripts/governance/tool.py")
        scan = ScanResult(scan_id="S-003", total_files=1, total_size_bytes=100, entries=[entry])
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.SCRIPT

    def test_classify_doc(self) -> None:
        c = Classifier()
        entry = _make_entry("docs/03_modules/readme.md", ext=".md")
        scan = ScanResult(scan_id="S-004", total_files=1, total_size_bytes=100, entries=[entry])
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.DOC

    def test_classify_config(self) -> None:
        c = Classifier()
        entry = _make_entry("config/settings.yaml", ext=".yaml")
        scan = ScanResult(scan_id="S-005", total_files=1, total_size_bytes=100, entries=[entry])
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.CONFIG

    def test_classify_test(self) -> None:
        c = Classifier()
        entry = _make_entry("tests/asset-inventory/test_models.py")
        scan = ScanResult(scan_id="S-006", total_files=1, total_size_bytes=100, entries=[entry])
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.TEST

    def test_classify_data(self) -> None:
        c = Classifier()
        entry = _make_entry("data/reports/metrics.db", ext=".db")
        scan = ScanResult(scan_id="S-007", total_files=1, total_size_bytes=100, entries=[entry])
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.DATA

    def test_classify_registry(self) -> None:
        c = Classifier()
        entry = _make_entry("src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml", ext=".yaml")
        scan = ScanResult(scan_id="S-008", total_files=1, total_size_bytes=100, entries=[entry])
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.REGISTRY

    def test_classify_unknown(self) -> None:
        c = Classifier()
        entry = _make_entry("scripts/governance/tool.md", ext=".md")
        scan = ScanResult(scan_id="S-009", total_files=1, total_size_bytes=100, entries=[entry])
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.UNKNOWN

    def test_unknown_threshold_warning(self) -> None:
        c = Classifier(unknown_threshold_pct=0.0)
        entry = _make_entry("scripts/governance/tool.md", ext=".md")
        scan = ScanResult(scan_id="S-010", total_files=1, total_size_bytes=100, entries=[entry])
        result = c.classify(scan)
        assert result.unknown_pct == 100.0

    def test_by_type_stats(self) -> None:
        c = Classifier()
        e1 = _make_entry("src/zephyr/a.py")
        e2 = _make_entry("src/zephyr/b.py")
        e3 = _make_entry("docs/readme.md", ext=".md")
        scan = ScanResult(scan_id="S-011", total_files=3, total_size_bytes=300, entries=[e1, e2, e3])
        result = c.classify(scan)
        assert result.by_type["module"] == 2
        assert result.by_type["doc"] == 1
