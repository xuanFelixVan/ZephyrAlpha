# [A_test] module_id: MOD-GOV_skill_registry_shared | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-575 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_skill_registry
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/skill-registry.py
===============================================
覆盖矩阵：
  PromptVariable：
    - 构造 × 2（必填 / 非必填带默认值）
    - name 为空拒绝 × 1
  PromptTemplate：
    - 构造 × 1
    - 默认 version/stability × 1
    - version 非 semver 拒绝 × 1
    - stability 非法值拒绝 × 1
    - extract_variables × 2
    - validate_variables × 3（一致 / 未声明 / 多余声明）
    - token_budget 负值拒绝 × 1
  SkillCategory：
    - 枚举值完整性 × 1
  SkillParameter：
    - 构造 × 1
    - 非必填带默认值 × 1
  SkillOutput：
    - 构造 × 1
  SkillDefinition：
    - 完整构造 × 1
    - version/stability 校验 × 2

Safety: MEDIUM（Pydantic 模型契约验证）
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
    def test_required_variable(self):
        var = PromptVariable(name="symbol", description="the symbol to search", required=True)
        assert var.name == "symbol"
        assert var.required is True
        assert var.default is None

    def test_optional_variable_with_default(self):
        var = PromptVariable(name="language", required=False, default="python")
        assert var.required is False
        assert var.default == "python"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            PromptVariable(name="")


class TestPromptTemplate:
    def test_construction(self):
        tmpl = PromptTemplate(
            template_id="find-refs-v1",
            name="Find References",
            template_str="Find all references to {symbol} in {language}",
            variables=[
                PromptVariable(name="symbol", required=True),
                PromptVariable(name="language", required=False, default="python"),
            ],
            token_budget=1000,
            tags=["search"],
        )
        assert tmpl.template_id == "find-refs-v1"
        assert tmpl.name == "Find References"
        assert tmpl.template_str == "Find all references to {symbol} in {language}"
        assert len(tmpl.variables) == 2

    def test_defaults(self):
        tmpl = PromptTemplate(
            template_id="min",
            name="Minimal",
            template_str="Hello {name}",
        )
        assert tmpl.version == "1.0.0"
        assert tmpl.stability == "evolving"
        assert tmpl.token_budget == 2000

    def test_invalid_version_rejected(self):
        with pytest.raises(ValidationError):
            PromptTemplate(
                template_id="x",
                name="x",
                template_str="x",
                version="1.0",
            )

    def test_invalid_stability_rejected(self):
        with pytest.raises(ValidationError):
            PromptTemplate(
                template_id="x",
                name="x",
                template_str="x",
                stability="deprecated",
            )

    def test_extract_variables(self):
        tmpl = PromptTemplate(
            template_id="t1",
            name="Test",
            template_str="Hello {name}, your {role} is {department}",
        )
        vars_found = tmpl.extract_variables()
        assert vars_found == {"name", "role", "department"}

    def test_extract_variables_none(self):
        tmpl = PromptTemplate(
            template_id="t2",
            name="Static",
            template_str="Hello, no variables here",
        )
        assert tmpl.extract_variables() == set()

    def test_validate_variables_consistent(self):
        tmpl = PromptTemplate(
            template_id="t1",
            name="Test",
            template_str="Hello {name}, your role is {role}",
            variables=[
                PromptVariable(name="name", required=True),
                PromptVariable(name="role", required=True),
            ],
        )
        assert tmpl.validate_variables() == []

    def test_validate_variables_missing_declared(self):
        tmpl = PromptTemplate(
            template_id="t1",
            name="Test",
            template_str="Hello {name}, your role is {role}",
            variables=[
                PromptVariable(name="name", required=True),
            ],
        )
        issues = tmpl.validate_variables()
        assert len(issues) == 1
        assert "Template vars not declared" in issues[0]

    def test_validate_variables_extra_declared(self):
        tmpl = PromptTemplate(
            template_id="t1",
            name="Test",
            template_str="Hello {name}",
            variables=[
                PromptVariable(name="name", required=True),
                PromptVariable(name="unused", required=True),
            ],
        )
        issues = tmpl.validate_variables()
        assert len(issues) == 1
        assert "Declared vars not in template" in issues[0]

    def test_negative_token_budget_rejected(self):
        with pytest.raises(ValidationError):
            PromptTemplate(
                template_id="x",
                name="x",
                template_str="x",
                token_budget=-1,
            )


class TestSkillCategory:
    def test_all_categories(self):
        values = {c.value for c in SkillCategory}
        assert "code" in values
        assert "writing" in values
        assert "research" in values
        assert "automation" in values
        assert "analysis" in values
        assert "design" in values
        assert len(values) == 6


class TestSkillParameter:
    def test_required_parameter(self):
        param = SkillParameter(
            name="file_path",
            param_type="string",
            description="Path to target file",
            required=True,
        )
        assert param.name == "file_path"
        assert param.param_type == "string"
        assert param.required is True

    def test_optional_parameter(self):
        param = SkillParameter(
            name="max_depth",
            param_type="integer",
            required=False,
            default=3,
        )
        assert param.required is False
        assert param.default == 3


class TestSkillOutput:
    def test_construction(self):
        output = SkillOutput(
            output_type="list",
            description="List of file paths",
            schema_example={"paths": ["a.py", "b.py"]},
        )
        assert output.output_type == "list"
        assert output.schema_example == {"paths": ["a.py", "b.py"]}


class TestSkillDefinition:
    def test_full_construction(self):
        skill = SkillDefinition(
            skill_id="find-code-refs",
            name="Find Code References",
            version="1.0.0",
            stability="stable",
            category=SkillCategory.CODE,
            description="Search codebase for references",
            prompt_template=PromptTemplate(
                template_id="find-refs-v1",
                name="Find References",
                template_str="Find all references to {symbol}",
                variables=[PromptVariable(name="symbol", required=True)],
            ),
            input_schema=[SkillParameter(name="symbol", param_type="string", required=True)],
            output_schema=SkillOutput(
                output_type="list",
                description="List of file paths",
            ),
            tags=["search", "code"],
        )
        assert skill.skill_id == "find-code-refs"
        assert skill.category == SkillCategory.CODE
        assert skill.stability == "stable"
        assert len(skill.tags) == 2
        assert skill.prompt_template.template_id == "find-refs-v1"

    def test_invalid_version_rejected(self):
        with pytest.raises(ValidationError):
            SkillDefinition(
                skill_id="x",
                name="x",
                version="bad-version",
                prompt_template=PromptTemplate(
                    template_id="t",
                    name="t",
                    template_str="t",
                ),
            )

    def test_invalid_stability_rejected(self):
        with pytest.raises(ValidationError):
            SkillDefinition(
                skill_id="x",
                name="x",
                stability="retired",
                prompt_template=PromptTemplate(
                    template_id="t",
                    name="t",
                    template_str="t",
                ),
            )

    def test_defaults(self):
        skill = SkillDefinition(
            skill_id="minimal",
            name="Minimal",
            prompt_template=PromptTemplate(
                template_id="m",
                name="m",
                template_str="m",
            ),
        )
        assert skill.version == "1.0.0"
        assert skill.stability == "evolving"
        assert skill.category == SkillCategory.CODE
        assert skill.input_schema == []
        assert skill.tags == []
