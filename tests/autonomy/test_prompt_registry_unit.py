# [A_test] module_id: MOD-GOV_prompt_registry_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-672 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_prompt_registry
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for prompt_registry.py (T-2-28, B12)
=================================================
验收标准：≥ 10 条单元测试，覆盖：
  - YAML 加载（文件 / 字符串）
  - 版本管理（注册、latest 追踪、版本排序）
  - 变量插值（正常、必填缺失、未知占位符、默认值）
  - Token 预算约束
  - render_with_context 集成接口（Mock）
  - 异常层次
"""


import textwrap
from typing import Any
from unittest.mock import MagicMock

import pytest

from zephyr.autonomy_core.prompt_registry import (
    PromptRegistry,
    PromptTemplate,
    PromptVariable,
    PromptVersion,
    RenderedPrompt,
    TemplateNotFoundError,
    TokenBudgetExceededError,
    VariableError,
    _compare_semver,
    _semver_tuple,
)
from zephyr.infrastructure.capacity_assurance.token_budget import estimate_tokens

# ---------------------------------------------------------------------------
# 工具函数测试
# ---------------------------------------------------------------------------

MINIMAL_YAML = textwrap.dedent("""\
    prompt_registry_version: "1.0.0"
    templates:
      - template_id: greet
        name: "Greeting"
        version: "1.0.0"
        stability: stable
        token_budget: 1000
        variables:
          - name: user
            required: true
        template_text: "Hello, {user}!"
""")

MULTI_VERSION_YAML = textwrap.dedent("""\
    prompt_registry_version: "1.0.0"
    templates:
      - template_id: analyze
        name: "Analyze"
        version: "1.0.0"
        stability: evolving
        token_budget: 2000
        variables:
          - name: task_id
            required: true
        template_text: "v1: analyze {task_id}"
      - template_id: analyze
        name: "Analyze"
        version: "2.0.0"
        stability: stable
        token_budget: 2000
        variables:
          - name: task_id
            required: true
          - name: context
            required: false
            default: ""
        template_text: "v2: analyze {task_id} context={context}"
