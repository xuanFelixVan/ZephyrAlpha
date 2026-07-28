# [A_test] module_id: MOD-GOV_schema_evolution_asset_inventory | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-240 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_schema_evolution
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §34 Schema Evolution module."""

from pathlib import Path

from zephyr.infrastructure.asset_inventory.index_generator import (
    MigrationPlan,
    MigrationStep,
    SchemaEvolutionManager,
)
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


class TestMigrationStep:
    def test_model_creation(self) -> None:
        s = MigrationStep(version="1.1.0", description="test")
        assert s.version == "1.1.0"
        assert not s.reverted


class TestMigrationPlan:
    def test_model_defaults(self) -> None:
        p = MigrationPlan(current_version="1.0.0", target_version="2.0.0")
        assert p.asset_type == "unified-asset-index"
        assert not p.requires_downtime


class TestSchemaEvolutionManager:
    def test_constructor(self) -> None:
        mgr = SchemaEvolutionManager(REPO_ROOT)
        assert mgr.VERSIONS

    def test_check_compatibility_same_version(self) -> None:
        mgr = SchemaEvolutionManager(REPO_ROOT)
        plan = mgr.check_compatibility("2.0.0")
        assert plan.steps == []
        assert not plan.is_breaking

    def test_check_compatibility_upgrade_path(self) -> None:
        mgr = SchemaEvolutionManager(REPO_ROOT)
        plan = mgr.check_compatibility("1.0.0")
        assert len(plan.steps) == 2
        assert plan.steps[0].version == "1.1.0"
        assert plan.steps[1].version == "2.0.0"

    def test_check_compatibility_unknown_version(self) -> None:
        mgr = SchemaEvolutionManager(REPO_ROOT)
        plan = mgr.check_compatibility("0.5.0")
        assert plan.is_breaking
        assert plan.requires_downtime

    def test_migrate_1_0_to_1_1(self) -> None:
        mgr = SchemaEvolutionManager(REPO_ROOT)
        data = {"schema_version": "1.0.0", "total_assets": 10, "assets": [{"tags": None}]}
        result = mgr.migrate_1_0_to_1_1(data)
        assert result["schema_version"] == "1.1.0"
        assert result["assets"][0]["tags"] == []

    def test_migrate_1_1_to_2_0(self) -> None:
        mgr = SchemaEvolutionManager(REPO_ROOT)
        data = {"schema_version": "1.1.0"}
        result = mgr.migrate_1_1_to_2_0(data)
        assert result["schema_version"] == "2.0.0"
        assert result["orphan_rate_pct"] == 0.0

    def test_run_migration_full(self) -> None:
        mgr = SchemaEvolutionManager(REPO_ROOT)
        plan = mgr.check_compatibility("1.0.0")
        data = {"schema_version": "1.0.0", "total_assets": 0, "assets": []}
        result = mgr.run_migration(plan, data)
        assert result["schema_version"] == "2.0.0"
