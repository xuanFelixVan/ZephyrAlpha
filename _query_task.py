"""查询任务卡详情。"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(r"d:\ZephyrAlpha\data\databases\governance.db")

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 查询任务详情
cur.execute("SELECT * FROM tasks WHERE task_id = ?", ("OPS-2026062108",))
row = cur.fetchone()

if row is None:
    print("[FAIL] 任务不存在")
    # 列出所有OPS任务
    cur.execute("SELECT task_id, status, title FROM tasks WHERE task_id LIKE 'OPS-%' ORDER BY task_id")
    rows = cur.fetchall()
    print(f"\n所有OPS任务 ({len(rows)} 个):")
    for r in rows:
        print(f"  {r['task_id']} | {r['status']} | {r['title'][:80]}")
else:
    # 打印所有字段
    for key in row.keys():
        value = row[key]
        if value and len(str(value)) > 200:
            print(f"{key}: {str(value)[:200]}...")
        else:
            print(f"{key}: {value}")

conn.close()
