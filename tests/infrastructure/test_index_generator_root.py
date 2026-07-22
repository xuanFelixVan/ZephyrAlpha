# [A_test] module_id: MOD-GOV_index_generator_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.test_index_generator
# [INVARIANTS] IndexGenerator.generate produces UnifiedAssetIndex; save uses atomic write
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_index_generator_root.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime

from zephyr.infrastructure.asset_inventory.index_generator import (
    IndexGenerator,
    MigrationPlan,
    MigrationStep,
    SchemaEvolutionManager,
    _calc_grade,
    _calc_numeric,
    _count_by_status,
    _to_yaml,
)
from zephyr.infrastructure.asset_inventory.models import (
    AssetStatus,
    AssetType,
    ClassificationResult,
    ClassifiedAsset,
    UnifiedAssetIndex,
)


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


def _make_classified(assets=None) -> ClassificationResult:
    if assets is None:
        assets = [_make_asset()]
    return ClassificationResult(
        classification_id="CLS-001",
        source_scan_id="SCAN-001",
        total_classified=len(assets),
        by_type={"module": len(assets)},
        by_layer={"L01": len(assets)},
        assets=assets,
    )


class TestIndexGeneratorInstantiation:
    def test_default(self):
        ig = IndexGenerator()
        assert ig.root is not None

    def test_custom_root(self, tmp_path):
        ig = IndexGenerator(root=tmp_path)
        assert ig.root == tmp_path


class TestIndexGeneratorGenerate:
    def test_basic_generate(self):
        ig = IndexGenerator()
        cr = _make_classified()
        index = ig.generate(cr)
        assert isinstance(index, UnifiedAssetIndex)
        assert index.total_assets >= 1

    def test_generate_preserves_by_type(self):
        ig = IndexGenerator()
        cr = _make_classified()
        index = ig.generate(cr)
        assert "module" in index.by_type

    def test_generate_with_empty_assets(self):
        ig = IndexGenerator()
        cr = _make_classified(assets=[])
        index = ig.generate(cr)
        assert index.total_assets == 0

    def test_generate_health_score(self):
        ig = IndexGenerator()
        cr = _make_classified()
        index = ig.generate(cr)
        assert index.health_score in ("A", "B", "C", "D", "F")


class TestIndexGeneratorSave:
    def test_save_creates_file(self, tmp_path):
        ig = IndexGenerator(root=tmp_path)
        cr = _make_classified()
        index = ig.generate(cr)
        out = ig.save(index, output_path=tmp_path / "index.yaml")
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "total_assets" in content


class TestCalcGrade:
    def test_a_grade(self):
        assert _calc_grade(0, 0, 0) == "A"

    def test_f_grade(self):
        assert _calc_grade(50, 50, 50) == "F"

    def test_b_grade(self):
        assert _calc_grade(5, 0, 0) == "B"


class TestCalcNumeric:
    def test_perfect_score(self):
        score = _calc_numeric(0, 0, 0)
        assert score >= 90

    def test_terrible_score(self):
        score = _calc_numeric(50, 50, 50)
        assert score < 50


class TestCountByStatus:
    def test_count(self):
        assets = [
            _make_asset(status=AssetStatus.ACTIVE),
            _make_asset(status=AssetStatus.ACTIVE),
            _make_asset(status=AssetStatus.STALE),
        ]
        result = _count_by_status(assets)
        assert result["active"] == 2
        assert result["stale"] == 1

    def test_empty(self):
        result = _count_by_status([])
        assert result == {}


class TestToYaml:
    def test_simple_dict(self):
        data = {"key": "value", "num": 42}
        result = _to_yaml(data)
        assert "key:" in result
        assert "num:" in result

    def test_nested_dict(self):
        data = {"outer": {"inner": "val"}}
        result = _to_yaml(data)
        assert "outer:" in result
        assert "inner:" in result

    def test_list_values(self):
        data = {"items": [1, 2, 3]}
        result = _to_yaml(data)
        assert "items:" in result

    def test_none_value(self):
        data = {"key": None}
        result = _to_yaml(data)
        assert "null" in result

    def test_bool_value(self):
        data = {"flag": True}
        result = _to_yaml(data)
        assert "true" in result


class TestSchemaEvolutionManagerInstantiation:
    def test_create(self, tmp_path):
        mgr = SchemaEvolutionManager(project_root=tmp_path)
        assert mgr._root == tmp_path


class TestSchemaEvolutionManagerCheckCompatibility:
    def test_current_version(self, tmp_path):
        mgr = SchemaEvolutionManager(project_root=tmp_path)
        plan = mgr.check_compatibility("1.0.0")
        assert isinstance(plan, MigrationPlan)
        assert plan.current_version == "1.0.0"

    def test_latest_version_no_steps(self, tmp_path):
        mgr = SchemaEvolutionManager(project_root=tmp_path)
        plan = mgr.check_compatibility("2.0.0")
        assert len(plan.steps) == 0

    def test_unknown_version_breaking(self, tmp_path):
        mgr = SchemaEvolutionManager(project_root=tmp_path)
        plan = mgr.check_compatibility("0.0.1")
        assert plan.is_breaking is True

    def test_migration_steps(self, tmp_path):
        mgr = SchemaEvolutionManager(project_root=tmp_path)
        plan = mgr.check_compatibility("1.0.0")
        assert len(plan.steps) >= 1


class TestSchemaEvolutionManagerRunMigration:
    def test_migrate_1_0_to_1_1(self, tmp_path):
        mgr = SchemaEvolutionManager(project_root=tmp_path)
        plan = mgr.check_compatibility("1.0.0")
        data = {"schema_version": "1.0.0", "assets": [{"relative_path": "a.py"}]}
        result = mgr.run_migration(plan, data)
        assert result["schema_version"] == "2.0.0"

    def test_migrate_no_steps(self, tmp_path):
        mgr = SchemaEvolutionManager(project_root=tmp_path)
        plan = mgr.check_compatibility("2.0.0")
        data = {"schema_version": "2.0.0"}
        result = mgr.run_migration(plan, data)
        assert result["schema_version"] == "2.0.0"


class TestMigrationStep:
    def test_create(self):
        step = MigrationStep(version="1.1.0", description="test step")
        assert step.reverted is False
        assert step.applied_at is None


class TestMigrationPlan:
    def test_create(self):
        plan = MigrationPlan(current_version="1.0.0", target_version="2.0.0")
        assert plan.is_breaking is False
        assert plan.requires_downtime is False
