# [BLUEPRINT] MOD-INF-005 | scripts/construction/reset_test_task.py | §
import sys

sys.path.insert(0, r"d:\ZephyrAlpha\src")
import sqlite3

from zephyr.governance.persistence.sqlite_schema import DB_PATH

conn = sqlite3.connect(DB_PATH)
conn.execute("UPDATE tasks SET status = 'PENDING' WHERE task_id = 'OPS-007'")
conn.commit()
conn.close()
print("OPS-007 reset to PENDING")
