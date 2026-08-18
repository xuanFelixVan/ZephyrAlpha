"""已归档脚本——P2迁移后 depgraph.db 已迁移至 PostgreSQL，此脚本不再适用。"""
import sys

sys.exit("DEPRECATED: 此脚本已归档，depgraph.db 已迁移至 PostgreSQL 16")

"""检查dep_cycles视图并创建（如果不存在）。"""

import sqlite3

DB = r"D:\ZephyrAlpha\data\databases\depgraph.db"

conn = sqlite3.connect(DB)

# 检查现有视图
views = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()]
print(f"现有视图: {views}")

# 检查dep_cycles是否存在
if "dep_cycles" not in views:
    print("[INFO] dep_cycles视图不存在，创建中...")

    # 根据§14.9创建dep_cycles视图
    # 视图定义：检测循环依赖（自引用或互相依赖的节点对）
    conn.execute("""
    CREATE VIEW IF NOT EXISTS dep_cycles AS
    SELECT
        e1.from_node_id,
        e1.to_node_id,
        n1.path AS from_path,
        n2.path AS to_path,
        e1.dep_type
    FROM edges e1
    JOIN nodes n1 ON e1.from_node_id = n1.node_id
    JOIN nodes n2 ON e1.to_node_id = n2.node_id
    WHERE e1.from_node_id = e1.to_node_id
       OR EXISTS (
           SELECT 1 FROM edges e2
           WHERE e2.from_node_id = e1.to_node_id
             AND e2.to_node_id = e1.from_node_id
       )
    """)
    conn.commit()
    print("[OK] dep_cycles视图已创建")

# 验证视图有结果
count = conn.execute("SELECT COUNT(*) FROM dep_cycles").fetchone()[0]
print(f"dep_cycles行数: {count}")

if count > 0:
    print("[PASS] dep_cycles有结果")
else:
    print("[INFO] dep_cycles为空（无循环依赖）— 视图存在且可查询")

conn.close()
