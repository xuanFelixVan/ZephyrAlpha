# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.schema.task_types
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance; zephyr.infrastructure; zephyr.trading (replaces shared_services.models imports)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] TaskCard = Task (PURE ALIAS — SSoT: governance.rule_enforcement.task_types.Task); 本模块禁止添加字段
# [MODIFY-GUARD] governance.rule_enforcement.task_types (SSoT)
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS] tests/test_schemas.py; tests/db/test_task_repo.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
task_types — 任务系统核心类型 re-export 层
=========================================
从 governance.rule_enforcement.task_types (SSoT) re-export，
替代 infrastructure.shared_services.models 中的 TaskCard 别名。
D-DATA、D-INFRA、D-ORCH 均从此模块导入，消除跨域直接依赖。

使用 __getattr__ 延迟导入，避免模块初始化时的循环依赖。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: task_types.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 ExecutionModel, GateLevel, Task, TaskAuditFinding, TaskCard, TaskNamespace,…
#   desc: __init__ import L0；__all__ 8 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（8 符号）
#   name_en: __all__
#   intro: ExecutionModel, GateLevel, Task, TaskAuditFinding, TaskCard, TaskNamespace, Tas…
#   downstream: zephyr.governance; zephyr.infrastructure; zephyr.trading (replaces shared_servi…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

__all__ = [
    "ExecutionModel",
    "GateLevel",
    "Task",
    "TaskAuditFinding",
    "TaskCard",
    "TaskNamespace",
    "TaskStatus",
    "normalize_execution_model",
]

_SOURCE_MODULE = "zephyr.gov_enforcement.rule_enforcement.task_types"
_EXEC_MODEL_MODULE = "zephyr.shared.schema.execution_model"

_LAZY_IMPORTS = {
    "Task": _SOURCE_MODULE,
    "TaskStatus": _SOURCE_MODULE,
    "TaskNamespace": _SOURCE_MODULE,
    "GateLevel": _SOURCE_MODULE,
    "TaskAuditFinding": _SOURCE_MODULE,
    "ExecutionModel": _EXEC_MODEL_MODULE,
    "normalize_execution_model": _EXEC_MODEL_MODULE,
}


def __getattr__(name: str):
    if name == "TaskCard":
        import importlib

        module = importlib.import_module(_SOURCE_MODULE)
        value = module.Task
        globals()["TaskCard"] = value
        return value
    if name in _LAZY_IMPORTS:
        import importlib

        module = importlib.import_module(_LAZY_IMPORTS[name])
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return list(__all__)
