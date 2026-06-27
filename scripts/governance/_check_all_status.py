# [BLUEPRINT]
# [MODULE] scripts.governance._check_all_status
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
# [TTL] task_bound
"""检查DM-201201和DM-201202的状态，了解它们如何成功transition."""
import sys
import sqlite3
from pathlib import Path

# 一次性 bootstrap：将 src/ 加入 sys.path（N 值对本文件固定且仅用一次，符合 project_memory 豁免）。
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# DB_PATH 真源为 zephyr.shared.io.paths（project_memory 钦定唯一真源）。
from zephyr.shared.io.paths import DB_PATH  # noqa: E402


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
