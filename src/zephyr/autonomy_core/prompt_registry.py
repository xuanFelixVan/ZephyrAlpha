# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.prompt_registry
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_prompt_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# AI-generated: YAML-driven prompt template registry with version management and token budget
"""
PromptRegistry: YAML-driven Prompt 模板注册表
=============================================
Task ID  : T-2-28 (B12)
safety_level : L
Depends  : context_injector.py（集成接口）

功能
----
- 从 YAML 文件或字符串加载 Prompt 模板
- 模板版本管理（semver，自动追踪 latest）
- 变量插值（Python str.format_map，安全无副作用）
- Token 预算约束（4 字符/token 启发式，与 context_injector 一致）
- 与 ContextInjector 的 render_with_context 集成接口

YAML 格式示例
-------------
prompt_registry_version: "1.0.0"
templates:
  - template_id: task_analysis
    name: "Task Analysis"
    version: "1.0.0"
    stability: stable
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

from __future__ import annotations

import re
import string
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog
import yaml
from pydantic import BaseModel, Field, field_validator

from zephyr.infrastructure.capacity_assurance.token_budget import estimate_tokens
from zephyr.integration.shared.schema.schemas import BASE_CONFIG

if TYPE_CHECKING:
    from zephyr.autonomy_core.context.context_injector import ContextInjector, InjectedContext

__all__ = [
    "PromptRegistry",
    "PromptRegistryError",
    "PromptTemplate",
    "PromptVariable",
    "PromptVersion",
    "RenderedPrompt",
    "TemplateNotFoundError",
    "TokenBudgetExceededError",
    "VariableError",
]

_log = structlog.get_logger().bind(layer="infra", module="prompt_registry")


class _SafeFormatter(string.Formatter):
    """5.146.5 修复: 仅允许 {name} 简单替换, 阻止 {obj.attr} / {obj[key]} 属性/索引访问。

    str.format_map 支持格式说明符中的属性访问({var.__class__})和索引访问,
    当 template_text 是 AI 可编辑的 prompt 模板时, 构成纵深防御缺口。
    本 Formatter 仅允许简单 {name} 占位符, 阻断属性链/索引链 RCE 路径。
    """

    def get_field(self, field_name: str, args: tuple, kwargs: dict) -> tuple[Any, str]:
        if "." in field_name or "[" in field_name:
            raise ValueError(f"Unsafe format spec blocked: {{{field_name}}}")
        return super().get_field(field_name, args, kwargs)


_safe_formatter = _SafeFormatter()

_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_STABILITY_VALUES: frozenset[str] = frozenset({"experimental", "beta", "stable", "frozen"})
_PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _semver_tuple(version: str) -> tuple[int, int, int]:
    """将 semver 字符串转换为可比较的元组。"""
    parts = version.split(".")
    return (int(parts[0]), int(parts[1]), int(parts[2]))


def _compare_semver(a: str, b: str) -> int:
    """比较两个 semver 字符串。返回 -1/0/1。"""
    ta = _semver_tuple(a)
    tb = _semver_tuple(b)
    if ta < tb:
        return -1
    if ta > tb:
        return 1
    return 0


# ---------------------------------------------------------------------------
# 异常层次
# ---------------------------------------------------------------------------


class PromptRegistryError(Exception):
    """PromptRegistry 基础异常。"""


class TokenBudgetExceededError(PromptRegistryError):
    """渲染后的 Prompt 超出 token 预算时抛出。"""


class TemplateNotFoundError(PromptRegistryError):
    """模板 ID 或版本未注册时抛出。"""


class VariableError(PromptRegistryError):
    """必填变量缺失或未知占位符时抛出。"""


# ---------------------------------------------------------------------------
# Pydantic 数据模型
# ---------------------------------------------------------------------------


class PromptVariable(BaseModel):
    """Prompt 模板的变量声明。"""

    model_config = BASE_CONFIG

    name: str = Field(min_length=1, description="变量名称")
    description: str = Field(default="", description="变量用途说明")
    required: bool = Field(default=True, description="是否为必填变量")
    default: str | None = Field(default=None, description="非必填时的默认值")
    var_type: str = Field(
        default="string",
        description="期望类型：string | integer | float | boolean",
    )


class PromptVersion(BaseModel):
    """单个版本的元信息（独立记录，供 changelog 追踪）。"""

    model_config = BASE_CONFIG

    version: str = Field(description="Semver 版本号，如 1.0.0")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    changelog: str = Field(default="", description="该版本变更说明")
    stability: str = Field(
        default="experimental",
        description="experimental | beta | stable | frozen",
    )

    @field_validator("version")
    @classmethod
    def _validate_semver(cls, v: str) -> str:
        if not _SEMVER_RE.match(v):
            raise ValueError(f"version 必须是 semver（X.Y.Z），得到：{v!r}")
        return v

    @field_validator("stability")
    @classmethod
    def _validate_stability(cls, v: str) -> str:
        if v not in _STABILITY_VALUES:
            raise ValueError(f"stability 必须是 {_STABILITY_VALUES} 之一，得到：{v!r}")
        return v


class PromptTemplate(BaseModel):
    """Prompt 模板实体（含版本、变量、token 预算）。"""

    model_config = BASE_CONFIG

    template_id: str = Field(min_length=1, description="模板唯一标识符")
    name: str = Field(description="人类可读名称")
    description: str = Field(default="", description="模板用途说明")
    version: str = Field(description="Semver 版本号")
    stability: str = Field(default="experimental", description="experimental | beta | stable | frozen")
    variables: list[PromptVariable] = Field(default_factory=list, description="变量声明列表")
    token_budget: int = Field(default=4000, ge=1, description="渲染后最大 token 数")
    template_text: str = Field(description="模板正文，含 {variable} 占位符")
    system_prefix: str = Field(default="", description="可选的 system 消息前缀")
    tags: list[str] = Field(default_factory=list, description="检索标签")

    @field_validator("version")
    @classmethod
    def _validate_semver(cls, v: str) -> str:
        if not _SEMVER_RE.match(v):
            raise ValueError(f"version 必须是 semver（X.Y.Z），得到：{v!r}")
        return v

    @field_validator("stability")
    @classmethod
    def _validate_stability(cls, v: str) -> str:
        if v not in _STABILITY_VALUES:
            raise ValueError(f"stability 必须是 {_STABILITY_VALUES} 之一")
        return v

    def get_placeholder_names(self) -> set[str]:
        """从 template_text 中提取所有 {placeholder} 名称。"""
        return set(_PLACEHOLDER_RE.findall(self.template_text))

    def render(self, variables: dict[str, str]) -> RenderedPrompt:
        """用给定变量渲染模板。

        Parameters
        ----------
        variables:
            键值对，将替换模板中的 {placeholder}。

        Raises
        ------
        VariableError
            必填变量缺失，或变量名与占位符不匹配。
        TokenBudgetExceededError
            渲染结果超出 token_budget。
        """
        effective: dict[str, str] = {}

        for var in self.variables:
            if var.name in variables:
                effective[var.name] = str(variables[var.name])
            elif not var.required and var.default is not None:
                effective[var.name] = var.default
            elif var.required:
                raise VariableError(f"模板 '{self.template_id}' 缺少必填变量 '{var.name}'")

        # 允许传入未声明的额外变量（透传）
        for k, v in variables.items():
            if k not in effective:
                effective[k] = str(v)

        try:
            # 5.146.5 修复: 用 _SafeFormatter 替代 str.format_map, 阻止 {obj.attr}/{obj[key]} 属性/索引访问
            rendered_body = _safe_formatter.vformat(self.template_text, (), effective)
        except KeyError as exc:
            raise VariableError(f"模板 '{self.template_id}' 含未知占位符 {exc}") from exc
        except ValueError as exc:
            raise VariableError(f"模板 '{self.template_id}' 含不安全格式说明符: {exc}") from exc

        full_text = f"{self.system_prefix}\n{rendered_body}".strip() if self.system_prefix else rendered_body
        token_count = estimate_tokens(full_text)

        if token_count > self.token_budget:
            raise TokenBudgetExceededError(
                f"模板 '{self.template_id}' 渲染后 {token_count} tokens，超出预算 {self.token_budget}"
            )

        return RenderedPrompt(
            template_id=self.template_id,
            version=self.version,
            rendered_text=full_text,
            variables_used=list(effective.keys()),
            token_count=token_count,
            budget_remaining=self.token_budget - token_count,
        )


class RenderedPrompt(BaseModel):
    """模板渲染结果。"""

    model_config = BASE_CONFIG

    template_id: str = Field(description="来源模板 ID")
    version: str = Field(description="来源模板版本")
    rendered_text: str = Field(description="最终渲染文本")
    variables_used: list[str] = Field(default_factory=list, description="实际使用的变量名列表")
    token_count: int = Field(ge=0, description="估算 token 数")
    budget_remaining: int = Field(ge=0, description="剩余 token 预算")
    context_injected: bool = Field(default=False, description="是否注入了 KB 上下文")
    context_sources: list[str] = Field(default_factory=list, description="KB 上下文来源路径")


# ---------------------------------------------------------------------------
# 注册表主体
# ---------------------------------------------------------------------------


class PromptRegistry:
    """YAML 驱动的 Prompt 模板注册表。

    功能
    ----
    - ``load_yaml(path)``：从 YAML 文件加载模板
    - ``load_yaml_text(text)``：从 YAML 字符串加载模板
    - ``register(template)``：手动注册单个模板
    - ``get(template_id, version=None)``：获取模板（默认取 latest）
    - ``render(template_id, variables)``：渲染模板
    - ``render_with_context(...)``：渲染并注入 KB 上下文
    - ``list_templates()``：列出所有已注册模板 ID
    - ``list_versions(template_id)``：列出某模板所有版本
    """

    def __init__(self) -> None:
        # (template_id, version) -> PromptTemplate
        self._templates: dict[tuple[str, str], PromptTemplate] = {}
        # template_id -> latest version string
        self._latest: dict[str, str] = {}

    # ------------------------------------------------------------------
    # 加载接口
    # ------------------------------------------------------------------

    def load_yaml(self, path: Path | str) -> int:
        """从 YAML 文件加载模板，返回成功加载的模板数量。"""
        resolved = Path(path)
        raw: dict[str, Any] = yaml.safe_load(resolved.read_text(encoding="utf-8"))
        count = self._load_from_dict(raw)
        _log.info("yaml_loaded", path=str(resolved), count=count)
        return count

    def load_yaml_text(self, text: str) -> int:
        """从 YAML 字符串加载模板，返回成功加载的模板数量。"""
        raw: dict[str, Any] = yaml.safe_load(text)
        return self._load_from_dict(raw)

    def _load_from_dict(self, raw: dict[str, Any]) -> int:
        templates_data: list[dict[str, Any]] = raw.get("templates", [])
        count = 0
        for item in templates_data:
            tpl = PromptTemplate(**item)
            self.register(tpl)
            count += 1
        return count

    # ------------------------------------------------------------------
    # 注册 / 查询接口
    # ------------------------------------------------------------------

    def register(self, template: PromptTemplate, *, allow_overwrite: bool = False) -> None:
        """注册单个模板。

        Parameters
        ----------
        template:
            要注册的 PromptTemplate 实例。
        allow_overwrite:
            为 True 时允许覆盖同 ID+版本的已有模板。
        """
        key = (template.template_id, template.version)
        if key in self._templates and not allow_overwrite:
            raise PromptRegistryError(
                f"模板 '{template.template_id}' v{template.version} 已注册，如需替换请使用 allow_overwrite=True"
            )
        self._templates[key] = template

        current_latest = self._latest.get(template.template_id)
        if current_latest is None or _compare_semver(template.version, current_latest) > 0:
            self._latest[template.template_id] = template.version

        _log.debug(
            "template_registered",
            template_id=template.template_id,
            version=template.version,
            stability=template.stability,
        )

    def get(self, template_id: str, version: str | None = None) -> PromptTemplate:
        """按 ID 和可选版本获取模板（version=None 时取 latest）。

        Raises
        ------
        TemplateNotFoundError
            template_id 或指定版本未注册。
        """
        resolved_version: str | None = version
        if resolved_version is None:
            resolved_version = self._latest.get(template_id)
            if resolved_version is None:
                raise TemplateNotFoundError(f"模板 '{template_id}' 未注册")

        key = (template_id, resolved_version)
        if key not in self._templates:
            raise TemplateNotFoundError(f"模板 '{template_id}' v{resolved_version} 未注册")
        return self._templates[key]

    def list_templates(self) -> list[str]:
        """列出所有已注册模板 ID。"""
        return list(self._latest.keys())

    def list_versions(self, template_id: str) -> list[str]:
        """列出某模板的所有版本（升序排列）。"""
        versions = [v for (tid, v) in self._templates if tid == template_id]
        return sorted(versions, key=_semver_tuple)

    def get_latest_version(self, template_id: str) -> str:
        """返回某模板的 latest 版本号。

        Raises
        ------
        TemplateNotFoundError
            template_id 未注册。
        """
        latest = self._latest.get(template_id)
        if latest is None:
            raise TemplateNotFoundError(f"模板 '{template_id}' 未注册")
        return latest

    # ------------------------------------------------------------------
    # 渲染接口
    # ------------------------------------------------------------------

    def render(
        self,
        template_id: str,
        variables: dict[str, str],
        version: str | None = None,
    ) -> RenderedPrompt:
        """渲染指定模板（不注入 KB 上下文）。

        Parameters
        ----------
        template_id:
            模板 ID。
        variables:
            变量字典。
        version:
            指定版本，None 表示取 latest。

        Returns
        -------
        RenderedPrompt
            渲染结果，含 token_count 和 budget_remaining。
        """
        template = self.get(template_id, version)
        result = template.render(variables)
        _log.info(
            "template_rendered",
            template_id=template_id,
            version=template.version,
            token_count=result.token_count,
        )
        return result

    def render_with_context(
        self,
        template_id: str,
        variables: dict[str, str],
        injector: ContextInjector,
        context_query: str,
        version: str | None = None,
    ) -> RenderedPrompt:
        """渲染模板并注入 KB 上下文（与 ContextInjector 集成接口）。

        Token 预算分配策略：一半用于注入上下文，一半留给模板其他变量。
        注入内容以 ``injected_context`` 变量名传入模板。

        Parameters
        ----------
        template_id:
            模板 ID。
        variables:
            用户提供的变量字典（不含 injected_context）。
        injector:
            ContextInjector 实例，用于检索 KB 上下文。
        context_query:
            传给 ContextInjector 的查询字符串。
        version:
            指定版本，None 表示取 latest。

        Returns
        -------
        RenderedPrompt
            渲染结果，context_injected=True，context_sources 已填充。
        """
        template = self.get(template_id, version)

        injected_ctx: InjectedContext = injector.inject(context_query)

        merged = dict(variables)
        merged.setdefault("injected_context", injected_ctx.context)

        result = template.render(merged)

        _log.info(
            "template_rendered_with_context",
            template_id=template_id,
            version=template.version,
            token_count=result.token_count,
            context_sources=injected_ctx.sources,
        )

        return RenderedPrompt(
            template_id=result.template_id,
            version=result.version,
            rendered_text=result.rendered_text,
            variables_used=result.variables_used,
            token_count=result.token_count,
            budget_remaining=result.budget_remaining,
            context_injected=True,
            context_sources=injected_ctx.sources,
        )
