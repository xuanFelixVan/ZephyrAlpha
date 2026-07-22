# [A_test] module_id: MOD-GOV_skill_registry_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-684 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_skill_registry
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for skill-registry.py
"""

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


class TestPromptVariable:
    def test_create(self):
        v = PromptVariable(name="task_id", required=True)
        assert v.name == "task_id"
        assert v.required is True
        assert v.default is None

    def test_optional_with_default(self):
        v = PromptVariable(name="context", required=False, default="none")
        assert v.default == "none"

    def test_name_required(self):
        with pytest.raises(ValidationError):
            PromptVariable(name="")


class TestPromptTemplate:
    def test_create_basic(self):
        t = PromptTemplate(
            template_id="test-v1",
            name="Test Template",
            template_str="Hello {name}!",
            variables=[PromptVariable(name="name", required=True)],
        )
        assert t.template_id == "test-v1"
        assert t.version == "1.0.0"
        assert t.stability == "evolving"
        assert t.token_budget == 2000

    def test_invalid_version(self):
        with pytest.raises(ValidationError):
            PromptTemplate(
                template_id="bad",
                name="Bad",
                template_str="test",
                version="not-semver",
            )

    def test_extract_variables(self):
        t = PromptTemplate(
            template_id="v1",
            name="Vars",
            template_str="Hello {name}, your task is {task_id}",
        )
        vars_set = t.extract_variables()
        assert "name" in vars_set
        assert "task_id" in vars_set

    def test_validate_variables_consistent(self):
        t = PromptTemplate(
            template_id="v1",
            name="Consistent",
            template_str="Hello {name}",
            variables=[PromptVariable(name="name", required=True)],
        )
        issues = t.validate_variables()
        assert len(issues) == 0

    def test_validate_variables_missing_declared(self):
        t = PromptTemplate(
            template_id="v1",
            name="Missing",
            template_str="Hello {name}, {extra}",
            variables=[PromptVariable(name="name", required=True)],
        )
        issues = t.validate_variables()
        assert len(issues) >= 1

    def test_validate_variables_unused(self):
        t = PromptTemplate(
            template_id="v1",
            name="Unused",
            template_str="Hello {name}",
            variables=[
                PromptVariable(name="name", required=True),
                PromptVariable(name="unused", required=False),
            ],
        )
        issues = t.validate_variables()
        assert len(issues) >= 1


class TestSkillDefinition:
    def test_create(self):
        skill = SkillDefinition(
            skill_id="find-refs",
            name="Find References",
            description="Find code references",
            category=SkillCategory.CODE,
            prompt_template=PromptTemplate(
                template_id="find-v1",
                name="Find",
                template_str="Find {symbol}",
            ),
            input_schema=[
                SkillParameter(name="symbol", param_type="string", required=True),
            ],
            output_schema=SkillOutput(
                output_type="list",
                description="List of references",
            ),
        )
        assert skill.skill_id == "find-refs"
        assert skill.category == SkillCategory.CODE
        assert len(skill.input_schema) == 1
        assert skill.output_schema is not None

    def test_invalid_version(self):
        with pytest.raises(ValidationError):
            SkillDefinition(
                skill_id="bad",
                name="Bad Version",
                version="not-semver",
                prompt_template=PromptTemplate(
                    template_id="t1",
                    name="T",
                    template_str="test",
                ),
            )

    def test_minimal(self):
        skill = SkillDefinition(
            skill_id="minimal",
            name="Minimal Skill",
            prompt_template=PromptTemplate(
                template_id="t1",
                name="T",
                template_str="minimal task",
            ),
        )
        assert skill.skill_id == "minimal"
        assert skill.input_schema == []
        assert skill.output_schema is None


class TestSkillCategories:
    def test_all_categories(self):
        cats = list(SkillCategory)
        assert SkillCategory.CODE in cats
        assert SkillCategory.WRITING in cats
        assert SkillCategory.RESEARCH in cats
        assert len(cats) >= 5
