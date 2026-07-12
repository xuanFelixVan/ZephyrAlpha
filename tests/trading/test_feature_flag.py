# [A_test] module_id: SRC-TST-0897 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_feature_flag
# [INVARIANTS] is_enabled returns True for unknown flags; set creates flag+audit entry
# [MODIFY-GUARD] src/zephyr/orchestrator/feature_flag.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] set/is_enabled/get_all never raise
# [TESTS] tests/test_feature_flag.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.governance.feature_flag import FeatureFlag, FeatureFlagManager


class TestFeatureFlagModel:
    def test_default_values(self):
        flag = FeatureFlag(contract_id="CT-TEST")
        assert flag.contract_id == "CT-TEST"
        assert flag.enabled is True
        assert flag.description == ""

    def test_custom_values(self):
        flag = FeatureFlag(contract_id="CT-X", enabled=False, description="test flag")
        assert flag.enabled is False
        assert flag.description == "test flag"


class TestFeatureFlagManagerInstantiation:
    def test_empty_flags_on_init(self):
        mgr = FeatureFlagManager()
        assert mgr._flags == {}

    def test_empty_audit_on_init(self):
        mgr = FeatureFlagManager()
        assert mgr._audit == []


class TestSet:
    def test_set_returns_feature_flag(self):
        mgr = FeatureFlagManager()
        flag = mgr.set("CT-TEST", True)
        assert isinstance(flag, FeatureFlag)
        assert flag.contract_id == "CT-TEST"
        assert flag.enabled is True

    def test_set_stores_flag(self):
        mgr = FeatureFlagManager()
        mgr.set("CT-A", True, "desc A")
        assert "CT-A" in mgr._flags
        assert mgr._flags["CT-A"].enabled is True
        assert mgr._flags["CT-A"].description == "desc A"

    def test_set_appends_audit(self):
        mgr = FeatureFlagManager()
        mgr.set("CT-B", False, "audit test")
        assert len(mgr._audit) == 1
        assert mgr._audit[0]["contract_id"] == "CT-B"
        assert mgr._audit[0]["enabled"] is False

    def test_set_overwrites_existing(self):
        mgr = FeatureFlagManager()
        mgr.set("CT-C", True)
        mgr.set("CT-C", False)
        assert mgr._flags["CT-C"].enabled is False
        assert len(mgr._audit) == 2


class TestIsEnabled:
    def test_unknown_flag_returns_true(self):
        mgr = FeatureFlagManager()
        assert mgr.is_enabled("UNKNOWN") is True

    def test_enabled_flag_returns_true(self):
        mgr = FeatureFlagManager()
        mgr.set("CT-ON", True)
        assert mgr.is_enabled("CT-ON") is True

    def test_disabled_flag_returns_false(self):
        mgr = FeatureFlagManager()
        mgr.set("CT-OFF", False)
        assert mgr.is_enabled("CT-OFF") is False


class TestGetAll:
    def test_empty_manager_returns_empty(self):
        mgr = FeatureFlagManager()
        assert mgr.get_all() == {}

    def test_returns_enabled_mapping(self):
        mgr = FeatureFlagManager()
        mgr.set("CT-X", True)
        mgr.set("CT-Y", False)
        result = mgr.get_all()
        assert result == {"CT-X": True, "CT-Y": False}


class TestBoundary:
    def test_set_empty_contract_id(self):
        mgr = FeatureFlagManager()
        flag = mgr.set("", True)
        assert flag.contract_id == ""
        assert mgr.is_enabled("") is True

    def test_set_empty_description(self):
        mgr = FeatureFlagManager()
        flag = mgr.set("CT-Z", True, "")
        assert flag.description == ""

    def test_multiple_sets_accumulate_audit(self):
        mgr = FeatureFlagManager()
        for i in range(5):
            mgr.set(f"CT-{i}", True)
        assert len(mgr._audit) == 5
