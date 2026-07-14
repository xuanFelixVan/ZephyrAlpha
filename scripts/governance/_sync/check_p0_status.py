# [BLUEPRINT] MOD-INF-005 | scripts/governance/_sync/check_p0_status.py | §
# [MODULE] scripts.governance._sync.check_p0_status
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._sync.cleanup_p0_auto_bridged
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
# [TTL] task_bound
__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""

import sqlite3
import sys
from pathlib import Path

_GOV_DIR = str(Path(__file__).resolve().parents[1])
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import DB_PATH  # noqa: E402

conn = sqlite3.connect(str(DB_PATH))
try:
    cur = conn.execute(
        "SELECT status, count(1) FROM tasks WHERE tags LIKE '%auto-bridged%' AND priority='P0' AND is_deleted=0 GROUP BY status"
    )
    print("auto-bridged P0 by status:")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]}")
    cur2 = conn.execute(
        "SELECT priority, status, count(1) FROM tasks WHERE tags LIKE '%auto-bridged%' AND is_deleted=0 GROUP BY priority, status"
    )
    print("\nauto-bridged (all priorities) by status:")
    for r in cur2.fetchall():
        print(f"  {r[0]}/{r[1]}: {r[2]}")
finally:
    conn.close()
