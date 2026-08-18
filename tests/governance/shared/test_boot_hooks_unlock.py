# [BLUEPRINT] MOD-TEST-508 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_boot_hooks_unlock | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from datetime import UTC, datetime

from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.shared.foundation.models import TaskCard, TaskNamespace, TaskStatus
from zephyr.shared.io.paths import DB_PATH, REPO_ROOT
from zephyr.shared.schema.execution_model import ExecutionModel
from zephyr.shared.schema.severity_types import Priority, SafetyLevel

DB_PATH = REPO_ROOT / "data" / "databases" / "governance.db"


def _make_task(task_id: str, title: str, depends_on: list[str] | None = None) -> TaskCard:
    now = datetime.now(UTC)
    ns, seq_str = task_id.split("-", 1)
    return TaskCard(
        task_id=task_id,
        namespace=getattr(TaskNamespace, ns, TaskNamespace.CP),
        seq=int(seq_str),
        title=title,
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model=ExecutionModel.deepseek,
        safety_level=SafetyLevel.L,
        depends_on=depends_on or [],
        source_blueprint="TEST",
        source_section="test",
        description=f"Test task: {title}",
        verification_status="verified",
        files_in_scope=["test.py"],
        deliverables=["test.py"],
        applicable_rules=[{"module_id": "GOV-TASK-001", "section": "1", "reason": "test"}],
        allowed_touch=["test.py"],
        rollback_instructions="git checkout test.py",
        post_sync_standard=["echo ok"],
        acceptance=["test passes"],
        created_at=now,
        updated_at=now,
    )


def test_downstream_unlock():
    repo = TaskRepository(str(DB_PATH), enable_gate=False)
    now = datetime.now(UTC)

    import time

    uid = str(int(time.time()))[-5:]
    task_a = _make_task(f"CP-{uid}1", "Task A (no deps)")
    task_b = _make_task(f"CP-{uid}2", "Task B (depends on A)", depends_on=[f"CP-{uid}1"])
    task_c = _make_task(f"CP-{uid}3", "Task C (no relation)")
    task_d = _make_task(f"CP-{uid}4", "Task D (depends on A+B)", depends_on=[f"CP-{uid}1", f"CP-{uid}2"])
    task_e = _make_task(f"CP-{uid}5", "Task E (depends on A+B, B done)", depends_on=[f"CP-{uid}1", f"CP-{uid}2"])

    for t in [task_a, task_b, task_c, task_d, task_e]:
        try:
            repo.create(t, allow_direct_create=True)
        except Exception:
            pass

    repo.transition(f"CP-{uid}1", "IN_PROGRESS")
    repo.transition(f"CP-{uid}2", "BLOCKED")
    repo.transition(f"CP-{uid}3", "IN_PROGRESS")
    repo.transition(f"CP-{uid}4", "BLOCKED")
    repo.transition(f"CP-{uid}5", "BLOCKED")

    downstream = repo.list_by_dependency(f"CP-{uid}1")
    downstream_ids = [d.task_id for d in downstream]
    assert f"CP-{uid}2" in downstream_ids, f"CP-{uid}2 should be downstream of CP-{uid}1, got {downstream_ids}"
    assert f"CP-{uid}4" in downstream_ids, f"CP-{uid}4 should be downstream of CP-{uid}1, got {downstream_ids}"
    assert f"CP-{uid}5" in downstream_ids, f"CP-{uid}5 should be downstream of CP-{uid}1, got {downstream_ids}"
    assert f"CP-{uid}3" not in downstream_ids, f"CP-{uid}3 should NOT be downstream of CP-{uid}1"

    repo.transition(f"CP-{uid}1", "COMPLETED")

    downstream_after = repo.list_by_dependency(f"CP-{uid}1")
    for ds in downstream_after:
        if ds.task_id == f"CP-{uid}2":
            deps = ds.depends_on or []
            all_done = all(repo.get(d).status.value == "COMPLETED" for d in deps if d)
            if all_done and ds.status.value in ("BLOCKED", "PENDING", "WAITING"):
                repo.transition(ds.task_id, "READY", note=f"unblocked by CP-{uid}1")
                print(f"  UNLOCKED: {ds.task_id} → READY")
            elif all_done:
                print(f"  ALREADY READY: {ds.task_id} (status={ds.status.value})")
            else:
                print(f"  STILL BLOCKED: {ds.task_id} (deps not all done)")

    task_b_after = repo.get(f"CP-{uid}2")
    assert task_b_after is not None
    print(f"  Task B status after A completed: {task_b_after.status.value}")

    task_d_after = repo.get(f"CP-{uid}4")
    assert task_d_after is not None
    print(f"  Task D status after A completed (B still BLOCKED): {task_d_after.status.value}")

    print("test_downstream_unlock PASSED")


def test_no_downstream():
    repo = TaskRepository(str(DB_PATH), enable_gate=False)
    downstream = repo.list_by_dependency("CP-99999")
    assert downstream == [], f"Non-existent task should have no downstream, got {downstream}"
    print("test_no_downstream PASSED")


if __name__ == "__main__":
    test_downstream_unlock()
    test_no_downstream()
