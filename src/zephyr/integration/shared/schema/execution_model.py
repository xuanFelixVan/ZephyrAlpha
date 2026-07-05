# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared.schema.execution_model
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] gates.task_types; shared.schema.schemas; core.blueprint_decomposer; db.task_repo; orchestrator; mcp; kb
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ExecutionModel values MUST match supported LLM providers
# [MODIFY-GUARD] §4.2; PS-STD-001 §7.1~§7.1.1
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ValueError on invalid execution model string
# [TESTS] tests/test_schemas.py
# [A_module] module_id=MOD-SHR_execution_model | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from enum import Enum

__all__ = [
    "ExecutionModel",
    "normalize_execution_model",
]


class ExecutionModel(str, Enum):
    deepseek = "deepseek"
    glm = "glm"
    claude = "claude"
    kimi = "kimi"
    qwen = "qwen"


def normalize_execution_model(value: str | ExecutionModel) -> ExecutionModel:
    if isinstance(value, ExecutionModel):
        return value
    v = str(value).strip().lower()
    try:
        return ExecutionModel(v)
    except ValueError:
        pass
    if v.startswith("claude"):
        return ExecutionModel.claude
    if v.startswith("glm"):
        return ExecutionModel.glm
    if "deepseek" in v or v in ("ds", "deep_seek"):
        return ExecutionModel.deepseek
    if v.startswith("kimi"):
        return ExecutionModel.kimi
    if v.startswith("qwen"):
        return ExecutionModel.qwen
    if v == "system":
        return ExecutionModel.qwen
    return ExecutionModel.deepseek
