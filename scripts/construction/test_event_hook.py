# [BLUEPRINT] MOD-INF-005 | scripts/construction/test_event_hook.py | §
import sys
sys.path.insert(0, r"d:\ZephyrAlpha\src")

from zephyr.hooks.event_hook import hook_registry, TransitionEvent
from zephyr.db.task_repo import TaskRepository
from zephyr.db.sqlite_schema import init_db

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
