# [A_test] module_id: MOD-GOV_support_prompt_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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
        RenderedPrompt,
        TemplateNotFoundError,
        VariableError,
    )
except Exception as _exc:
    pytest.skip(f"cannot import prompt_registry: {_exc}", allow_module_level=True)


_SAMPLE_YAML = """
prompt_registry_version: "1.0.0"
templates:
  - template_id: test_tpl
    name: "Test Template"
    version: "1.0.0"
    stability: evolving
    token_budget: 2000
    variables:
      - name: task_id
        required: true
      - name: context
        required: false
        default: ""
    template_text: |
      Analyze task {task_id}:
      {context}
"""


class TestPromptRegistryLoadYaml:
    def test_load_yaml_text(self):
        reg = PromptRegistry()
        count = reg.load_yaml_text(_SAMPLE_YAML)
        assert count == 1

    def test_list_templates_after_load(self):
        reg = PromptRegistry()
        reg.load_yaml_text(_SAMPLE_YAML)
        templates = reg.list_templates()
        assert "test_tpl" in templates


class TestPromptRegistryGet:
    def test_get_existing_template(self):
        reg = PromptRegistry()
        reg.load_yaml_text(_SAMPLE_YAML)
        tpl = reg.get("test_tpl")
        assert tpl.template_id == "test_tpl"

    def test_get_nonexistent_template_raises(self):
        reg = PromptRegistry()
        with pytest.raises(TemplateNotFoundError):
            reg.get("nonexistent")

    def test_get_latest_version(self):
        reg = PromptRegistry()
        reg.load_yaml_text(_SAMPLE_YAML)
        version = reg.get_latest_version("test_tpl")
        assert version == "1.0.0"


class TestPromptRegistryRender:
    def test_render_template(self):
        reg = PromptRegistry()
        reg.load_yaml_text(_SAMPLE_YAML)
        result = reg.render("test_tpl", {"task_id": "T-001"})
        assert isinstance(result, RenderedPrompt)
        assert "T-001" in result.rendered_text

    def test_render_missing_required_variable_raises(self):
        reg = PromptRegistry()
        reg.load_yaml_text(_SAMPLE_YAML)
        with pytest.raises(VariableError):
            reg.render("test_tpl", {})


class TestPromptRegistryRegister:
    def test_register_template(self):
        reg = PromptRegistry()
        tpl = PromptTemplate(
            template_id="custom",
            name="Custom",
            version="1.0.0",
            template_text="Hello {name}",
            variables=[PromptVariable(name="name", required=True)],
            token_budget=1000,
        )
        reg.register(tpl)
        assert "custom" in reg.list_templates()

    def test_register_duplicate_raises(self):
        reg = PromptRegistry()
        tpl = PromptTemplate(
            template_id="dup",
            name="Dup",
            version="1.0.0",
            template_text="text",
            token_budget=1000,
        )
        reg.register(tpl)
        with pytest.raises(PromptRegistryError):
            reg.register(tpl)

    def test_register_duplicate_with_overwrite(self):
        reg = PromptRegistry()
        tpl = PromptTemplate(
            template_id="dup2",
            name="Dup2",
            version="1.0.0",
            template_text="text",
            token_budget=1000,
        )
        reg.register(tpl)
        reg.register(tpl, allow_overwrite=True)


class TestPromptTemplate:
    def test_get_placeholder_names(self):
        tpl = PromptTemplate(
            template_id="t1",
            name="T1",
            version="1.0.0",
            template_text="Hello {name}, your {item} is ready",
            token_budget=1000,
        )
        names = tpl.get_placeholder_names()
        assert "name" in names
        assert "item" in names

    def test_render_with_variables(self):
        tpl = PromptTemplate(
            template_id="t2",
            name="T2",
            version="1.0.0",
            template_text="Hello {name}",
            variables=[PromptVariable(name="name", required=True)],
            token_budget=1000,
        )
        result = tpl.render({"name": "World"})
        assert "World" in result.rendered_text

    def test_invalid_semver_raises(self):
        with pytest.raises(ValueError):
            PromptTemplate(
                template_id="t3",
                name="T3",
                version="not-semver",
                template_text="text",
                token_budget=1000,
            )
