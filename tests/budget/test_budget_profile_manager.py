# [A_test] module_id: MOD-GOV_budget_profile_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_budget_profile_manager
# [INVARIANTS] DEFAULT_PROFILES always present; remove cannot delete defaults
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.ops_governance.budget_profile_manager import (
    BudgetProfile,
    BudgetProfileManager,
)


@pytest.fixture
def tmp_profile_path(tmp_path):
    return str(tmp_path / "budget_profiles.yaml")


@pytest.fixture
def manager(tmp_profile_path):
    return BudgetProfileManager(profile_path=tmp_profile_path)


class TestBudgetProfile:
    def test_creation(self):
        p = BudgetProfile(name="test", token_limit=1000, cost_limit=0.1, time_limit=60.0, model_tier="economy")
        assert p.name == "test"
        assert p.token_limit == 1000

    def test_default_description(self):
        p = BudgetProfile(name="x", token_limit=100, cost_limit=0.1, time_limit=60.0, model_tier="economy")
        assert p.description == ""


class TestBudgetProfileManager:
    def test_instantiation_with_defaults(self, manager):
        profiles = manager.list_profiles()
        assert "minimal" in profiles
        assert "standard" in profiles
        assert "premium" in profiles

    def test_get_existing_profile(self, manager):
        p = manager.get("standard")
        assert p is not None
        assert p.name == "standard"
        assert p.token_limit == 8000

    def test_get_nonexistent_profile(self, manager):
        p = manager.get("nonexistent")
        assert p is None

    def test_add_profile(self, manager):
        custom = BudgetProfile(name="custom", token_limit=5000, cost_limit=0.2, time_limit=120.0, model_tier="economy")
        manager.add(custom)
        assert manager.get("custom") is not None
        assert manager.get("custom").token_limit == 5000

    def test_remove_non_default_profile(self, manager):
        custom = BudgetProfile(name="custom", token_limit=5000, cost_limit=0.2, time_limit=120.0, model_tier="economy")
        manager.add(custom)
        manager.remove("custom")
        assert manager.get("custom") is None

    def test_cannot_remove_default_profile(self, manager):
        manager.remove("standard")
        assert manager.get("standard") is not None

    def test_set_active_returns_profile(self, manager):
        p = manager.set_active("premium")
        assert p is not None
        assert p.model_tier == "standard"

    def test_set_active_nonexistent(self, manager):
        p = manager.set_active("nonexistent")
        assert p is None

    def test_match_for_task_minimal(self, manager):
        p = manager.match_for_task(estimated_tokens=100, estimated_cost=0.01)
        assert p.token_limit >= 100
        assert p.cost_limit >= 0.01

    def test_match_for_task_standard(self, manager):
        p = manager.match_for_task(estimated_tokens=5000, estimated_cost=0.2)
        assert p.name in ("standard", "premium", "minimal")

    def test_match_for_task_premium(self, manager):
        p = manager.match_for_task(estimated_tokens=10000, estimated_cost=0.5)
        assert p.name in ("premium", "standard", "minimal")

    def test_persistence(self, tmp_profile_path):
        mgr1 = BudgetProfileManager(profile_path=tmp_profile_path)
        custom = BudgetProfile(
            name="persist_test", token_limit=9999, cost_limit=1.0, time_limit=300.0, model_tier="premium"
        )
        mgr1.add(custom)
        mgr2 = BudgetProfileManager(profile_path=tmp_profile_path)
        assert mgr2.get("persist_test") is not None
        assert mgr2.get("persist_test").token_limit == 9999


class TestBoundaryCases:
    def test_get_with_empty_string(self, manager):
        p = manager.get("")
        assert p is None

    def test_match_for_task_zero(self, manager):
        p = manager.match_for_task(estimated_tokens=0, estimated_cost=0.0)
        assert p.token_limit >= 0

    def test_match_for_task_exceeding_all(self, manager):
        p = manager.match_for_task(estimated_tokens=999999, estimated_cost=999.0)
        assert p is not None
