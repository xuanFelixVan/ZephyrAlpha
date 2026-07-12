# [A_test] module_id: SRC-TST-0572 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_config
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_config_root.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_code_quality.code_dedup.config import (
    EXIT_CODES,
    PATH_THRESHOLDS,
    POLICY_TREE,
    PROJECT_SCALE_TIERS,
    get_tier_for_project,
    get_tier_name,
    load_policy_rules,
    load_policy_tree,
)


class TestProjectScaleTiers:
    def test_four_tiers_exist(self):
        assert "Tier1_small" in PROJECT_SCALE_TIERS
        assert "Tier2_medium" in PROJECT_SCALE_TIERS
        assert "Tier3_large" in PROJECT_SCALE_TIERS
        assert "Tier4_xlarge" in PROJECT_SCALE_TIERS

    def test_tier1_small(self):
        t = PROJECT_SCALE_TIERS["Tier1_small"]
        assert t["max_lines"] == 5000
        assert t["ast_similarity_threshold"] == 0.65

    def test_tier2_medium(self):
        t = PROJECT_SCALE_TIERS["Tier2_medium"]
        assert t["min_lines"] == 5000
        assert t["max_lines"] == 15000

    def test_tier3_large(self):
        t = PROJECT_SCALE_TIERS["Tier3_large"]
        assert t["min_lines"] == 15000
        assert t["max_lines"] == 50000

    def test_tier4_xlarge(self):
        t = PROJECT_SCALE_TIERS["Tier4_xlarge"]
        assert t["min_lines"] == 50000


class TestGetTierForProject:
    def test_tier1(self):
        result = get_tier_for_project(1000)
        assert result["name"] == "小型项目"

    def test_tier2(self):
        result = get_tier_for_project(8000)
        assert result["name"] == "中型项目"

    def test_tier3(self):
        result = get_tier_for_project(30000)
        assert result["name"] == "大型项目"

    def test_tier4(self):
        result = get_tier_for_project(100000)
        assert result["name"] == "超大型项目"

    def test_boundary_tier1_tier2(self):
        result = get_tier_for_project(4999)
        assert result["name"] == "小型项目"
        result = get_tier_for_project(5000)
        assert result["name"] == "中型项目"

    def test_zero_lines(self):
        result = get_tier_for_project(0)
        assert result["name"] == "小型项目"


class TestGetTierName:
    def test_returns_name_string(self):
        assert get_tier_name(1000) == "小型项目"
        assert get_tier_name(8000) == "中型项目"


class TestPolicyTree:
    def test_version_exists(self):
        assert "version" in POLICY_TREE

    def test_cloning_detection_exists(self):
        assert "cloning_detection" in POLICY_TREE
        assert POLICY_TREE["cloning_detection"]["type1_exact_match"] is True

    def test_thresholds_exist(self):
        assert "thresholds" in POLICY_TREE
        assert "high_confidence" in POLICY_TREE["thresholds"]

    def test_auto_fix_exists(self):
        assert "auto_fix" in POLICY_TREE
        assert POLICY_TREE["auto_fix"]["enabled"] is True


class TestLoadPolicyTree:
    def test_returns_dict(self):
        result = load_policy_tree()
        assert isinstance(result, dict)
        assert "version" in result

    def test_fallback_contains_core_keys(self):
        result = load_policy_tree()
        assert "version" in result
        assert "thresholds" in result
        assert "auto_fix" in result
        assert "cloning_detection" in result


class TestLoadPolicyRules:
    def test_returns_list(self):
        result = load_policy_rules()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_rules_have_required_fields(self):
        result = load_policy_rules()
        for rule in result:
            assert "id" in rule
            assert "name" in rule
            assert "action" in rule


class TestExitCodes:
    def test_all_codes_defined(self):
        assert 0 in EXIT_CODES
        assert 1 in EXIT_CODES
        assert 2 in EXIT_CODES
        assert 3 in EXIT_CODES
        assert 4 in EXIT_CODES


class TestPathThresholds:
    def test_all_paths_defined(self):
        assert "shared" in PATH_THRESHOLDS
        assert "core" in PATH_THRESHOLDS
        assert "default" in PATH_THRESHOLDS
        assert "tests" in PATH_THRESHOLDS
        assert "scripts" in PATH_THRESHOLDS

    def test_thresholds_are_floats(self):
        for key, val in PATH_THRESHOLDS.items():
            assert isinstance(val, float)
            assert 0.0 <= val <= 1.0
