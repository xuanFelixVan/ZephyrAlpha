# [BLUEPRINT] MOD-INF-005 | scripts/construction/reset_test_task.py | §
# [MODULE] scripts.construction.reset_test_task
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
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
# [TTL] permanent
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "governance"))

from _shared.constants import DB_PATH  # noqa: E402
import sqlite3

from zephyr.shared.io.paths import DB_PATH

conn = sqlite3.connect(DB_PATH)
try:
    conn.execute("UPDATE tasks SET status = 'PENDING' WHERE task_id = 'OPS-007'")
    conn.commit()
finally:
    conn.close()
print("OPS-007 reset to PENDING")
