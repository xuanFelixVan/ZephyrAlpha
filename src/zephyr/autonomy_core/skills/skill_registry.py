# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_registry
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
skill-registry.py —— Skill 注册基座（Phase 14 | 盲点 B34）

痛点修复：prompt_registry.py 在 context-engine/ 而非 shared/，
且缺少与 Skill 系统的 Pydantic 抽象层。
需在 shared/ 定义 PromptTemplate + SkillDefinition Pydantic 模型作为跨层契约。

设计对标：
  - PydanticAI Agent Skills: SkillDefinition 声明式能力定义
  - context-engine/prompt_registry.py: 已有的 PromptTemplate 模型（本模块对齐）
  - VSCode Copilot Skills: 可注册/可发现的能力模块化

AI 施工约定：
  - SkillDefinition 是 shared/ 层的抽象契约—不包含引擎逻辑
  - 与 context-engine/prompt_registry.py 互补——本模块为跨层数据契约
  - PromptTemplate 版本管理——semver + stability + variable validation

SSoT: MOD-INF-019 §12 盲点 B34
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum, unique
from typing import Any

from pydantic import BaseModel, Field, field_validator

from zephyr.integration.shared.schema.schemas import BASE_CONFIG
# 5.160.20 修复：SEMVER正则统一为共享常量
from zephyr.shared.foundation.constants import SEMVER_PATTERN

_STABILITY_VALUES: frozenset[str] = frozenset({"experimental", "beta", "stable", "frozen"})


def _validate_semver(v: str) -> str:
    if not SEMVER_PATTERN.match(v):
        raise ValueError(f"version must be semver (X.Y.Z), got: {v!r}")
    return v


def _validate_stability(v: str) -> str:
    if v not in _STABILITY_VALUES:
        raise ValueError(f"stability must be one of {_STABILITY_VALUES}, got: {v!r}")
    return v


class PromptVariable(BaseModel):
    """Prompt 模板的变量声明。与 context-engine/prompt_registry.py 对齐。"""

    model_config = BASE_CONFIG

    name: str = Field(min_length=1, description="变量名称")
    description: str = Field(default="", description="变量用途说明")
    required: bool = Field(default=True, description="是否为必填变量")
    default: str | None = Field(default=None, description="非必填时的默认值")


class PromptTemplate(BaseModel):
    """Prompt 模板抽象——跨层数据契约。"""

    model_config = BASE_CONFIG

    template_id: str = Field(min_length=1, description="模板唯一标识符")
    name: str = Field(min_length=1, description="模板名称")
    version: str = Field(default="1.0.0", description="Semver 版本号")
    stability: str = Field(default="experimental", description="experimental|beta|stable|frozen")
    description: str = Field(default="", description="模板用途说明")
    template_str: str = Field(min_length=1, description="模板文本——{variable} 占位符")
    variables: list[PromptVariable] = Field(default_factory=list, description="变量声明列表")
    token_budget: int = Field(default=2000, ge=0, description="渲染后的 token 预算上限")
    tags: list[str] = Field(default_factory=list, description="分类标签")

    @field_validator("version")
    @classmethod
    def _check_version(cls, v: str) -> str:
        return _validate_semver(v)

    @field_validator("stability")
    @classmethod
    def _check_stability(cls, v: str) -> str:
        return _validate_stability(v)

    def extract_variables(self) -> set[str]:
        """从 template_str 中自动提取占位符变量名。"""
        return set(re.findall(r"\{(\w+)\}", self.template_str))

    def validate_variables(self) -> list[str]:
        """校验 template_str 与 variables 声明一致。返回不一致信息列表。"""
        issues: list[str] = []
        template_vars = self.extract_variables()
        declared_vars = {v.name for v in self.variables}

        missing_declared = template_vars - declared_vars
        if missing_declared:
            issues.append(f"Template vars not declared: {missing_declared}")

        unused_declared = declared_vars - template_vars
        if unused_declared:
            issues.append(f"Declared vars not in template: {unused_declared}")

        return issues


@unique
class SkillCategory(str, Enum):
    CODE = "code"
    WRITING = "writing"
    RESEARCH = "research"
    AUTOMATION = "automation"
    ANALYSIS = "analysis"
    DESIGN = "design"


class SkillParameter(BaseModel):
    """Skill 输入参数定义。"""

    model_config = BASE_CONFIG

    name: str = Field(min_length=1, description="参数名")
    param_type: str = Field(default="string", description="参数类型: string|integer|float|boolean|list")
    description: str = Field(default="", description="参数说明")
    required: bool = Field(default=True)
    default: object = None


class SkillOutput(BaseModel):
    """Skill 输出 Schema 定义。"""

    model_config = BASE_CONFIG

    output_type: str = Field(default="dict", description="输出类型")
    description: str = Field(default="", description="输出说明")
    schema_example: dict[str, Any] = Field(default_factory=dict, description="输出 schema 示例")


class SkillDefinition(BaseModel):
    """Skill 定义——跨层契约模型。

    Usage::

        skill = SkillDefinition(
            skill_id="find-code-refs",
            name="Find Code References",
            category=SkillCategory.CODE,
            description="Search codebase for references to a symbol",
            prompt_template=PromptTemplate(
                template_id="find-refs-v1",
                name="Find References",
                template_str="Find all references to {symbol} in the codebase",
                variables=[PromptVariable(name="symbol", required=True)],
            ),
            input_schema=[SkillParameter(name="symbol", param_type="string", required=True)],
            output_schema=SkillOutput(
                output_type="list",
                description="List of file paths and line numbers",
            ),
        )
    """

    model_config = BASE_CONFIG

    skill_id: str = Field(min_length=1, description="Skill 唯一标识符")
    name: str = Field(min_length=1, description="Skill 名称")
    version: str = Field(default="1.0.0", description="Semver 版本号")
    stability: str = Field(default="experimental", description="稳定性")
    category: SkillCategory = Field(default=SkillCategory.CODE, description="Skill 分类")
    description: str = Field(default="", description="Skill 用途说明")
    prompt_template: PromptTemplate = Field(description="关联的 Prompt 模板")
    input_schema: list[SkillParameter] = Field(default_factory=list, description="输入参数定义")
    output_schema: SkillOutput | None = Field(default=None, description="输出 Schema 定义")
    metadata: dict[str, str] = Field(default_factory=dict, description="扩展元数据")
    tags: list[str] = Field(default_factory=list, description="分类标签")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("version")
    @classmethod
    def _check_version(cls, v: str) -> str:
        return _validate_semver(v)

    @field_validator("stability")
    @classmethod
    def _check_stability(cls, v: str) -> str:
        return _validate_stability(v)


__all__ = [
    "PromptTemplate",
    "PromptVariable",
    "SkillCategory",
    "SkillDefinition",
    "SkillOutput",
    "SkillParameter",
]
