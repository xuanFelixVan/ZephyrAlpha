# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.testing
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: _utc_now与pipeline_base._utcnow是同类UTC时间工具,趋同演化非复制粘贴

"""
testing.py —— ZephyrAlpha 共享测试夹具/工厂

Phase 5 新增（盲点 B1）——解决此前每个消费者各自手写 TaskCard() 构造代码、
AI 频繁写错字段名/漏必填字段/搞错枚举值的问题。

设计原则：
  - 每个工厂函数返回 valid-by-construction 的模型实例（无需额外校验）
  - 所有必填字段有合法默认值——AI 只需传 override 字段
  - 有 Pydantic default 的字段不显式传（让 Pydantic 处理默认值）
  - 枚举值取常用成员——减少 AI 记忆负担

对标：
  - Meta shared test fixtures: factory_boy / polymorphic factories
  - Django model_mommy: sensible defaults for all fields
  - polyfactory (Pydantic): auto-generated valid instances from model schema

SSoT: MOD-INF-016 §2.11 shared-testing
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: task_id 参数
#   fields: 参数 task_id（无注解）
#   code: testing.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: namespace 参数
#   fields: 参数 namespace（无注解）
#   code: testing.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: seq 参数
#   fields: 参数 seq（无注解）
#   code: testing.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: title 参数
#   fields: 参数 title（无注解）
#   code: testing.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① make_valid_task
#   name_en: make_valid_task
#   intro: 构造一个 valid-by-construction 的 Task 实例。
#   desc: 构造一个 valid-by-construction 的 Task 实例。 必填字段 (task_id/namespace/seq/title/phase/execution_m…；源码 L189-L235
#   inputs: task_id namespace seq title phase execution_model safety_level create…
#   outputs: Task
# - id: A2
#   name_zh: ② make_p0_task
#   name_en: make_p0_task
#   intro: 构造 P0 + H 安全等级的紧急任务。
#   desc: 构造 P0 + H 安全等级的紧急任务。；源码 L238-L245
#   inputs: 无参数
#   outputs: Task
# - id: A3
#   name_zh: ③ make_completed_task
#   name_en: make_completed_task
#   intro: 构造 COMPLETED 状态的任务（completed_at 自动填当前时间）。
#   desc: 构造 COMPLETED 状态的任务（completed_at 自动填当前时间）。；源码 L248-L256
#   inputs: 无参数
#   outputs: Task
# - id: A4
#   name_zh: ④ make_valid_audit_report
#   name_en: make_valid_audit_report
#   intro: 构造 valid-by-construction 的 AuditReport 实例。
#   desc: 构造 valid-by-construction 的 AuditReport 实例。 findings 默认生成一条 P2 的示例 AuditFinding。；源码 L270-L298
#   inputs: report_id scanner scan_target findings
#   outputs: AuditReport
# - id: A5
#   name_zh: ⑤ make_valid_knowledge_entry
#   name_en: make_valid_knowledge_entry
#   intro: 构造 valid-by-construction 的 KnowledgeEntry 实例。
#   desc: 构造 valid-by-construction 的 KnowledgeEntry 实例。；源码 L312-L330
#   inputs: ke_id title category
#   outputs: KnowledgeEntry
# - id: A6
#   name_zh: ⑥ make_valid_failure_pattern
#   name_en: make_valid_failure_pattern
#   intro: 构造 valid-by-construction 的 FailurePattern 实例。
#   desc: 构造 valid-by-construction 的 FailurePattern 实例。；源码 L344-L365
#   inputs: pattern_id failure_type title description reproduction_steps
#   outputs: FailurePattern
# - id: A7
#   name_zh: ⑦ make_valid_handoff_package
#   name_en: make_valid_handoff_package
#   intro: 构造 valid-by-construction 的 HandoffPackage 实例。
#   desc: 构造 valid-by-construction 的 HandoffPackage 实例。；源码 L368-L404
#   inputs: session_id context_summary
#   outputs: HandoffPackage
# 层: 输出
# - id: O1
#   name_zh: Task
#   name_en: Task
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: AuditReport
#   name_en: AuditReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from typing import Any

from zephyr.shared.schema.schemas import (
    AuditFinding,
    AuditReport,
    AuditSeverity,
    BlockedItem,
    Decision,
    ExecutionModel,
    FailurePattern,
    FailureType,
    HandoffPackage,
    KeCategory,
    KnowledgeEntry,
    NextAction,
    Priority,
    SafetyLevel,
    Task,
    TaskNamespace,
    TaskStatus,
    normalize_execution_model,
)

__all__ = [
    "make_completed_task",
    "make_p0_task",
    "make_valid_audit_report",
    "make_valid_failure_pattern",
    "make_valid_handoff_package",
    "make_valid_knowledge_entry",
    "make_valid_task",
]


def _utc_now() -> datetime:
    return datetime.now(UTC)


_task_counter = 0
_counter_lock = threading.Lock()


def _next_task_seq(namespace: str = "STD") -> tuple[str, int]:
    global _task_counter
    with _counter_lock:
        _task_counter += 1
        seq = _task_counter
    task_id = f"{namespace}-{seq:03d}"
    return task_id, seq


def make_valid_task(
    *,
    task_id: str | None = None,
    namespace: TaskNamespace | None = None,
    seq: int = 1,
    title: str = "Factory-generated test task",
    phase: int = 0,
    execution_model: str | ExecutionModel = "deepseek",
    safety_level: SafetyLevel = SafetyLevel.M,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    status: TaskStatus = TaskStatus.PENDING,
    priority: Priority = Priority.P2,
    description: str = "Factory-generated test task description.",
    **overrides: Any,
) -> Task:
    """构造一个 valid-by-construction 的 Task 实例。

    必填字段 (task_id/namespace/seq/title/phase/execution_model/safety_level/
    created_at/updated_at/description) 全部有合法默认值。
    有 Pydantic default 的字段不显式传——让模型自己 fill default。

    用法:
        task = make_valid_task()
        task = make_valid_task(title="Fix bug", priority=Priority.P0, phase=1)
        task = make_valid_task(execution_model="claude")
    """
    now = _utc_now()
    if task_id is None:
        ns = (namespace or TaskNamespace.STD).value
        task_id, _ = _next_task_seq(ns)
    kwargs: dict[str, Any] = {
        "task_id": task_id,
        "namespace": namespace or TaskNamespace.STD,
        "seq": seq,
        "title": title,
        "phase": phase,
        "execution_model": normalize_execution_model(execution_model),
        "safety_level": safety_level,
        "created_at": created_at or now,
        "updated_at": updated_at or now,
        "description": description,
    }
    kwargs["status"] = status
    kwargs["priority"] = priority
    kwargs.update(overrides)
    return Task(**kwargs)


def make_p0_task(**overrides: Any) -> Task:
    """构造 P0 + H 安全等级的紧急任务。"""
    return make_valid_task(
        title="P0 urgent task",
        priority=Priority.P0,
        safety_level=SafetyLevel.H,
        **overrides,
    )


def make_completed_task(**overrides: Any) -> Task:
    """构造 COMPLETED 状态的任务（completed_at 自动填当前时间）。"""
    now = _utc_now()
    return make_valid_task(
        title="Completed task",
        status=TaskStatus.COMPLETED,
        completed_at=now,
        **overrides,
    )


_audit_counter = 0


def _next_audit_id() -> str:
    global _audit_counter
    with _counter_lock:
        _audit_counter += 1
        seq = _audit_counter
    return f"AUDIT-{seq:03d}"


def make_valid_audit_report(
    *,
    report_id: str | None = None,
    scanner: str = "factory-scanner",
    scan_target: str = "tests/factory-scan-target/",
    findings: list[AuditFinding] | None = None,
    **overrides: Any,
) -> AuditReport:
    """构造 valid-by-construction 的 AuditReport 实例。

    findings 默认生成一条 P2 的示例 AuditFinding。
    """
    if findings is None:
        findings = [
            AuditFinding(
                finding_id=f"F-{_audit_counter:03d}-01",
                severity=AuditSeverity.P2,
                description="Factory-generated audit finding.",
            )
        ]
    kwargs: dict[str, Any] = {
        "report_id": report_id or _next_audit_id(),
        "scanner": scanner,
        "scan_target": scan_target,
        "findings": findings,
        "created_at": _utc_now(),
    }
    kwargs.update(overrides)
    return AuditReport(**kwargs)


_ke_counter = 0


def _next_ke_id() -> str:
    global _ke_counter
    with _counter_lock:
        _ke_counter += 1
        seq = _ke_counter
    return f"KE-{seq:03d}"


def make_valid_knowledge_entry(
    *,
    ke_id: str | None = None,
    title: str = "Factory-generated knowledge entry",
    category: KeCategory = KeCategory.best_practice,
    **overrides: Any,
) -> KnowledgeEntry:
    """构造 valid-by-construction 的 KnowledgeEntry 实例。"""
    now = _utc_now()
    kwargs: dict[str, Any] = {
        "ke_id": ke_id or _next_ke_id(),
        "title": title,
        "category": category,
        "source_file": "docs/factory-generated-source.md",
        "created_at": now,
        "updated_at": now,
    }
    kwargs.update(overrides)
    return KnowledgeEntry(**kwargs)


_pattern_counter = 0


def _next_pattern_id() -> str:
    global _pattern_counter
    with _counter_lock:
        _pattern_counter += 1
        seq = _pattern_counter
    return f"F-{seq:03d}"


def make_valid_failure_pattern(
    *,
    pattern_id: str | None = None,
    failure_type: FailureType = FailureType.VALIDATION,
    title: str = "Factory-generated failure pattern",
    description: str = "A factory-generated failure pattern for testing.",
    reproduction_steps: list[str] | None = None,
    **overrides: Any,
) -> FailurePattern:
    """构造 valid-by-construction 的 FailurePattern 实例。"""
    now = _utc_now()
    kwargs: dict[str, Any] = {
        "pattern_id": pattern_id or _next_pattern_id(),
        "failure_type": failure_type,
        "title": title,
        "description": description,
        "reproduction_steps": reproduction_steps or ["Factory step 1 — reproduce"],
        "created_at": now,
        "updated_at": now,
    }
    kwargs.update(overrides)
    return FailurePattern(**kwargs)


def make_valid_handoff_package(
    *,
    session_id: str = "factory-session-001",
    context_summary: str = "Factory-generated context summary for handoff.",
    **overrides: Any,
) -> HandoffPackage:
    """构造 valid-by-construction 的 HandoffPackage 实例。"""
    now = _utc_now()
    kwargs: dict[str, Any] = {
        "session_id": session_id,
        "context_summary": context_summary,
        "completed_tasks": [f"STD-{i:03d}" for i in range(1, 4)],
        "in_progress_tasks": [f"STD-{i:03d}" for i in range(4, 6)],
        "blocked_items": [
            BlockedItem(
                task_id="STD-006",
                reason="Factory-generated blocked item for testing.",
            )
        ],
        "decisions_made": [
            Decision(
                decision_id="DEC-001",
                summary="Factory decision — use default model for testing.",
                rationale="Sensible defaults reduce AI cognitive load.",
            )
        ],
        "next_actions": [
            NextAction(
                priority=1,
                action="Continue factory test with verified defaults.",
            )
        ],
        "open_questions": ["Are all factory defaults valid for this module?"],
        "created_at": now,
    }
    kwargs.update(overrides)
    return HandoffPackage(**kwargs)
