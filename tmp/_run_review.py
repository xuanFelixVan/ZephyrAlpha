"""临时: 运行batch_review + verify + transition"""
import sys
from zephyr.governance.persistence.task_repo import TaskRepository, TaskStatus

task_id = sys.argv[1]
session_id = sys.argv[2] if len(sys.argv) > 2 else None
repo = TaskRepository()

# Round 1
r1 = repo.batch_review(task_id, reviewer="ai", session_id=session_id)
print(f"Round 1: total_issues={r1['total_issues']} consecutive_zero={r1['consecutive_zero']} passed={r1['passed']}")
for d, v in r1['dimensions'].items():
    if not v['passed']:
        print(f"  FAIL {d}: {v['issues']}")

if r1['total_issues'] > 0:
    print("Round 1 has issues, aborting")
    sys.exit(1)

# Round 2
r2 = repo.batch_review(task_id, reviewer="ai", session_id=session_id)
print(f"Round 2: total_issues={r2['total_issues']} consecutive_zero={r2['consecutive_zero']} passed={r2['passed']}")
for d, v in r2['dimensions'].items():
    if not v['passed']:
        print(f"  FAIL {d}: {v['issues']}")

if r2['consecutive_zero'] >= 2:
    print("consecutive_zero >= 2, calling verify...")
    repo.verify(task_id, session_id=session_id)
    print("verified, transitioning to COMPLETED...")
    repo.transition(task_id, TaskStatus.COMPLETED)
    print(f"{task_id} -> COMPLETED")
else:
    print(f"consecutive_zero={r2['consecutive_zero']} < 2, NOT transitioning")
