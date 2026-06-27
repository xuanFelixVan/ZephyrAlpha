# [BLUEPRINT]
# [MODULE] scripts.governance._check_vs
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""查看已完成任务卡的verification_status."""
import sys
sys.path.insert(0, "src")

from zephyr.governance.task_repo import TaskRepository

repo = TaskRepository()
for tid in ["DM-201201", "DM-201202", "DM-201203"]:
    try:
        task = repo.get(tid)
        print(f"{tid}: status={task.status}, verification_status={task.verification_status}")
    except Exception as e:
        print(f"{tid}: ERROR {e}")
repo.close()
