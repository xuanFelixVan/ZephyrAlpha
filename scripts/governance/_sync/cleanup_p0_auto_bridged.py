# [BLUEPRINT] MOD-INF-005 | scripts/governance/_sync/cleanup_p0_auto_bridged.py | §
# [MODULE] scripts.governance._sync.cleanup_p0_auto_bridged
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
清理历史 P0 自动桥接任务
"""

__manifest__ = """
args: []
description: >
  一次性：清理历史 P0 自动桥接任务（tags 含 auto-bridged 的 PENDING→P1+COMPLETED）。
  运行后删除，属止血操作。
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


"""
将所有 tags 含 'auto-bridged' 的 PENDING 任务：
1. 优先级 P0 -> P1（自动桥接 Finding 不代表 P0 紧急度）
2. 状态 PENDING -> COMPLETED（系统已记录此发现，不阻塞人工队列）
"""

import sqlite3
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import DB_PATH  # noqa: E402


def main() -> int:
    if not DB_PATH.exists():
        print(f"[ERROR] DB 不存在: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute("PRAGMA journal_mode=WAL")

        cur = conn.execute(
            "SELECT priority, status, count(1) FROM tasks "
            "WHERE tags LIKE '%auto-bridged%' "
            "AND status = 'PENDING' "
            "AND is_deleted = 0 "
            "GROUP BY priority, status"
        )
        report = cur.fetchall()
        print("当前 PENDING auto-bridged 任务:")
        total = 0
        for pri, st, cnt in report:
            print(f"  {pri}/{st}: {cnt}")
            total += cnt
        print(f"  总计: {total}")

        if total == 0:
            print("DB is clean.")
            return 0

        downgraded = conn.execute(
            "UPDATE tasks SET priority = 'P1' "
            "WHERE tags LIKE '%auto-bridged%' "
            "AND priority = 'P0' "
            "AND status = 'PENDING' "
            "AND is_deleted = 0"
        ).rowcount

        now = conn.execute("SELECT datetime('now')").fetchone()[0]
        closed = conn.execute(
            "UPDATE tasks SET status = 'COMPLETED', updated_at = ? "
            "WHERE tags LIKE '%auto-bridged%' "
            "AND status = 'PENDING' "
            "AND is_deleted = 0",
            (now,),
        ).rowcount

        conn.commit()

        print("\n已完成:")
        print(f"  P0→P1 降级: {downgraded}")
        print(f"  PENDING→COMPLETED: {closed}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
