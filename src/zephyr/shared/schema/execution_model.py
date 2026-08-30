# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.schema.execution_model
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] orchestrator ; mcp ; kb
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ExecutionModel values MUST match supported LLM providers
# [MODIFY-GUARD] §4.2; PS-STD-001 §7.1~§7.1.1
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ValueError on invalid execution model string
# [TESTS] tests/test_schemas.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: value 参数
#   fields: 参数 value，类型注解 str | ExecutionModel
#   code: execution_model.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① normalize_execution_model
#   name_en: normalize_execution_model
#   intro: normalize_execution_model(value) 源码 L67-L87
#   desc: 源码 L67-L87
#   inputs: value
#   outputs: ExecutionModel
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ExecutionModel
#   name_en: ExecutionModel
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: orchestrator ; mcp ; kb
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
