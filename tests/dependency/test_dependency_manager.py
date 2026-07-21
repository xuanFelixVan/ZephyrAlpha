# [A_test] module_id: MOD-GOV_dependency_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [MODULE] tests.test_dependency_manager
# [INVARIANTS] DEPENDENCIES contains at least one TIER1_CORE dep; get_by_tier returns subset
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_dependency_manager.py
# [TTL] task_bound

from __future__ import annotations

import pytest
from pydantic import ValidationError

from zephyr.governance.architecture_governance.dependency_manager import (
    DEPENDENCIES,
    DependencyTier,
    ManagedDependency,
    get_by_tier,
    get_core_deps,
)


class TestDependencyTier:
    def test_tier_values(self):
        assert DependencyTier.TIER1_CORE.value == "Tier1_CORE"
        assert DependencyTier.TIER2_ENHANCED.value == "Tier2_ENHANCED"
        assert DependencyTier.TIER3_OPTIONAL.value == "Tier3_OPTIONAL"

    def test_is_str_enum(self):
        assert isinstance(DependencyTier.TIER1_CORE, str)
        assert isinstance(DependencyTier.TIER2_ENHANCED, str)
        assert isinstance(DependencyTier.TIER3_OPTIONAL, str)

    def test_member_count(self):
        assert len(DependencyTier) == 3

    def test_iteration_covers_all(self):
        values = {t.value for t in DependencyTier}
        expected = {"Tier1_CORE", "Tier2_ENHANCED", "Tier3_OPTIONAL"}
        assert values == expected


class TestManagedDependency:
    def test_creation_with_defaults(self):
        dep = ManagedDependency(name="TestDep", tier=DependencyTier.TIER1_CORE)
        assert dep.name == "TestDep"
        assert dep.tier == DependencyTier.TIER1_CORE
        assert dep.redundancy == ""
        assert dep.fallback is None

    def test_creation_with_all_fields(self):
        dep = ManagedDependency(
            name="TestDep",
            tier=DependencyTier.TIER2_ENHANCED,
            redundancy="dual",
            fallback="Backup",
        )
        assert dep.name == "TestDep"
        assert dep.tier == DependencyTier.TIER2_ENHANCED
        assert dep.redundancy == "dual"
        assert dep.fallback == "Backup"

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            ManagedDependency(tier=DependencyTier.TIER1_CORE)

    def test_missing_tier_raises(self):
        with pytest.raises(ValidationError):
            ManagedDependency(name="NoTier")

    def test_empty_name_allowed(self):
        dep = ManagedDependency(name="", tier=DependencyTier.TIER1_CORE)
        assert dep.name == ""

    def test_fallback_none_explicit(self):
        dep = ManagedDependency(name="X", tier=DependencyTier.TIER3_OPTIONAL, fallback=None)
        assert dep.fallback is None

    def test_invalid_tier_raises(self):
        with pytest.raises(ValidationError):
            ManagedDependency(name="Bad", tier="INVALID_TIER")


class TestDependencies:
    def test_not_empty(self):
        assert len(DEPENDENCIES) > 0

    def test_all_are_managed(self):
        for dep in DEPENDENCIES:
            assert isinstance(dep, ManagedDependency)

    def test_each_tier_represented(self):
        tiers = {d.tier for d in DEPENDENCIES}
        assert DependencyTier.TIER1_CORE in tiers
        assert DependencyTier.TIER2_ENHANCED in tiers
        assert DependencyTier.TIER3_OPTIONAL in tiers

    def test_all_names_non_empty(self):
        for dep in DEPENDENCIES:
            assert dep.name != ""

    def test_core_deps_have_fallbacks(self):
        core = [d for d in DEPENDENCIES if d.tier == DependencyTier.TIER1_CORE]
        for dep in core:
            assert dep.fallback is not None


class TestGetByTier:
    def test_core_tier(self):
        result = get_by_tier(DependencyTier.TIER1_CORE)
        assert len(result) > 0
        assert all(d.tier == DependencyTier.TIER1_CORE for d in result)

    def test_enhanced_tier(self):
        result = get_by_tier(DependencyTier.TIER2_ENHANCED)
        assert len(result) > 0
        assert all(d.tier == DependencyTier.TIER2_ENHANCED for d in result)

    def test_optional_tier(self):
        result = get_by_tier(DependencyTier.TIER3_OPTIONAL)
        assert len(result) > 0
        assert all(d.tier == DependencyTier.TIER3_OPTIONAL for d in result)

    def test_returns_managed_instances(self):
        result = get_by_tier(DependencyTier.TIER1_CORE)
        for dep in result:
            assert isinstance(dep, ManagedDependency)

    def test_no_cross_tier_contamination(self):
        core = get_by_tier(DependencyTier.TIER1_CORE)
        enhanced = get_by_tier(DependencyTier.TIER2_ENHANCED)
        core_names = {d.name for d in core}
        enhanced_names = {d.name for d in enhanced}
        assert core_names.isdisjoint(enhanced_names)


class TestGetCoreDeps:
    def test_returns_core(self):
        result = get_core_deps()
        assert len(result) > 0
        assert all(d.tier == DependencyTier.TIER1_CORE for d in result)

    def test_equivalent_to_get_by_tier(self):
        assert get_core_deps() == get_by_tier(DependencyTier.TIER1_CORE)

    def test_core_deps_have_fallback(self):
        for dep in get_core_deps():
            assert dep.fallback is not None

    def test_core_deps_have_redundancy(self):
        for dep in get_core_deps():
            assert dep.redundancy != ""


class TestBoundary:
    def test_managed_dependency_no_args_raises(self):
        with pytest.raises(ValidationError):
            ManagedDependency()

    def test_managed_dependency_none_name_raises(self):
        with pytest.raises(ValidationError):
            ManagedDependency(name=None, tier=DependencyTier.TIER1_CORE)

    def test_managed_dependency_none_tier_raises(self):
        with pytest.raises(ValidationError):
            ManagedDependency(name="X", tier=None)

    def test_get_by_tier_returns_list(self):
        result = get_by_tier(DependencyTier.TIER1_CORE)
        assert isinstance(result, list)

    def test_get_core_deps_returns_list(self):
        result = get_core_deps()
        assert isinstance(result, list)

    def test_dependencies_is_list(self):
        assert isinstance(DEPENDENCIES, list)

    def test_optional_dep_may_have_no_fallback(self):
        optional = get_by_tier(DependencyTier.TIER3_OPTIONAL)
        has_none_fallback = any(d.fallback is None for d in optional)
        assert has_none_fallback
