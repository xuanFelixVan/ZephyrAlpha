# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_schema_evolution
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""Tests for MOD-INF-026 §34 Schema Evolution module."""

from pathlib import Path

from zephyr.asset_inventory.index_generator import (
    MigrationPlan,
    MigrationStep,
    SchemaEvolutionManager,
)


class TestMigrationStep:
    def test_model_creation(self) -> None:
        s = MigrationStep(version="1.1.0", description="test")
        assert s.version == "1.1.0"
        assert not s.reverted


class TestMigrationPlan:
    def test_model_defaults(self) -> None:
        p = MigrationPlan(current_version="1.0.0", target_version="2.0.0")
        assert p.asset_type == "unified_asset_index"
        assert not p.requires_downtime


class TestSchemaEvolutionManager:
    def test_constructor(self) -> None:
        mgr = SchemaEvolutionManager(Path("D:/ZephyrAlpha"))
        assert mgr.VERSIONS

    def test_check_compatibility_same_version(self) -> None:
        mgr = SchemaEvolutionManager(Path("D:/ZephyrAlpha"))
        plan = mgr.check_compatibility("2.0.0")
        assert plan.steps == []
        assert not plan.is_breaking

    def test_check_compatibility_upgrade_path(self) -> None:
        mgr = SchemaEvolutionManager(Path("D:/ZephyrAlpha"))
        plan = mgr.check_compatibility("1.0.0")
        assert len(plan.steps) == 2
        assert plan.steps[0].version == "1.1.0"
        assert plan.steps[1].version == "2.0.0"

    def test_check_compatibility_unknown_version(self) -> None:
        mgr = SchemaEvolutionManager(Path("D:/ZephyrAlpha"))
        plan = mgr.check_compatibility("0.5.0")
        assert plan.is_breaking
        assert plan.requires_downtime

    def test_migrate_1_0_to_1_1(self) -> None:
        mgr = SchemaEvolutionManager(Path("D:/ZephyrAlpha"))
        data = {"schema_version": "1.0.0", "total_assets": 10, "assets": [{"tags": None}]}
        result = mgr._migrate_1_0_to_1_1(data)
        assert result["schema_version"] == "1.1.0"
        assert result["assets"][0]["tags"] == []

    def test_migrate_1_1_to_2_0(self) -> None:
        mgr = SchemaEvolutionManager(Path("D:/ZephyrAlpha"))
        data = {"schema_version": "1.1.0"}
        result = mgr._migrate_1_1_to_2_0(data)
        assert result["schema_version"] == "2.0.0"
        assert result["orphan_rate_pct"] == 0.0

    def test_run_migration_full(self) -> None:
        mgr = SchemaEvolutionManager(Path("D:/ZephyrAlpha"))
        plan = mgr.check_compatibility("1.0.0")
        data = {"schema_version": "1.0.0", "total_assets": 0, "assets": []}
        result = mgr.run_migration(plan, data)
        assert result["schema_version"] == "2.0.0"
