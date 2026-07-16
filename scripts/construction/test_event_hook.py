# [BLUEPRINT] MOD-INF-005 | scripts/construction/test_event_hook.py | §
# [MODULE] scripts.construction.test_event_hook
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.integration.__init__; zephyr.governance.persistence.task_repo; zephyr.governance.persistence.sqlite_schema
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

from zephyr.integration.zephyr.event_hook import TransitionEvent, hook_registry

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.governance.persistence.task_repo import TaskRepository

init_db()

events = []


def log(event: TransitionEvent):
    events.append(event.task_id)
    print(f"Hook fired: {event.task_id} {event.from_status} -> {event.to_status}")


hook_registry.register(log, priority=1, name="test-logger")

repo = TaskRepository()

c = repo.get("OPS-007")
print(f"OPS-007 before: {c.status.value}")

repo.transition("OPS-007", "IN_PROGRESS")

print("Captured events:", events)
assert "OPS-007" in events, "Hook NOT fired!"

hook_registry.clear()
print("OPS-007: EventHook works!")
