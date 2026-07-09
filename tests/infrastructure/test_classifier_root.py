# [A_test] module_id: SRC-TST-0524 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.test_classifier
# [INVARIANTS] Classifier.classify returns ClassificationResult; type mapping rules are deterministic
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_classifier_root.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime

from zephyr.infrastructure.asset_inventory.classifier import (
    LAYER_BY_DIR,
    REGISTRY_PATTERNS,
    STATUS_BY_DIR,
    TYPE_MAPPING,
    Classifier,
    _generate_classification_id,
)
from zephyr.infrastructure.asset_inventory.models import (
    AssetLayer,
    AssetStatus,
    AssetType,
    ClassificationResult,
    RawFileEntry,
    ScanResult,
)


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


class TestClassifierInstantiation:
    def test_default(self):
        c = Classifier()
        assert c.type_mapping == TYPE_MAPPING
        assert c.unknown_threshold_pct == 10.0

    def test_custom_mapping(self):
        custom = [("custom/", [".py"], AssetType.MODULE)]
        c = Classifier(type_mapping=custom, unknown_threshold_pct=5.0)
        assert c.type_mapping == custom
        assert c.unknown_threshold_pct == 5.0


class TestClassifierClassify:
    def test_classify_module(self):
        entry = _make_entry(relative_path="src/zephyr/core.py", extension=".py")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert isinstance(result, ClassificationResult)
        assert result.assets[0].asset_type == AssetType.MODULE

    def test_classify_script(self):
        entry = _make_entry(relative_path="scripts/scan.py", extension=".py")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.SCRIPT

    def test_classify_gate(self):
        entry = _make_entry(relative_path="src/zephyr/governance/rule_enforcement/g1_ingest.yaml", extension=".yaml")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.GATE

    def test_classify_doc(self):
        entry = _make_entry(relative_path="docs/guide.md", extension=".md")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.DOC

    def test_classify_config(self):
        entry = _make_entry(relative_path="config/settings.yaml", extension=".yaml")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.CONFIG

    def test_classify_test(self):
        entry = _make_entry(relative_path="tests/test_foo.py", extension=".py")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.TEST

    def test_classify_data(self):
        entry = _make_entry(relative_path="data/index.db", extension=".db")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.DATA

    def test_classify_registry(self):
        entry = _make_entry(relative_path="src/zephyr/governance/rule_enforcement/_registry.yaml", extension=".yaml")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.REGISTRY

    def test_classify_unknown(self):
        entry = _make_entry(relative_path="random/file.xyz", extension=".xyz")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].asset_type == AssetType.UNKNOWN

    def test_classify_empty_scan(self):
        scan = _make_scan(entries=[])
        c = Classifier()
        result = c.classify(scan)
        assert result.total_classified == 0
        assert result.unknown_pct == 0.0

    def test_classify_unknown_pct(self):
        entries = [
            _make_entry(relative_path="src/zephyr/a.py", extension=".py"),
            _make_entry(relative_path="random/b.xyz", extension=".xyz"),
        ]
        scan = _make_scan(entries=entries)
        c = Classifier()
        result = c.classify(scan)
        assert result.unknown_count == 1
        assert result.unknown_pct == 50.0

    def test_classify_by_type(self):
        entries = [
            _make_entry(relative_path="src/zephyr/a.py", extension=".py"),
            _make_entry(relative_path="scripts/b.py", extension=".py"),
        ]
        scan = _make_scan(entries=entries)
        c = Classifier()
        result = c.classify(scan)
        assert "module" in result.by_type
        assert "script" in result.by_type

    def test_classify_deprecated_status(self):
        entry = _make_entry(relative_path="src/_deprecated/old.py", extension=".py")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].status == AssetStatus.DEPRECATED

    def test_classify_archived_status(self):
        entry = _make_entry(relative_path="src/_archived/old.py", extension=".py")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].status == AssetStatus.ARCHIVED


class TestClassifierConfidence:
    def test_known_type_confidence(self):
        entry = _make_entry(relative_path="src/zephyr/a.py", extension=".py")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].classification_confidence == 0.85

    def test_unknown_type_confidence(self):
        entry = _make_entry(relative_path="random/b.xyz", extension=".xyz")
        scan = _make_scan(entries=[entry])
        c = Classifier()
        result = c.classify(scan)
        assert result.assets[0].classification_confidence == 0.3


class TestTypeMapping:
    def test_mapping_not_empty(self):
        assert len(TYPE_MAPPING) > 0

    def test_mapping_structure(self):
        for prefix, extensions, atype in TYPE_MAPPING:
            assert isinstance(prefix, str)
            assert isinstance(extensions, list)
            assert isinstance(atype, AssetType)


class TestLayerByDir:
    def test_mapping_not_empty(self):
        assert len(LAYER_BY_DIR) > 0

    def test_values_are_asset_layer(self):
        for prefix, layer in LAYER_BY_DIR.items():
            assert isinstance(layer, AssetLayer)


class TestStatusByDir:
    def test_mapping_not_empty(self):
        assert len(STATUS_BY_DIR) > 0

    def test_values_are_asset_status(self):
        for suffix, status in STATUS_BY_DIR.items():
            assert isinstance(status, AssetStatus)


class TestRegistryPatterns:
    def test_patterns_exist(self):
        assert len(REGISTRY_PATTERNS) > 0


class TestGenerateClassificationId:
    def test_format(self):
        cid = _generate_classification_id()
        assert cid.startswith("CLS-")
