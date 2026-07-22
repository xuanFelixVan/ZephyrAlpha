# [A_test] module_id: MOD-GOV_prompt_registry_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.prompt_registry
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.prompt_registry import (
        PromptRegistry,
        PromptRegistryError,
        PromptTemplate,
        PromptVariable,
        PromptVersion,
        RenderedPrompt,
        TemplateNotFoundError,
        TokenBudgetExceededError,
        VariableError,
    )
except Exception as exc:
    pytest.skip(f"Cannot import prompt_registry: {exc}", allow_module_level=True)


def _make_template(
    template_id: str = "test_tpl",
    version: str = "1.0.0",
    template_text: str = "Hello {name}!",
    token_budget: int = 4000,
    variables: list[PromptVariable] | None = None,
    stability: str = "stable",
    system_prefix: str = "",
) -> PromptTemplate:
    if variables is None:
        variables = [PromptVariable(name="name", required=True)]
    return PromptTemplate(
        template_id=template_id,
        name="Test Template",
        version=version,
        stability=stability,
        variables=variables,
        token_budget=token_budget,
        template_text=template_text,
        system_prefix=system_prefix,
    )


class TestPromptVariable:
    def test_defaults(self):
        v = PromptVariable(name="x")
        assert v.name == "x"
        assert v.required is True
        assert v.default is None
        assert v.var_type == "string"

    def test_optional_variable(self):
        v = PromptVariable(name="y", required=False, default="fallback")
        assert v.required is False
        assert v.default == "fallback"


class TestPromptVersion:
    def test_valid_semver(self):
        pv = PromptVersion(version="1.2.3", stability="stable")
        assert pv.version == "1.2.3"

    def test_invalid_semver(self):
        with pytest.raises(Exception):
            PromptVersion(version="not-semver", stability="stable")

    def test_invalid_stability(self):
        with pytest.raises(Exception):
            PromptVersion(version="1.0.0", stability="invalid")


class TestPromptTemplate:
    def test_get_placeholder_names(self):
        tpl = _make_template(template_text="Hello {name}, welcome to {place}!")
        placeholders = tpl.get_placeholder_names()
        assert placeholders == {"name", "place"}

    def test_render_basic(self):
        tpl = _make_template()
        result = tpl.render({"name": "World"})
        assert isinstance(result, RenderedPrompt)
        assert "World" in result.rendered_text
        assert result.token_count > 0

    def test_render_missing_required_variable(self):
        tpl = _make_template()
        with pytest.raises(VariableError):
            tpl.render({})

    def test_render_with_default_variable(self):
        tpl = _make_template(
            template_text="Hello {name} from {city}!",
            variables=[
                PromptVariable(name="name", required=True),
                PromptVariable(name="city", required=False, default="Earth"),
            ],
        )
        result = tpl.render({"name": "Alice"})
        assert "Earth" in result.rendered_text

    def test_render_token_budget_exceeded(self):
        tpl = _make_template(token_budget=1)
        with pytest.raises(TokenBudgetExceededError):
            tpl.render({"name": "World"})

    def test_render_with_system_prefix(self):
        tpl = _make_template(
            template_text="Hello {name}!",
            system_prefix="SYSTEM:",
        )
        result = tpl.render({"name": "World"})
        assert result.rendered_text.startswith("SYSTEM:")


class TestPromptRegistry:
    def test_register_and_get(self):
        reg = PromptRegistry()
        tpl = _make_template()
        reg.register(tpl)
        fetched = reg.get("test_tpl")
        assert fetched.template_id == "test_tpl"

    def test_get_nonexistent(self):
        reg = PromptRegistry()
        with pytest.raises(TemplateNotFoundError):
            reg.get("nonexistent")

    def test_register_duplicate_without_overwrite(self):
        reg = PromptRegistry()
        tpl = _make_template()
        reg.register(tpl)
        with pytest.raises(PromptRegistryError):
            reg.register(tpl)

    def test_register_duplicate_with_overwrite(self):
        reg = PromptRegistry()
        tpl1 = _make_template(template_text="Version A {name}")
        reg.register(tpl1)
        tpl2 = _make_template(template_text="Version B {name}")
        reg.register(tpl2, allow_overwrite=True)
        fetched = reg.get("test_tpl")
        assert "Version B" in fetched.template_text

    def test_list_templates(self):
        reg = PromptRegistry()
        reg.register(_make_template(template_id="tpl_a"))
        reg.register(_make_template(template_id="tpl_b"))
        ids = reg.list_templates()
        assert set(ids) == {"tpl_a", "tpl_b"}

    def test_list_versions(self):
        reg = PromptRegistry()
        reg.register(_make_template(version="1.0.0"))
        reg.register(_make_template(version="2.0.0"))
        versions = reg.list_versions("test_tpl")
        assert versions == ["1.0.0", "2.0.0"]

    def test_get_latest_version(self):
        reg = PromptRegistry()
        reg.register(_make_template(version="1.0.0"))
        reg.register(_make_template(version="2.0.0"))
        latest = reg.get_latest_version("test_tpl")
        assert latest == "2.0.0"

    def test_get_specific_version(self):
        reg = PromptRegistry()
        reg.register(_make_template(version="1.0.0"))
        reg.register(_make_template(version="2.0.0"))
        fetched = reg.get("test_tpl", version="1.0.0")
        assert fetched.version == "1.0.0"

    def test_render(self):
        reg = PromptRegistry()
        reg.register(_make_template())
        result = reg.render("test_tpl", {"name": "World"})
        assert "World" in result.rendered_text

    def test_render_nonexistent(self):
        reg = PromptRegistry()
        with pytest.raises(TemplateNotFoundError):
            reg.render("nonexistent", {"name": "World"})

    def test_load_yaml_text(self):
        yaml_text = """
prompt_registry_version: "1.0.0"
templates:
  - template_id: yaml_tpl
    name: "YAML Template"
    version: "1.0.0"
    stability: stable
    token_budget: 2000
    variables:
      - name: task_id
        required: true
    template_text: "Task {task_id} analysis"
"""
        reg = PromptRegistry()
        count = reg.load_yaml_text(yaml_text)
        assert count == 1
        fetched = reg.get("yaml_tpl")
        assert fetched.name == "YAML Template"

    def test_load_yaml_text_multiple(self):
        yaml_text = """
prompt_registry_version: "1.0.0"
templates:
  - template_id: tpl1
    name: "Template 1"
    version: "1.0.0"
    stability: evolving
    token_budget: 1000
    template_text: "One {x}"
    variables:
      - name: x
        required: true
  - template_id: tpl2
    name: "Template 2"
    version: "1.0.0"
    stability: evolving
    token_budget: 2000
    template_text: "Two {y}"
    variables:
      - name: y
        required: true
"""
        reg = PromptRegistry()
        count = reg.load_yaml_text(yaml_text)
        assert count == 2
        assert len(reg.list_templates()) == 2

    def test_get_latest_version_nonexistent(self):
        reg = PromptRegistry()
        with pytest.raises(TemplateNotFoundError):
            reg.get_latest_version("nonexistent")
