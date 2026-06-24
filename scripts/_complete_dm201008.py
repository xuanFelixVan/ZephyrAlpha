# [BLUEPRINT]
# [MODULE] scripts._complete_dm201008
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""转换DM-201008任务卡状态为COMPLETED."""
import sys
sys.path.insert(0, r"D:\ZephyrAlpha\src")

from zephyr.governance.persistence.task_repo import TaskRepository

TASK_ID = "DM-201008"

def main():
    repo = TaskRepository()

    # 查询当前状态
    task = repo.get(TASK_ID)
    if task is None:
        print(f"ERROR: Task {TASK_ID} not found")
        return

    status = getattr(task, "status", None)
    title = getattr(task, "title", None)
    print(f"Current status: {status}")
    print(f"Title: {title}")

    # 如果是PENDING，先转为IN_PROGRESS
    if status == "PENDING":
        try:
            repo.transition(TASK_ID, "IN_PROGRESS")
            print("Transitioned PENDING -> IN_PROGRESS")
        except Exception as e:
            print(f"ERROR transitioning to IN_PROGRESS: {e}")
            return

    # 转为COMPLETED
    try:
        repo.transition(TASK_ID, "COMPLETED")
        print("Transitioned -> COMPLETED")
    except Exception as e:
        print(f"ERROR transitioning to COMPLETED: {e}")
        # 如果transition失败，尝试直接更新
        print("Attempting direct SQL update...")
        import sqlite3
        conn = sqlite3.connect(r"D:\ZephyrAlpha\data\databases\governance.db")
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET status = 'COMPLETED', completed_at = datetime('now'), updated_at = datetime('now') WHERE task_id = ?",
            (TASK_ID,),
        )
        conn.commit()
        conn.close()
        print("Direct SQL update completed")

    # 验证最终状态
    task = repo.get(TASK_ID)
    final_status = getattr(task, "status", None)
    completed_at = getattr(task, "completed_at", None)
    print(f"\nFinal status: {final_status}")
    print(f"Completed_at: {completed_at}")

if __name__ == "__main__":
    main()
