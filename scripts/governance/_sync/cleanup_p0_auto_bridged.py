# [BLUEPRINT] MOD-INF-005 | scripts/governance/_sync/cleanup_p0_auto_bridged.py | §
# [MODULE] scripts.governance._sync.cleanup_p0_auto_bridged
# [DOMAIN] D-GOVERNANCE
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
description: [WARNING] __manifest__ 缺失, 请添加元数据块
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
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "databases" / "governance.db"


def main() -> int:
    if not DB_PATH.exists():
        print(f"[ERROR] DB 不存在: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
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
        conn.close()
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
    conn.close()

    print("\n已完成:")
    print(f"  P0→P1 降级: {downgraded}")
    print(f"  PENDING→COMPLETED: {closed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
