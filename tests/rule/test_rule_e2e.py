# [A_test] module_id: DM-100053 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-019 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §rule_engine
# [MODULE] tests.test_rule_e2e
# [INVARIANTS] RuleLoader API 必须正确加载 YAML 规则; 缓存必须命中; 缺失操作返回空列表
# [MODIFY-GUARD] rule_engine.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertions on RuleLoader API returns
# [TESTS] tests/test_rule_e2e.py
# [TTL] task_bound

import pytest

from zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_engine import RuleLoader


@pytest.fixture
def loader():
    return RuleLoader()


class TestOperationTrigger:
    def test_file_write_returns_trae001(self, loader):
        rules = loader.load_for_operation("file_write")
        assert isinstance(rules, list)
        rule_ids = [r.get("rule_id") for r in rules]
        assert "TRAE-001" in rule_ids, f"TRAE-001 not found in {rule_ids}"


class TestSkillTrigger:
    def test_skill_ded_returns_rules(self, loader):
        rules = loader.load_for_skill("SKILL-DOM-DED-001")
        assert isinstance(rules, list)
        assert len(rules) > 0, "SKILL-DOM-DED-001 should return at least one rule"


class TestGateTrigger:
    def test_gate_g0_returns_rules(self, loader):
        rules = loader.load_for_gate("G0")
        assert isinstance(rules, list)
        assert len(rules) > 0, "G0 gate should return at least one rule"


class TestContentIntegrity:
    def test_trae001_title_and_sections(self, loader):
        rule = loader.get_rule_by_id("TRAE-001")
        assert rule is not None, "TRAE-001 should be loadable"
        assert rule.get("title") == "文件操作安全协议"
        sections = rule.get("sections", {})
        assert "file_lock_protocol" in sections, "Missing file_lock_protocol section"
        assert "atomic_write" in sections, "Missing atomic_write section"
        assert "delete_confirmation" in sections, "Missing delete_confirmation section"
        assert "create_and_register" in sections, "Missing create_and_register section"
        assert "zero_residue" in sections, "Missing zero_residue section"


class TestCache:
    def test_second_load_returns_cached(self, loader):
        first = loader.load_for_operation("file_write")
        second = loader.load_for_operation("file_write")
        assert first == second, "Second load should return equal results (cached)"


class TestMissingOperation:
    def test_nonexistent_op_returns_empty(self, loader):
        rules = loader.load_for_operation("nonexistent_op")
        assert isinstance(rules, list)
        assert len(rules) == 0, "Nonexistent operation should return empty list"


class TestGetCriticalRules:
    def test_returns_l0_critical_rules(self, loader):
        critical = loader.get_critical_rules()
        assert isinstance(critical, list)
        assert len(critical) >= 10, f"Expected >= 10 critical rules, got {len(critical)}"
        for rule in critical:
            assert rule.get("metadata", {}).get("impact_level") == "H"


class TestGetRuleById:
    def test_trae001_returns_dict(self, loader):
        rule = loader.get_rule_by_id("TRAE-001")
        assert rule is not None
        assert rule.get("rule_id") == "TRAE-001"


class TestListAllRules:
    def test_returns_53_rules(self, loader):
        summaries = loader.list_all_rules()
        assert isinstance(summaries, list)
        assert len(summaries) == 53, f"Expected 53 rules, got {len(summaries)}"
