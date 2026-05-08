"""
durable_execution.py —— AI 长流程 Durable Execution（Phase 13 | 盲点 B30）

痛点修复：长流程 AI task 可能运行数小时——进程崩溃后从头重跑浪费已消耗 token。
需要 Worker/Activity 抽象层、进度快照、断点恢复。

设计对标：
  - Temporal.io: Activity/Workflow 抽象 + 事件溯源 + 重放机制
  - PydanticAI Durable Execution: 可恢复 Agent 执行流
  - AWS Step Functions: 状态机持久化

核心抽象：
  - Activity Protocol → execute() + checkpoint() + resume()
  - WorkflowManager → 编排多个 Activity，保存进度快照
  - 进程崩溃后 resume() 可从最近快照恢复，不重复执行已完成 Activity

SSoT: MOD-INF-016 §12 盲点 B30
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum, unique
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@unique
class ActivityStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ActivityResult:
    """单次 Activity 执行结果。"""

    activity_name: str
    status: ActivityStatus
    output: Any = None
    error: str | None = None
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str | None = None
    retry_count: int = 0


@dataclass
class ProgressSnapshot:
    """执行进度快照——可序列化到磁盘用于断点恢复。"""

    workflow_id: str
    completed_activities: list[str] = field(default_factory=list)
    current_activity: str | None = None
    activity_results: dict[str, ActivityResult] = field(default_factory=dict)
    global_state: dict[str, Any] = field(default_factory=dict)
    snapshot_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    version: int = 1


@runtime_checkable
class Activity(Protocol):
    """Activity 协议——任何可持久化执行的 AI 操作单元。

    每个 Activity 必须是幂等的：resume() 时可能重放。
    """

    @property
    def name(self) -> str: ...

    def execute(self, context: dict[str, Any]) -> dict[str, Any]: ...

    async def execute_async(self, context: dict[str, Any]) -> dict[str, Any]:
        ...

    def checkpoint_data(self) -> dict[str, Any]: ...

    def resume(self, checkpoint: dict[str, Any]) -> None: ...


@dataclass
class SimpleActivity:
    """简单 Activity 实现——包装一个同步可调用对象。"""

    _name: str
    _fn: Any

    @property
    def name(self) -> str:
        return self._name

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return self._fn(context)

    async def execute_async(self, context: dict[str, Any]) -> dict[str, Any]:
        return self._fn(context)

    def checkpoint_data(self) -> dict[str, Any]:
        return {"name": self._name}

    def resume(self, checkpoint: dict[str, Any]) -> None:
        pass


@dataclass
class WorkflowManager:
    """工作流编排器——管理多个 Activity 的执行流程与进度持久化。

    Usage::

        manager = WorkflowManager(workflow_id="build-knowledge-graph")
        manager.add_activity(my_parse_activity)
        manager.add_activity(my_index_activity)

        try:
            manager.run({"input": "docs/"})
        except Exception:
            manager.save_snapshot()

        # 恢复
        manager2 = WorkflowManager(workflow_id="build-knowledge-graph")
        manager2.load_snapshot()
        manager2.resume()

    Attributes:
        workflow_id: 工作流唯一标识。
        snapshot_dir: 快照存储目录。
    """

    workflow_id: str
    snapshot_dir: str = "logs/workflow_snapshots/"

    activities: list[Activity] = field(default_factory=list)
    _current_index: int = field(default=0, init=False)
    _results: dict[str, ActivityResult] = field(default_factory=dict, init=False)
    _lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)

    def __post_init__(self) -> None:
        Path(self.snapshot_dir).mkdir(parents=True, exist_ok=True)

    def add_activity(self, activity: Activity) -> None:
        self.activities.append(activity)

    def add_activities(self, activities: list[Activity]) -> None:
        self.activities.extend(activities)

    @property
    def completed_activities(self) -> list[str]:
        with self._lock:
            return [
                name
                for name, r in self._results.items()
                if r.status == ActivityStatus.COMPLETED
            ]

    @property
    def pending_activities(self) -> list[str]:
        with self._lock:
            completed = set(self.completed_activities)
            return [a.name for a in self.activities if a.name not in completed]

    @property
    def progress(self) -> float:
        if not self.activities:
            return 0.0
        with self._lock:
            return len(self.completed_activities) / len(self.activities)

    def run(self, context: dict[str, Any]) -> dict[str, ActivityResult]:
        """从头执行所有 Activity。"""
        results: dict[str, ActivityResult] = {}
        with self._lock:
            self._current_index = 0

        for i, activity in enumerate(self.activities):
            with self._lock:
                self._current_index = i

            result = self._execute_activity(activity, context)
            results[activity.name] = result

            with self._lock:
                self._results[activity.name] = result

            if result.status == ActivityStatus.FAILED:
                break

        return results

    def resume(self, context: dict[str, Any] | None = None) -> dict[str, ActivityResult]:
        """从快照恢复执行——跳过已完成 Activity，从断点继续。"""
        if context is None:
            context = {}

        snapshot = self.load_snapshot()
        if snapshot is None:
            return self.run(context)

        with self._lock:
            self._results = dict(snapshot.activity_results)
            completed = set(snapshot.completed_activities)

        results: dict[str, ActivityResult] = {}
        for i, activity in enumerate(self.activities):
            if activity.name in completed:
                results[activity.name] = self._results.get(
                    activity.name,
                    ActivityResult(
                        activity_name=activity.name,
                        status=ActivityStatus.COMPLETED,
                    ),
                )
                continue

            with self._lock:
                self._current_index = i

            result = self._execute_activity(activity, context)
            results[activity.name] = result

            with self._lock:
                self._results[activity.name] = result

            if result.status == ActivityStatus.FAILED:
                break

        return results

    def _execute_activity(
        self, activity: Activity, context: dict[str, Any]
    ) -> ActivityResult:
        try:
            output = activity.execute(context)
            return ActivityResult(
                activity_name=activity.name,
                status=ActivityStatus.COMPLETED,
                output=output,
                completed_at=datetime.now(UTC).isoformat(),
            )
        except Exception as e:
            return ActivityResult(
                activity_name=activity.name,
                status=ActivityStatus.FAILED,
                error=str(e),
                completed_at=datetime.now(UTC).isoformat(),
            )

    def save_snapshot(self) -> ProgressSnapshot:
        """保存当前进度到磁盘。"""
        snapshot = ProgressSnapshot(
            workflow_id=self.workflow_id,
            completed_activities=self.completed_activities,
            current_activity=(
                self.activities[self._current_index].name
                if self._current_index < len(self.activities)
                else None
            ),
            activity_results=dict(self._results),
        )

        snapshot_data = asdict(snapshot)
        snapshot_data["activity_results"] = {
            name: asdict(r) for name, r in self._results.items()
        }

        filepath = Path(self.snapshot_dir) / f"{self.workflow_id}.snapshot.json"
        tmp_path = f"{filepath}.{os.getpid()}.tmp"
        with self._lock:
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
                os.replace(tmp_path, str(filepath))
            except PermissionError:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

        return snapshot

    def load_snapshot(self) -> ProgressSnapshot | None:
        """从磁盘加载进度快照。"""
        filepath = Path(self.snapshot_dir) / f"{self.workflow_id}.snapshot.json"
        if not filepath.exists():
            return None

        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            results_raw = data.pop("activity_results", {})
            activity_results: dict[str, ActivityResult] = {}
            for name, r in results_raw.items():
                activity_results[name] = ActivityResult(**r)

            return ProgressSnapshot(
                workflow_id=data.get("workflow_id", self.workflow_id),
                completed_activities=data.get("completed_activities", []),
                current_activity=data.get("current_activity"),
                activity_results=activity_results,
                global_state=data.get("global_state", {}),
                snapshot_at=data.get("snapshot_at", ""),
                version=data.get("version", 1),
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def get_result(self, activity_name: str) -> ActivityResult | None:
        with self._lock:
            return self._results.get(activity_name)

    def reset(self) -> None:
        with self._lock:
            self._current_index = 0
            self._results.clear()

        filepath = Path(self.snapshot_dir) / f"{self.workflow_id}.snapshot.json"
        if filepath.exists():
            filepath.unlink()


__all__ = [
    "ActivityStatus",
    "ActivityResult",
    "ProgressSnapshot",
    "Activity",
    "SimpleActivity",
    "WorkflowManager",
]
