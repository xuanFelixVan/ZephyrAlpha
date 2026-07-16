# [BLUEPRINT] MOD-INF-005 | scripts/construction/finalize_tasks.py | §
# [MODULE] scripts.construction.finalize_tasks
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.task_repo; zephyr.governance.persistence.sqlite_schema; zephyr.integration.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from zephyr.integration.schema.schemas import TaskStatus

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.governance.persistence.task_repo import TaskRepository

init_db()
repo = TaskRepository()


def safe_transition(tid: str, target: str) -> None:
    c = repo.get(tid)
    if c.status == TaskStatus(target):
        print(f"{tid}: already {target}")
        return
    repo.transition(tid, target)
    print(f"{tid}: -> {target}")


safe_transition("OPS-006", "COMPLETED")
safe_transition("OPS-007", "COMPLETED")

safe_transition("OPS-008", "IN_PROGRESS")
safe_transition("OPS-008", "COMPLETED")

safe_transition("OPS-009", "IN_PROGRESS")
safe_transition("OPS-009", "COMPLETED")

print()
for tid in ["OPS-001", "OPS-002", "OPS-003", "OPS-004", "OPS-005", "OPS-006", "OPS-007", "OPS-008", "OPS-009"]:
    c = repo.get(tid)
    print(f"  {tid}: {c.status.value}")

all_done = all(
    repo.get(tid).status.value == "COMPLETED"
    for tid in ["OPS-001", "OPS-002", "OPS-003", "OPS-004", "OPS-005", "OPS-006", "OPS-007", "OPS-008", "OPS-009"]
)
print(f"\nAll COMPLETED: {all_done}")
