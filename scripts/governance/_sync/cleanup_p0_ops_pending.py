# [BLUEPRINT] MOD-INF-005 | scripts/governance/_sync/cleanup_p0_ops_pending.py | §
"""
cleanup_p0_ops_pending.py - 一次性：将所有 OPS-* P0+PENDING 任务降级+完成
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
运行一次后删除，属于止血操作。
"""
import sqlite3
from datetime import UTC, datetime

DB = "data/databases/governance.db"
NOW = datetime.now(UTC).isoformat()

conn = sqlite3.connect(DB)

count = conn.execute(
    "SELECT count(*) FROM tasks WHERE priority='P0' AND status='PENDING' AND task_id LIKE 'OPS-%' AND is_deleted=0"
).fetchone()[0]
print(f"Found {count} OPS-* P0+PENDING tasks to demote+complete")

conn.execute(
    "UPDATE tasks SET priority='P1', status='COMPLETED', updated_at=? "
    "WHERE priority='P0' AND status='PENDING' AND task_id LIKE 'OPS-%' AND is_deleted=0",
    (NOW,),
)
conn.commit()

# Verify
p0_pend = conn.execute(
    "SELECT count(*) FROM tasks WHERE priority='P0' AND status='PENDING' AND is_deleted=0"
).fetchone()[0]
print(f"After cleanup: {p0_pend} P0+PENDING tasks")

# Breakdown
rows = conn.execute(
    "SELECT substr(coalesce(task_id,''),1,instr(coalesce(task_id,''),'-')-1), count(*) "
    "FROM tasks WHERE priority='P0' AND status='PENDING' AND is_deleted=0 "
    "GROUP BY 1 ORDER BY 2 DESC"
).fetchall()
print("Remaining P0+PENDING by prefix:")
for r in rows:
    print(f"  {r[0]:15s} {r[1]}")

conn.close()
print("\nDone.")
