# [BLUEPRINT]
# [MODULE] scripts.governance._check_task
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
"""查看DM-201203任务卡的post_sync_standard和acceptance."""
import sys
sys.path.insert(0, "src")

from zephyr.governance.task_repo import TaskRepository

repo = TaskRepository()
task = repo.get("DM-201203")
print(f"task_id={task.task_id}")
print(f"verification_status={task.verification_status}")
print(f"acceptance={task.acceptance}")
print(f"post_sync_standard={task.post_sync_standard}")
print(f"rollback_instructions={task.rollback_instructions[:200] if task.rollback_instructions else 'N/A'}")
repo.close()
