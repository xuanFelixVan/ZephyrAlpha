# [A_test] module_id: MOD-GOV_ba_dependency_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md
# [MODULE] tests.test_ba_dependency_manager
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_ba_dependency_manager.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.architecture_governance.dependency_manager import (
    DEPENDENCIES,
    DependencyTier,
    ManagedDependency,
    get_by_tier,
    get_core_deps,
)


class TestDependencyTier:
    def test_all_tiers_exist(self):
        assert DependencyTier.TIER1_CORE == "Tier1_CORE"
        assert DependencyTier.TIER2_ENHANCED == "Tier2_ENHANCED"
        assert DependencyTier.TIER3_OPTIONAL == "Tier3_OPTIONAL"

    def test_is_str_enum(self):
        assert isinstance(DependencyTier.TIER1_CORE, str)

    def test_tier_count(self):
        assert len(DependencyTier) == 3


class TestManagedDependency:
    def test_required_fields(self):
        dep = ManagedDependency(name="TestDep", tier=DependencyTier.TIER1_CORE)
        assert dep.name == "TestDep"
        assert dep.tier == DependencyTier.TIER1_CORE
        assert dep.redundancy == ""
        assert dep.fallback is None

    def test_all_fields(self):
        dep = ManagedDependency(
            name="TestDep",
            tier=DependencyTier.TIER2_ENHANCED,
            redundancy="dual",
            fallback="Backup",
        )
        assert dep.redundancy == "dual"
        assert dep.fallback == "Backup"


class TestDependencies:
    def test_dependencies_non_empty(self):
        assert len(DEPENDENCIES) > 0

    def test_all_dependencies_are_managed(self):
        for dep in DEPENDENCIES:
            assert isinstance(dep, ManagedDependency)

    def test_at_least_one_core_dependency(self):
        core = [d for d in DEPENDENCIES if d.tier == DependencyTier.TIER1_CORE]
        assert len(core) >= 1

    def test_each_tier_represented(self):
        tiers = {d.tier for d in DEPENDENCIES}
        assert DependencyTier.TIER1_CORE in tiers
        assert DependencyTier.TIER2_ENHANCED in tiers
        assert DependencyTier.TIER3_OPTIONAL in tiers


class TestGetByTier:
    def test_get_tier1_core(self):
        result = get_by_tier(DependencyTier.TIER1_CORE)
        assert len(result) > 0
        for dep in result:
            assert dep.tier == DependencyTier.TIER1_CORE

    def test_get_tier2_enhanced(self):
        result = get_by_tier(DependencyTier.TIER2_ENHANCED)
        assert len(result) > 0
        for dep in result:
            assert dep.tier == DependencyTier.TIER2_ENHANCED

    def test_get_tier3_optional(self):
        result = get_by_tier(DependencyTier.TIER3_OPTIONAL)
        assert len(result) > 0
        for dep in result:
            assert dep.tier == DependencyTier.TIER3_OPTIONAL

    def test_get_returns_managed_dependencies(self):
        result = get_by_tier(DependencyTier.TIER1_CORE)
        for dep in result:
            assert isinstance(dep, ManagedDependency)


class TestGetCoreDeps:
    def test_returns_core_deps(self):
        result = get_core_deps()
        assert len(result) > 0
        for dep in result:
            assert dep.tier == DependencyTier.TIER1_CORE

    def test_core_deps_have_fallback(self):
        for dep in get_core_deps():
            assert dep.fallback is not None

    def test_core_deps_have_redundancy(self):
        for dep in get_core_deps():
            assert dep.redundancy != ""
