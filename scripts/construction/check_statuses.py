# [BLUEPRINT] MOD-INF-005 | scripts/construction/check_statuses.py | §
import sys

sys.path.insert(0, r"d:\ZephyrAlpha\src")
from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.governance.persistence.task_repo import TaskRepository

init_db()
repo = TaskRepository()

# OPS-006: was IN_PROGRESS from earlier test
# Reset to PENDING first so we can do proper PENDING->IN_PROGRESS->COMPLETED
# Actually we need to be more careful. Let me check statuses first.

for card_id in ["OPS-006", "OPS-007", "OPS-008", "OPS-009"]:
    c = repo.get(card_id)
    current = c.status.value
    print(f"{card_id}: {current}")
