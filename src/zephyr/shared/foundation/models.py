# [BLUEPRINT] SRC-120 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.foundation.models
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] db.task_repo; core.blueprint_decomposer; pipeline.*; orchestrator.*
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] TaskCard = Task (PURE ALIAS — NOT a second model. SSoT: gates/task_types.py Task 70 fields. DO NOT add fields here.)
# [MODIFY-GUARD] gates/task_types.py (SSoT for Task/GateLevel/TaskAuditFinding)
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS] tests/test_schemas.py; tests/db/test_task_repo.py; tests/gate/test_gate_engine.py
# [A_module] module_id=MOD-INF_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ZephyrAlpha 任务系统核心数据模型
================================
Task/GateLevel/TaskAuditFinding  SSoT: gates/task_types.py（70字段，2026-05-28合并）
DecompositionResult/GateCheckResult: 本模块本地定义

⚠️  AI SESSION NOTICE — 防漂移标识 ⚠️
TaskCard = Task 是纯别名，不是第二个模型。禁止对 TaskCard 做任何修改。
SSoT 唯一入口: from zephyr.governance.rule_enforcement.task_types import Task
若需修改任务卡字段 → 改 gates/task_types.py Task 模型 → 同步 migration + INSERT + TEMPLATE_REQUIRED_FIELDS
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

__all__ = [
    "DecompositionResult",
    "GateCheckResult",
    "GateLevel",
    "Task",
    "TaskAuditFinding",
    "TaskCard",
    "TaskNamespace",
    "TaskStatus",
]

_LAZY_GOVERNANCE_ATTRS: dict[str, str] = {
    "TaskStatus": "TaskStatus",
    "TaskNamespace": "TaskNamespace",
    "GateLevel": "GateLevel",
    "TaskAuditFinding": "TaskAuditFinding",
    "Task": "Task",
}


import importlib


def _lazy_import_governance(name: str):
    _tt = importlib.import_module("zephyr.governance.rule_enforcement.task_types")
    return getattr(_tt, name)


class DecompositionResult(BaseModel):
    """蓝图拆解结果——蓝图 MOD-TASK_SYSTEM §3.2.2"""

    model_config = BaseModel.model_config

    total_tasks: int = Field(ge=0)
    tasks: list[TaskCard]
    dependency_graph: dict[str, list[str]] = Field(default_factory=dict)
    unassigned_items: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GateCheckResult(BaseModel):
    """门禁检查结果——蓝图 MOD-TASK_SYSTEM §3.2.2"""

    model_config = BaseModel.model_config

    gate_id: GateLevel
    task_id: str
    passed: bool
    violations: list[str] = Field(default_factory=list)
    checked_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# 治本: 显式触发 lazy 加载并注入 globals, 使 pydantic forward reference 能被 model_rebuild() 解析。
# 原 shared_services proxy 通过 dir()+getattr() 循环无意中触发, 删除 proxy 后需在此显式补全。
# task_types.py 不依赖本模块 (import 链: integration.shared.schema.*), 无循环 import 风险。
TaskCard = _lazy_import_governance("Task")
Task = _lazy_import_governance("Task")
TaskStatus = _lazy_import_governance("TaskStatus")
TaskNamespace = _lazy_import_governance("TaskNamespace")
GateLevel = _lazy_import_governance("GateLevel")
TaskAuditFinding = _lazy_import_governance("TaskAuditFinding")
DecompositionResult.model_rebuild()
GateCheckResult.model_rebuild()

_STABILITY_FROZEN = True
_FROZEN_PUBLIC_API = frozenset(__all__)


def __getattr__(name: str):
    if name in _LAZY_GOVERNANCE_ATTRS:
        return _lazy_import_governance(name)
    if name == "TaskCard":
        return _lazy_import_governance("Task")
    if name in _FROZEN_PUBLIC_API:
        import logging

        logging.getLogger("zephyr.stability_guard").warning(
            "STABILITY VIOLATION: Public API attribute '%s' removed from frozen module zephyr.infrastructure.shared_services.models",
            name,
        )
    raise AttributeError(f"module 'zephyr.infrastructure.shared_services.models' has no attribute {name!r}")
