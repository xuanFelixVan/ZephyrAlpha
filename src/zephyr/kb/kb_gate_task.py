"""KB 五阶段门禁 evaluate 用的最小合法 Task（对齐 ADR-0040 / tasks 表）。"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.schemas import Task, TaskNamespace, TaskStatus, normalize_execution_model

# 与 KB 流水线文档任务链隔离的专用 seq，避免与真实 tasks 表主键碰撞概率
_GATE_SEQ: dict[str, tuple[TaskNamespace, int]] = {
    "G1": (TaskNamespace.ADR, 9101),
    "G2": (TaskNamespace.ADR, 9102),
    "G3": (TaskNamespace.ADR, 9103),
    "G4": (TaskNamespace.ADR, 9104),
    "G5": (TaskNamespace.ADR, 9105),
}


def build_kb_gate_eval_task(*, gate_id: str, title: str, deliverable: Path) -> Task:
    """构造 ``GateEngine.evaluate(task, gate_id)`` 所需的最小 Task。"""
    ns, seq = _GATE_SEQ[gate_id]
    now = datetime.now(UTC)
    return Task(
        task_id=f"{ns.value}-{seq}",
        namespace=ns,
        seq=seq,
        title=title,
        phase=2,
        status=TaskStatus.IN_PROGRESS,
        execution_model=normalize_execution_model("system"),
        safety_level="M",
        deliverables=[str(deliverable)],
        created_at=now,
        updated_at=now,
    )
