"""查询 OPS-2026062106 任务详情和 N-06 违规清单"""
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(r"d:\ZephyrAlpha")
DB_PATH = REPO_ROOT / "data" / "databases" / "governance.db"

# 1. 查询任务详情
print("=" * 70)
print("任务详情: OPS-2026062106")
print("=" * 70)
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()
cursor.execute("SELECT task_id, title, description, status, files_in_scope, deliverables, allowed_touch, acceptance FROM tasks WHERE task_id = ?", ("OPS-2026062106",))
row = cursor.fetchone()
if row:
    print(f"task_id: {row[0]}")
    print(f"title: {row[1]}")
    print(f"description: {row[2]}")
    print(f"status: {row[3]}")
    print(f"files_in_scope: {row[4]}")
    print(f"deliverables: {row[5]}")
    print(f"allowed_touch: {row[6]}")
    print(f"acceptance: {row[7]}")
else:
    print("未找到任务")
conn.close()

# 2. 获取 N-06 违规清单
print("\n" + "=" * 70)
print("N-06 违规清单")
print("=" * 70)
check_script = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"
result = subprocess.run(
    [sys.executable, str(check_script), "--scan", "--warn-only"],
    capture_output=True,
    cwd=str(REPO_ROOT),
    timeout=300,
)
output = result.stdout.decode("utf-8", errors="replace")
n06_violations = []
for line in output.splitlines():
    if "N-06" in line:
        n06_violations.append(line.strip())
print(f"N-06 违规总数: {len(n06_violations)}")
print("-" * 70)
for v in n06_violations[:50]:  # 只显示前50个
    print(v)
if len(n06_violations) > 50:
    print(f"... 还有 {len(n06_violations) - 50} 个违规")
