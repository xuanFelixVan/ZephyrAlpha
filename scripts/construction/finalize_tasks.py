# [BLUEPRINT] MOD-INF-005 | scripts/construction/finalize_tasks.py | §
import sys
sys.path.insert(0, r"d:\ZephyrAlpha\src")
from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.integration.schema.schemas import TaskStatus

init_db()
repo = TaskRepository()

def safe_transition(tid, target):
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
for tid in ["OPS-001","OPS-002","OPS-003","OPS-004","OPS-005",
            "OPS-006","OPS-007","OPS-008","OPS-009"]:
    c = repo.get(tid)
    print(f"  {tid}: {c.status.value}")

all_done = all(repo.get(tid).status.value == "COMPLETED"
               for tid in ["OPS-001","OPS-002","OPS-003","OPS-004","OPS-005",
                           "OPS-006","OPS-007","OPS-008","OPS-009"])
print(f"\nAll COMPLETED: {all_done}")
