# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.shared.resilience.durable_execution
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] tests
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_durable_execution.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: workflow_id 参数
#   fields: 参数 workflow_id（无注解）
#   code: durable_execution.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: snapshot_dir 参数
#   fields: 参数 snapshot_dir（无注解）
#   code: durable_execution.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① Activity
#   name_en: Activity
#   intro: class Activity 源码 L107-L112
#   desc: 公共方法（定义序）: execute, checkpoint_data, resume；源码 L107-L112
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② SimpleActivity
#   name_en: SimpleActivity
#   intro: class SimpleActivity 源码 L116-L127
#   desc: 公共方法（定义序）: execute, checkpoint_data, resume；源码 L116-L127
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ WorkflowManager
#   name_en: WorkflowManager
#   intro: class WorkflowManager 源码 L130-L277
#   desc: 公共方法（定义序）: activities, completed_activities, pending_activities, progress, add_activity, add_activities, run,…
#   inputs: workflow_id snapshot_dir
#   outputs: 返回值
#   （注：A3 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: Activity, SimpleActivity, WorkflowManager
#   downstream: tests
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

import json
import os
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from zephyr.shared.io.file_utils import atomic_write


class ActivityStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class ActivityResult:
    activity_name: str
    status: ActivityStatus
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class ProgressSnapshot:
    workflow_id: str
    completed_activities: list[str] = field(default_factory=list)
    current_activity: str = ""
    version: int = 1


@runtime_checkable
class Activity(Protocol):
    name: str

    def execute(self, ctx: dict[str, Any]) -> dict[str, Any]: ...
    def checkpoint_data(self) -> dict[str, Any]: ...
    def resume(self, data: dict[str, Any]) -> None: ...


@dataclass
class SimpleActivity:
    name: str
    _fn: Callable[[dict[str, Any]], dict[str, Any]] = field(repr=False)

    def execute(self, ctx: dict[str, Any]) -> dict[str, Any]:
        return self._fn(ctx)

    def checkpoint_data(self) -> dict[str, Any]:
        return {"name": self.name}

    def resume(self, data: dict[str, Any]) -> None:
        pass


class WorkflowManager:
    def __init__(self, workflow_id: str = "", snapshot_dir: str = "") -> None:
        self.workflow_id = workflow_id or str(uuid.uuid4())[:8]
        self._snapshot_dir = snapshot_dir
        self._activities: list[Activity] = []
        self._results: dict[str, ActivityResult] = {}
        self._completed_order: list[str] = []
        if snapshot_dir:
            os.makedirs(snapshot_dir, exist_ok=True)

    @property
    def activities(self) -> list[Activity]:
        return list(self._activities)

    @property
    def completed_activities(self) -> list[str]:
        return list(self._completed_order)

    @property
    def pending_activities(self) -> list[str]:
        completed = set(self._completed_order)
        return [
            a.name
            for a in self._activities
            if (a.name not in completed and a.name not in self._results)
            or self._results[a.name].status is not ActivityStatus.COMPLETED
        ]

    @property
    def progress(self) -> float:
        if not self._activities:
            return 0.0
        completed = sum(1 for r in self._results.values() if r.status is ActivityStatus.COMPLETED)
        return completed / len(self._activities)

    def add_activity(self, activity: Activity) -> None:
        self._activities.append(activity)

    def add_activities(self, activities: list[Activity]) -> None:
        for a in activities:
            self._activities.append(a)

    def run(self, ctx: dict[str, Any]) -> dict[str, ActivityResult]:
        for activity in self._activities:
            if activity.name in self._results and self._results[activity.name].status is ActivityStatus.COMPLETED:
                continue
            try:
                output = activity.execute(ctx)
                self._results[activity.name] = ActivityResult(
                    activity_name=activity.name,
                    status=ActivityStatus.COMPLETED,
                    output=output,
                )
                self._completed_order.append(activity.name)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._results[activity.name] = ActivityResult(
                    activity_name=activity.name,
                    status=ActivityStatus.FAILED,
                    error=str(exc),
                )
                break
        return dict(self._results)

    def save_snapshot(self) -> ProgressSnapshot | None:
        snapshot = ProgressSnapshot(
            workflow_id=self.workflow_id,
            completed_activities=list(self._completed_order),
            current_activity=self._completed_order[-1] if self._completed_order else "",
            version=1,
        )
        if not self._snapshot_dir:
            return snapshot
        data = {
            "workflow_id": self.workflow_id,
            "completed_activities": self._completed_order,
            "version": 1,
        }
        path = Path(self._snapshot_dir) / f"{self.workflow_id}.snapshot.json"
        try:
            # AI-15 审计治本（2026-08-17）：委托唯一真源 file_utils.atomic_write，
            # 消除本地 tmp+os.replace 重复实现。
            atomic_write(path, json.dumps(data, ensure_ascii=False))
        except OSError:  # 快照保存为 best-effort（load_snapshot 容忍缺失）；原子写失败静默跳过
            pass
        return snapshot

    def load_snapshot(self) -> ProgressSnapshot | None:
        if not self._snapshot_dir:
            return None
        path = Path(self._snapshot_dir) / f"{self.workflow_id}.snapshot.json"
        if not path.exists():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return ProgressSnapshot(
                workflow_id=data["workflow_id"],
                completed_activities=data.get("completed_activities", []),
                current_activity=data.get("current_activity", ""),
                version=data.get("version", 1),
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def resume(self, ctx: dict[str, Any]) -> dict[str, ActivityResult]:
        snapshot = self.load_snapshot()
        if snapshot is None:
            return self.run(ctx)
        for name in snapshot.completed_activities:
            if name not in self._completed_order:
                self._completed_order.append(name)
                self._results[name] = ActivityResult(
                    activity_name=name,
                    status=ActivityStatus.COMPLETED,
                )
        for activity in self._activities:
            if activity.name in self._completed_order:
                continue
            try:
                output = activity.execute(ctx)
                self._results[activity.name] = ActivityResult(
                    activity_name=activity.name,
                    status=ActivityStatus.COMPLETED,
                    output=output,
                )
                self._completed_order.append(activity.name)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._results[activity.name] = ActivityResult(
                    activity_name=activity.name,
                    status=ActivityStatus.FAILED,
                    error=str(exc),
                )
                break
        return dict(self._results)

    def get_result(self, activity_name: str) -> ActivityResult | None:
        return self._results.get(activity_name)

    def reset(self) -> None:
        self._results.clear()
        self._completed_order.clear()
        if self._snapshot_dir:
            path = Path(self._snapshot_dir) / f"{self.workflow_id}.snapshot.json"
            if path.exists():
                try:
                    path.unlink()
                except OSError:
                    pass


__all__ = [
    "Activity",
    "ActivityResult",
    "ActivityStatus",
    "ProgressSnapshot",
    "SimpleActivity",
    "WorkflowManager",
]