""")


class TestEstimateTokens:
    def test_non_empty_text(self) -> None:
        assert estimate_tokens("hello world") > 0

    def test_empty_text_returns_zero(self) -> None:
        assert estimate_tokens("") == 0

    def test_four_chars_equals_one_token(self) -> None:
        assert estimate_tokens("abcd") == 1

    def test_long_text_scales_linearly(self) -> None:
        assert estimate_tokens("a" * 400) == 100


class TestSemver:
    def test_tuple_parsing(self) -> None:
        assert _semver_tuple("2.3.1") == (2, 3, 1)

    def test_compare_lower(self) -> None:
        assert _compare_semver("1.0.0", "2.0.0") == -1

    def test_compare_equal(self) -> None:
        assert _compare_semver("1.0.0", "1.0.0") == 0

    def test_compare_higher(self) -> None:
        assert _compare_semver("2.1.0", "2.0.9") == 1


# ---------------------------------------------------------------------------
# PromptVariable 测试
# ---------------------------------------------------------------------------


class TestPromptVariable:
    def test_required_default(self) -> None:
        v = PromptVariable(name="x")
        assert v.required is True
        assert v.default is None

    def test_optional_with_default(self) -> None:
        v = PromptVariable(name="ctx", required=False, default="none")
        assert v.default == "none"


# ---------------------------------------------------------------------------
# PromptVersion 测试
# ---------------------------------------------------------------------------


class TestPromptVersion:
    def test_valid_version(self) -> None:
        pv = PromptVersion(version="1.2.3", stability="stable")
        assert pv.version == "1.2.3"

    def test_invalid_semver_raises(self) -> None:
        with pytest.raises(Exception):
            PromptVersion(version="v1.2", stability="stable")

    def test_invalid_stability_raises(self) -> None:
        with pytest.raises(Exception):
            PromptVersion(version="1.0.0", stability="unknown_level")


# ---------------------------------------------------------------------------
# PromptTemplate 测试
# ---------------------------------------------------------------------------


class TestPromptTemplate:
    def _make_template(
        self,
        template_text: str = "Hello {name}!",
        token_budget: int = 1000,
        variables: list[PromptVariable] | None = None,
    ) -> PromptTemplate:
        return PromptTemplate(
            template_id="test_tpl",
            name="Test",
            version="1.0.0",
            template_text=template_text,
            token_budget=token_budget,
            variables=variables or [PromptVariable(name="name", required=True)],
        )

    def test_render_simple(self) -> None:
        tpl = self._make_template()
        result = tpl.render({"name": "Alice"})
        assert isinstance(result, RenderedPrompt)
        assert "Alice" in result.rendered_text

    def test_render_missing_required_raises(self) -> None:
        tpl = self._make_template()
        with pytest.raises(VariableError, match="name"):
            tpl.render({})

    def test_render_with_default_variable(self) -> None:
        tpl = self._make_template(
            template_text="hello {name} ctx={ctx}",
            variables=[
                PromptVariable(name="name", required=True),
                PromptVariable(name="ctx", required=False, default="none"),
            ],
        )
        result = tpl.render({"name": "Bob"})
        assert "ctx=none" in result.rendered_text

    def test_render_token_budget_exceeded(self) -> None:
        tpl = self._make_template(token_budget=1)
        with pytest.raises(TokenBudgetExceededError):
            tpl.render({"name": "Alice " * 10})

    def test_render_with_system_prefix(self) -> None:
        tpl = PromptTemplate(
            template_id="sys_tpl",
            name="Sys",
            version="1.0.0",
            template_text="body {x}",
            system_prefix="You are a helpful assistant.",
            variables=[PromptVariable(name="x", required=True)],
        )
        result = tpl.render({"x": "test"})
        assert "You are a helpful assistant." in result.rendered_text

    def test_get_placeholder_names(self) -> None:
        tpl = self._make_template(template_text="Hello {name}, task={task_id}!")
        placeholders = tpl.get_placeholder_names()
        assert placeholders == {"name", "task_id"}

    def test_budget_remaining_calculated(self) -> None:
        tpl = self._make_template(token_budget=500)
        result = tpl.render({"name": "X"})
        assert result.budget_remaining == 500 - result.token_count

    def test_extra_variables_passthrough(self) -> None:
        tpl = self._make_template(template_text="a={a} b={b}")
        tpl2 = PromptTemplate(
            template_id="tpl2",
            name="T2",
            version="1.0.0",
            template_text="a={a} b={b}",
            variables=[PromptVariable(name="a", required=True)],
        )
        result = tpl2.render({"a": "1", "b": "2"})
        assert "b=2" in result.rendered_text


# ---------------------------------------------------------------------------
# PromptRegistry 测试
# ---------------------------------------------------------------------------


class TestPromptRegistryLoadYaml:
    def test_load_yaml_text_basic(self) -> None:
        reg = PromptRegistry()
        count = reg.load_yaml_text(MINIMAL_YAML)
        assert count == 1
        assert "greet" in reg.list_templates()

    def test_load_yaml_file(self, tmp_path: Any) -> None:
        yaml_file = tmp_path / "prompts.yaml"
        yaml_file.write_text(MINIMAL_YAML, encoding="utf-8")
        reg = PromptRegistry()
        count = reg.load_yaml(yaml_file)
        assert count == 1

    def test_load_multi_version(self) -> None:
        reg = PromptRegistry()
        count = reg.load_yaml_text(MULTI_VERSION_YAML)
        assert count == 2
        assert reg.get_latest_version("analyze") == "2.0.0"

    def test_list_versions_sorted(self) -> None:
        reg = PromptRegistry()
        reg.load_yaml_text(MULTI_VERSION_YAML)
        versions = reg.list_versions("analyze")
        assert versions == ["1.0.0", "2.0.0"]


class TestPromptRegistryRegister:
    def _make_tpl(self, tid: str, version: str) -> PromptTemplate:
        return PromptTemplate(
            template_id=tid,
            name="T",
            version=version,
            template_text="hi {x}",
            variables=[PromptVariable(name="x", required=True)],
        )

    def test_register_new_template(self) -> None:
        reg = PromptRegistry()
        reg.register(self._make_tpl("foo", "1.0.0"))
        assert "foo" in reg.list_templates()

    def test_register_duplicate_raises(self) -> None:
        reg = PromptRegistry()
        reg.register(self._make_tpl("foo", "1.0.0"))
        with pytest.raises(Exception):
            reg.register(self._make_tpl("foo", "1.0.0"))

    def test_register_duplicate_overwrite(self) -> None:
        reg = PromptRegistry()
        reg.register(self._make_tpl("foo", "1.0.0"))
        reg.register(self._make_tpl("foo", "1.0.0"), allow_overwrite=True)
        assert "foo" in reg.list_templates()

    def test_latest_tracks_highest_version(self) -> None:
        reg = PromptRegistry()
        reg.register(self._make_tpl("bar", "1.0.0"))
        reg.register(self._make_tpl("bar", "3.0.0"))
        reg.register(self._make_tpl("bar", "2.0.0"))
        assert reg.get_latest_version("bar") == "3.0.0"


class TestPromptRegistryGet:
    def _load(self) -> PromptRegistry:
        reg = PromptRegistry()
        reg.load_yaml_text(MULTI_VERSION_YAML)
        return reg

    def test_get_latest_by_default(self) -> None:
        reg = self._load()
        tpl = reg.get("analyze")
        assert tpl.version == "2.0.0"

    def test_get_specific_version(self) -> None:
        reg = self._load()
        tpl = reg.get("analyze", version="1.0.0")
        assert tpl.version == "1.0.0"

    def test_get_not_found_raises(self) -> None:
        reg = PromptRegistry()
        with pytest.raises(TemplateNotFoundError):
            reg.get("nonexistent")

    def test_get_version_not_found_raises(self) -> None:
        reg = self._load()
        with pytest.raises(TemplateNotFoundError):
            reg.get("analyze", version="9.9.9")


class TestPromptRegistryRender:
    def _load(self) -> PromptRegistry:
        reg = PromptRegistry()
        reg.load_yaml_text(MINIMAL_YAML)
        return reg

    def test_render_returns_rendered_prompt(self) -> None:
        reg = self._load()
        result = reg.render("greet", {"user": "ZephyrAlpha"})
        assert isinstance(result, RenderedPrompt)
        assert "ZephyrAlpha" in result.rendered_text

    def test_render_missing_variable_raises(self) -> None:
        reg = self._load()
        with pytest.raises(VariableError):
            reg.render("greet", {})

    def test_render_token_count_positive(self) -> None:
        reg = self._load()
        result = reg.render("greet", {"user": "Alice"})
        assert result.token_count > 0


class TestPromptRegistryRenderWithContext:
    def _make_registry(self) -> PromptRegistry:
        yaml_text = textwrap.dedent("""\
            prompt_registry_version: "1.0.0"
            templates:
              - template_id: ctx_template
                name: "Context Template"
                version: "1.0.0"
                stability: evolving
                token_budget: 8000
                variables:
                  - name: task_id
                    required: true
                  - name: injected_context
                    required: false
                    default: ""
                template_text: "Analyze {task_id}\\nContext: {injected_context}"
        """)
        reg = PromptRegistry()
        reg.load_yaml_text(yaml_text)
        return reg

    def test_render_with_context_sets_flag(self) -> None:
        reg = self._make_registry()

        # Mock ContextInjector — inject() 直接返回配置好的 mock 对象
        mock_injected = MagicMock()
        mock_injected.context = "relevant KE context"
        mock_injected.sources = ["ke/KE-001.md"]

        mock_injector = MagicMock()
        mock_injector.inject.return_value = mock_injected

        result = reg.render_with_context(
            "ctx_template",
            {"task_id": "T-2-28"},
            mock_injector,
            context_query="prompt registry",
        )

        assert result.context_injected is True
        assert any("KE-001.md" in src for src in result.context_sources)
        assert "T-2-28" in result.rendered_text
