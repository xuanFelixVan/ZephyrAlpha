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
# [A_module] module_id=MOD-INT_durable_execution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import json
import os
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


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
            or self._results[a.name].status != ActivityStatus.COMPLETED
        ]

    @property
    def progress(self) -> float:
        if not self._activities:
            return 0.0
        completed = sum(1 for r in self._results.values() if r.status == ActivityStatus.COMPLETED)
        return completed / len(self._activities)

    def add_activity(self, activity: Activity) -> None:
        self._activities.append(activity)

    def add_activities(self, activities: list[Activity]) -> None:
        for a in activities:
            self._activities.append(a)

    def run(self, ctx: dict[str, Any]) -> dict[str, ActivityResult]:
        for activity in self._activities:
            if activity.name in self._results and self._results[activity.name].status == ActivityStatus.COMPLETED:
                continue
            try:
                output = activity.execute(ctx)
                self._results[activity.name] = ActivityResult(
                    activity_name=activity.name,
                    status=ActivityStatus.COMPLETED,
                    output=output,
                )
                self._completed_order.append(activity.name)
            except Exception as exc:
                self._results[activity.name] = ActivityResult(
                    activity_name=activity.name,
                    status=ActivityStatus.FAILED,
                    error=str(exc),
                )
                break
        return dict(self._results)

    def save_snapshot(self) -> None:
        if not self._snapshot_dir:
            return
        data = {
            "workflow_id": self.workflow_id,
            "completed_activities": self._completed_order,
            "version": 1,
        }
        path = Path(self._snapshot_dir) / f"{self.workflow_id}.snapshot.json"
        tmp_path = f"{path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            os.replace(tmp_path, path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

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
            except Exception as exc:
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
