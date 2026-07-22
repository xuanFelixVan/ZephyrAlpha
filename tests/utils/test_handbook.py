# [A_test] module_id: MOD-GOV_handbook | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-391 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_handbook
# [INVARIANTS] Handbook.generate_onboarding_context返回非空str; get_directory_map返回非空dict
# [MODIFY-GUARD] 仅当handbook公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_handbook.py -q
# [TTL] task_bound


from zephyr.shared.maintenance.handbook import Handbook, HandbookSection


class TestHandbookInstantiation:
    def test_default_instantiation(self):
        hb = Handbook()
        assert hb is not None

    def test_instantiation_with_project_root(self, tmp_path):
        hb = Handbook(project_root=tmp_path)
        assert hb is not None

    def test_instantiation_with_none_root(self):
        hb = Handbook(project_root=None)
        assert hb is not None


class TestHandbookGenerateOnboardingContext:
    def test_returns_string(self):
        hb = Handbook()
        result = hb.generate_onboarding_context()
        assert isinstance(result, str)

    def test_non_empty_output(self):
        hb = Handbook()
        result = hb.generate_onboarding_context()
        assert len(result) > 0

    def test_contains_project_name(self):
        hb = Handbook()
        result = hb.generate_onboarding_context()
        assert "ZephyrAlpha" in result

    def test_contains_core_constraints(self):
        hb = Handbook()
        result = hb.generate_onboarding_context()
        assert "Core Constraints" in result

    def test_contains_key_directories(self):
        hb = Handbook()
        result = hb.generate_onboarding_context()
        assert "Key Directories" in result

    def test_contains_state_machine(self):
        hb = Handbook()
        result = hb.generate_onboarding_context()
        assert "State Machine" in result

    def test_contains_key_tools(self):
        hb = Handbook()
        result = hb.generate_onboarding_context()
        assert "Key Tools" in result

    def test_contains_rule_zero_reference(self):
        hb = Handbook()
        result = hb.generate_onboarding_context()
        assert "RULE-ZERO" in result


class TestHandbookGetTaskCardTemplate:
    def test_returns_string(self):
        hb = Handbook()
        result = hb.get_task_card_template()
        assert isinstance(result, str)

    def test_non_empty_output(self):
        hb = Handbook()
        result = hb.get_task_card_template()
        assert len(result) > 0

    def test_contains_table_format(self):
        hb = Handbook()
        result = hb.get_task_card_template()
        assert "|" in result
        assert "---" in result

    def test_contains_task_id_placeholder(self):
        hb = Handbook()
        result = hb.get_task_card_template()
        assert "TASK_NAME" in result


class TestHandbookGetDirectoryMap:
    def test_returns_dict(self):
        hb = Handbook()
        result = hb.get_directory_map()
        assert isinstance(result, dict)

    def test_non_empty_map(self):
        hb = Handbook()
        result = hb.get_directory_map()
        assert len(result) > 0

    def test_contains_core_directory(self):
        hb = Handbook()
        result = hb.get_directory_map()
        assert any("core" in k for k in result.keys())

    def test_contains_observability_directory(self):
        hb = Handbook()
        result = hb.get_directory_map()
        assert any("observability" in k for k in result.keys())

    def test_values_are_strings(self):
        hb = Handbook()
        result = hb.get_directory_map()
        for v in result.values():
            assert isinstance(v, str)
            assert len(v) > 0

    def test_contains_mcp_directory(self):
        hb = Handbook()
        result = hb.get_directory_map()
        assert any("mcp" in k for k in result.keys())


class TestHandbookSection:
    def test_section_construction(self):
        section = HandbookSection(
            section_id="SEC-001",
            title="Test Section",
            content="Test content",
        )
        assert section.section_id == "SEC-001"
        assert section.title == "Test Section"
        assert section.content == "Test content"
        assert section.source_file == ""

    def test_section_with_source_file(self):
        section = HandbookSection(
            section_id="SEC-002",
            title="Section",
            content="Content",
            source_file="docs/test.md",
        )
        assert section.source_file == "docs/test.md"

    def test_section_empty_content(self):
        section = HandbookSection(
            section_id="SEC-003",
            title="Empty",
            content="",
        )
        assert section.content == ""
