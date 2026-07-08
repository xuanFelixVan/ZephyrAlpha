# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_pipeline
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__; zephyr.integration.shared.schema.schemas
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
# [A_module] module_id=MOD-ORC_context_pipeline | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
context_pipeline — Context Engine **四段流水线组合根**
======================================================

病根（为何审计会判「 Assembler ≠ build->compress->validate->inject 」）
--------------------------------------------------------------------
1. ``zephyr.autonomy_core`` 包文档与 ``docs/.../context-engine-interface.md``
   将 **同一语义**约束为 ``build -> compress -> validate -> inject``。
2. 实现演进时三段能力落在 **独立类**：``ContextAssembler``（已将 build + 超限 compress
   内联在同一 ``assemble``）、``DocCompressor``、``ContextInjector``，
   **未提供组合根**，于是「等价性」无法在单模块内验证——这是**结构性缺口**，而非单点 bug。
3. 本模块只做 **显式编排**（不改变子组件算法），把调用顺序钉为蓝图顺序，供门禁/集成引用。

语义映射
--------
- **build + compress**：``ContextAssembler.assemble`` —— manifest 读到 ``context_text``，
  token 超限则内置 ``DocCompressor``（见 Assembler 源码）。
- **validate**：``ContextAssembler.validate``（G3）。
- **inject**（可选）：``ContextInjector`` —— KB 检索，与 manifest 拼装结果用分隔符合并。

inject 省略时仍可完成前三段闭环；KB refactor Step 2.1 移除 kb_repo 后 inject 返回空上下文。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from zephyr.shared.blueprint_tools.architecture_context_loader import (
    format_architecture_context_excerpt,
    load_architecture_context_dict,
)
from zephyr.autonomy_core.context.context_assembler import AssembledContext, AssemblyError, ContextAssembler
from zephyr.autonomy_core.context.context_injector import ContextInjector, InjectedContext
from zephyr.autonomy_core.context.context_rule_registry import ContextRuleRegistry
from zephyr.infrastructure.capacity_assurance.token_budget import DEFAULT_CONTEXT_TOKEN_BUDGET
from zephyr.integration.shared.schema.schemas import BASE_CONFIG

InjectMode = Literal["none", "task_id", "module_id", "keyword"]

__all__ = [
    "ContextFourStageResult",
    "run_context_four_stage",
    "run_context_four_stage_or_raise",
]


class ContextFourStageResult(BaseModel):
    """四段流水线一次跑完的结构化产出。"""

    model_config = BASE_CONFIG

    assembled: AssembledContext
    g3_passed: bool
    injected: InjectedContext | None = None
    final_context: str = Field(
        default="",
        description="manifest 上下文与（若有）KB inject 上下文合并后的建议使用串",
    )
    pipeline_warnings: list[str] = Field(default_factory=list)


def run_context_four_stage(
    manifest: list[dict[str, str]],
    *,
    token_budget: int = DEFAULT_CONTEXT_TOKEN_BUDGET,
    compress_manifest: bool = True,
    require_absolute_manifest_paths: bool = True,
    inject_mode: InjectMode = "none",
    inject_query: str = "",
    assembler: ContextAssembler | None = None,
    injector: ContextInjector | None = None,
    include_architecture_context: bool = False,
    architecture_context_path: Path | None = None,
    rule_registry: ContextRuleRegistry | None = None,
) -> ContextFourStageResult:
    """按蓝图顺序执行 build(含压缩)->validate->(可选)inject。

    Parameters
    ----------
    manifest
        ``TaskCard.context_assembly_manifest`` 形态。
    inject_mode / inject_query
        ``inject_mode != "none"`` 时需 ``inject_query`` 非空（KB refactor 后 inject 返回空上下文）。
    include_architecture_context
        为 True 时尝试加载 ``architecture-context.json`` 并前置到 ``final_context``。
    architecture_context_path
        显式 JSON 路径；默认使用 ``context_engine/architecture-context.json``。
    """
    warnings: list[str] = []
    asm = assembler or ContextAssembler(
        require_absolute_paths=require_absolute_manifest_paths,
        rule_registry=rule_registry,
    )
    assembled = asm.assemble(manifest, token_budget=token_budget, compress=compress_manifest)

    arch_blob = ""
    if include_architecture_context:
        arch = load_architecture_context_dict(architecture_context_path)
        arch_blob = format_architecture_context_excerpt(arch)
        if not arch_blob.strip():
            warnings.append(
                "architecture_context: 未找到预编译 JSON，请运行 "
                "python scripts/context/generate_architecture_context.py",
            )

    g3 = asm.validate(assembled)
    if not g3:
        warnings.append("G3_validate: assemble 结果未通过校验（见 AssembledContext.errors）")

    injected: InjectedContext | None = None
    final_ctx = assembled.context_text
    if arch_blob.strip():
        final_ctx = arch_blob.strip() + "\n\n--- MANIFEST_CONTEXT ---\n\n" + final_ctx

    if inject_mode != "none":
        if not inject_query.strip():
            warnings.append("inject: inject_mode≠none 但 inject_query 为空，已跳过 inject")
        else:
            inj = injector or ContextInjector(token_budget=token_budget)
            try:
                if inject_mode == "task_id":
                    injected = inj.inject_by_task_id(inject_query.strip())
                elif inject_mode == "module_id":
                    injected = inj.inject_by_module_id(inject_query.strip())
                elif inject_mode == "keyword":
                    injected = inj.inject_by_keyword(inject_query.strip())
                merged: list[str] = []
                if final_ctx.strip():
                    merged.append(final_ctx.strip())
                if injected.context.strip():
                    merged.append("--- CONTEXT_ENGINE_INJECT ---\n" + injected.context.strip())
                final_ctx = "\n\n".join(merged)
            except Exception as exc:
                warnings.append(f"inject failed: {type(exc).__name__}: {exc}")

    return ContextFourStageResult(
        assembled=assembled,
        g3_passed=g3,
        injected=injected,
        final_context=final_ctx,
        pipeline_warnings=warnings,
    )


def run_context_four_stage_or_raise(
    manifest: list[dict[str, str]],
    **kwargs: Any,
) -> ContextFourStageResult:
    """同 ``run_context_four_stage``，但当 G3 失败或 assembled 含致命 errors 时抛 ``AssemblyError``。"""
    r = run_context_four_stage(manifest, **kwargs)
    if not r.g3_passed or r.assembled.errors:
        raise AssemblyError(r.assembled.errors or ["G3 validation failed"])
    return r
