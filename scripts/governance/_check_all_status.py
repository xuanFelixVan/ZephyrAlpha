"""检查DM-201201和DM-201202的状态，了解它们如何成功transition."""
import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

DB_PATH = Path(__file__).parent.parent.parent / "data" / "databases" / "governance.db"


def main() -> int:
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        for task_id in ["DM-201201", "DM-201202", "DM-201203"]:
            row = conn.execute(
                "SELECT task_id, status, verification_status, construction_status FROM tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row:
                print(f"{task_id}: status={row['status']}, vs={row['verification_status']}, cs={row['construction_status']}")
            else:
                print(f"{task_id}: NOT FOUND")

        # 检查task_reviews表
        print("\n--- task_reviews ---")
        rows = conn.execute(
            "SELECT task_id, review_round, dimension, issue_count, passed FROM task_reviews WHERE task_id IN ('DM-201201','DM-201202','DM-201203') ORDER BY task_id, review_round, dimension",
        ).fetchall()
        for r in rows:
            print(f"  {r['task_id']} round={r['review_round']} dim={r['dimension']} issues={r['issue_count']} passed={r['passed']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
