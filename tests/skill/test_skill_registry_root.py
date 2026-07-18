# [A_test] module_id: SRC-TST-1646 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_registry
# [INVARIANTS] SkillDefinition requires skill_id+name+prompt_template; version must be semver; stability must be valid enum
# [MODIFY-GUARD] changes require review of skill-registry.py API
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValidationError on invalid version/stability; ValueError on semver check
# [TESTS] pytest tests/test_skill_registry.py -q
# [TTL] task_bound

import pytest
from pydantic import ValidationError

from zephyr.autonomy_core.skills.skill_registry import (
    PromptTemplate,
    PromptVariable,
    SkillCategory,
    SkillDefinition,
    SkillOutput,
    SkillParameter,
)


def _make_prompt_template(**overrides):
    defaults = {
        "template_id": "tpl-001",
        "name": "Test Template",
        "template_str": "Find all references to {symbol}",
        "variables": [PromptVariable(name="symbol", required=True)],
    }
    defaults.update(overrides)
    return PromptTemplate(**defaults)


def _make_skill_definition(**overrides):
    defaults = {
        "skill_id": "find-code-refs",
        "name": "Find Code References",
        "category": SkillCategory.CODE,
        "prompt_template": _make_prompt_template(),
    }
    defaults.update(overrides)
    return SkillDefinition(**defaults)


class TestPromptVariable:
    def test_valid_prompt_variable(self):
        pv = PromptVariable(name="symbol", description="The symbol to find", required=True)
        assert pv.name == "symbol"
        assert pv.required is True

    def test_default_values(self):
        pv = PromptVariable(name="x")
        assert pv.description == ""
        assert pv.required is True
        assert pv.default is None

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            PromptVariable(name="")

    def test_optional_variable_with_default(self):
        pv = PromptVariable(name="limit", required=False, default="10")
        assert pv.required is False
        assert pv.default == "10"


class TestPromptTemplate:
    def test_valid_template(self):
        tpl = _make_prompt_template()
        assert tpl.template_id == "tpl-001"
        assert tpl.version == "1.0.0"
        assert tpl.stability == "evolving"

    def test_extract_variables(self):
        tpl = _make_prompt_template(template_str="Hello {name}, welcome to {place}")
        extracted = tpl.extract_variables()
        assert extracted == {"name", "place"}

    def test_validate_variables_consistent(self):
        tpl = _make_prompt_template(
            template_str="Find {symbol} in {scope}",
            variables=[
                PromptVariable(name="symbol", required=True),
                PromptVariable(name="scope", required=False, default="project"),
            ],
        )
        issues = tpl.validate_variables()
        assert issues == []

    def test_validate_variables_missing_declared(self):
        tpl = _make_prompt_template(
            template_str="Find {symbol} in {scope}",
            variables=[PromptVariable(name="symbol", required=True)],
        )
        issues = tpl.validate_variables()
        assert len(issues) >= 1
        assert any("not declared" in i for i in issues)

    def test_validate_variables_unused_declared(self):
        tpl = _make_prompt_template(
            template_str="Find {symbol}",
            variables=[
                PromptVariable(name="symbol", required=True),
                PromptVariable(name="unused_var", required=False),
            ],
        )
        issues = tpl.validate_variables()
        assert len(issues) >= 1
        assert any("not in template" in i for i in issues)

    def test_invalid_version_raises(self):
        with pytest.raises(ValidationError):
            _make_prompt_template(version="1.0")

    def test_invalid_stability_raises(self):
        with pytest.raises(ValidationError):
            _make_prompt_template(stability="invalid")

    def test_valid_stability_values(self):
        for stability in ("volatile", "evolving", "stable", "frozen"):
            tpl = _make_prompt_template(stability=stability)
            assert tpl.stability == stability

    def test_empty_template_id_raises(self):
        with pytest.raises(ValidationError):
            _make_prompt_template(template_id="")

    def test_empty_template_str_raises(self):
        with pytest.raises(ValidationError):
            _make_prompt_template(template_str="")

    def test_token_budget_default(self):
        tpl = _make_prompt_template()
        assert tpl.token_budget == 2000

    def test_negative_token_budget_raises(self):
        with pytest.raises(ValidationError):
            _make_prompt_template(token_budget=-1)


class TestSkillCategory:
    def test_all_categories(self):
        expected = {"code", "writing", "research", "automation", "analysis", "design"}
        actual = {c.value for c in SkillCategory}
        assert actual == expected

    def test_category_from_string(self):
        assert SkillCategory("code") == SkillCategory.CODE


class TestSkillParameter:
    def test_valid_parameter(self):
        sp = SkillParameter(name="query", param_type="string", required=True)
        assert sp.name == "query"
        assert sp.param_type == "string"
        assert sp.required is True

    def test_default_values(self):
        sp = SkillParameter(name="limit")
        assert sp.param_type == "string"
        assert sp.required is True
        assert sp.default is None

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            SkillParameter(name="")


class TestSkillOutput:
    def test_valid_output(self):
        so = SkillOutput(output_type="list", description="List of results")
        assert so.output_type == "list"
        assert so.description == "List of results"

    def test_default_values(self):
        so = SkillOutput()
        assert so.output_type == "dict"
        assert so.description == ""
        assert so.schema_example == {}


class TestSkillDefinition:
    def test_valid_skill_definition(self):
        sd = _make_skill_definition()
        assert sd.skill_id == "find-code-refs"
        assert sd.name == "Find Code References"
        assert sd.category == SkillCategory.CODE
        assert sd.version == "1.0.0"
        assert sd.stability == "evolving"

    def test_invalid_version_raises(self):
        with pytest.raises(ValidationError):
            _make_skill_definition(version="2.0")

    def test_invalid_stability_raises(self):
        with pytest.raises(ValidationError):
            _make_skill_definition(stability="unstable")

    def test_empty_skill_id_raises(self):
        with pytest.raises(ValidationError):
            _make_skill_definition(skill_id="")

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            _make_skill_definition(name="")

    def test_with_input_schema(self):
        sd = _make_skill_definition(
            input_schema=[
                SkillParameter(name="symbol", param_type="string", required=True),
                SkillParameter(name="scope", param_type="string", required=False, default="project"),
            ],
        )
        assert len(sd.input_schema) == 2
        assert sd.input_schema[0].name == "symbol"

    def test_with_output_schema(self):
        sd = _make_skill_definition(
            output_schema=SkillOutput(output_type="list", description="References"),
        )
        assert sd.output_schema is not None
        assert sd.output_schema.output_type == "list"

    def test_with_metadata(self):
        sd = _make_skill_definition(metadata={"author": "test", "team": "infra"})
        assert sd.metadata["author"] == "test"

    def test_with_tags(self):
        sd = _make_skill_definition(tags=["search", "code"])
        assert "search" in sd.tags

    def test_default_category_is_code(self):
        sd = _make_skill_definition(category=SkillCategory.CODE)
        assert sd.category == SkillCategory.CODE

    def test_all_stability_values_accepted(self):
        for stability in ("volatile", "evolving", "stable", "frozen"):
            sd = _make_skill_definition(stability=stability)
            assert sd.stability == stability

    def test_prompt_template_is_embedded(self):
        sd = _make_skill_definition()
        assert isinstance(sd.prompt_template, PromptTemplate)
        assert sd.prompt_template.template_id == "tpl-001"

    def test_created_at_auto_set(self):
        sd = _make_skill_definition()
        assert sd.created_at is not None
