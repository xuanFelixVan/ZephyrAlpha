# [A_test] module_id: MOD-GOV_all_skill_modules | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_all_skill_modules
# [INVARIANTS] MODULE_LIST is a non-empty list of strings; all_modules returns same list; count matches len
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_all_skill_modules.py
# [TTL] task_bound

from zephyr.autonomy_core.all_skill_modules import AllSkillModules


class TestAllSkillModulesInstantiation:
    def test_class_has_module_list(self):
        assert hasattr(AllSkillModules, "MODULE_LIST")

    def test_module_list_is_list(self):
        assert isinstance(AllSkillModules.MODULE_LIST, list)

    def test_module_list_not_empty(self):
        assert len(AllSkillModules.MODULE_LIST) > 0


class TestAllModules:
    def test_all_modules_returns_list(self):
        result = AllSkillModules.all_modules()
        assert isinstance(result, list)

    def test_all_modules_returns_module_list(self):
        result = AllSkillModules.all_modules()
        assert result == AllSkillModules.MODULE_LIST

    def test_all_modules_items_are_strings(self):
        for item in AllSkillModules.all_modules():
            assert isinstance(item, str), f"Expected str, got {type(item)}: {item}"

    def test_all_modules_contains_known_entries(self):
        result = AllSkillModules.all_modules()
        assert "skill_model" in result
        assert "skill_loader" in result
        assert "skill_router" in result

    def test_all_modules_no_duplicates(self):
        result = AllSkillModules.all_modules()
        assert len(result) == len(set(result)), "MODULE_LIST contains duplicates"


class TestCount:
    def test_count_returns_int(self):
        result = AllSkillModules.count()
        assert isinstance(result, int)

    def test_count_matches_module_list_length(self):
        assert AllSkillModules.count() == len(AllSkillModules.MODULE_LIST)

    def test_count_greater_than_zero(self):
        assert AllSkillModules.count() > 0

    def test_count_consistent_with_all_modules(self):
        assert AllSkillModules.count() == len(AllSkillModules.all_modules())
