# [BLUEPRINT] MOD-INF-005 | scripts/construction/check_transition_code.py | §
# [MODULE] scripts.construction.check_transition_code
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.task_repo
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
