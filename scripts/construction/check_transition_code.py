# [BLUEPRINT] MOD-INF-005 | scripts/construction/check_transition_code.py | §
import sys

sys.path.insert(0, r"d:\ZephyrAlpha\src")

import inspect

from zephyr.governance.persistence.task_repo import TaskRepository

src = inspect.getsource(TaskRepository.transition)
if "DEBUG" in src:
    print("transition HAS debug prints")
    for i, line in enumerate(src.splitlines(), 1):
        if "DEBUG" in line:
            print(f"  L{i}: {line.strip()}")
else:
    print("transition has NO debug prints! STALE CODE!")
    print(src[:500])
