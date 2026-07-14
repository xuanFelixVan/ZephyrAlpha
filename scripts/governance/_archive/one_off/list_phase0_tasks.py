# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.list_phase0_tasks
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
[BLUEPRINT] MOD-ARCH-002 | scripts/governance/list_phase0_tasks.py | §1.11
[MODULE] 无（独立脚本）
[INVARIANTS] 仅查询不修改; 连接失败→exit 1
[MODIFY-GUARD] 只读脚本，无修改
[CONSUMERS] autopilot session-20260618-001; §1.11建卡验收
[STABILITY] stable
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] DB不存在→exit 1; 查询异常→exit 1; 成功→exit 0
[TESTS] 执行后验证输出包含38张任务卡

P1-2 列出所有Phase 0任务卡状态
根因：§1.11要求建卡验收脚本，原脚本缺失
治根：落盘查询脚本确保可验证Phase 0任务卡完整性
"""

import os
import sqlite3
import sys
from pathlib import Path

# DB_PATH 真源为 _shared.constants（re-export 自 zephyr.shared.io.paths.REPO_ROOT）。
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import DB_PATH  # noqa: E402


def main():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] 数据库不存在: {DB_PATH}")
        return 1

    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT task_id, status, title FROM tasks "
            "WHERE task_id LIKE 'DM-200%' OR task_id LIKE 'MIG-%' "
            "ORDER BY task_id"
        ).fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"[ERROR] 查询失败: {e}")
        return 1

    print(f"Phase 0 任务卡清单（共{len(rows)}张）")
    print("=" * 80)
    print(f"{'task_id':<15} {'status':<12} title")
    print("-" * 80)
    for task_id, status, title in rows:
        print(f"{task_id:<15} {status:<12} {title}")

    print("=" * 80)
    status_counts = {}
    for _, status, _ in rows:
        status_counts[status] = status_counts.get(status, 0) + 1
    print("状态统计:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    completed = status_counts.get("COMPLETED", 0)
    print(f"\n[INFO] COMPLETED: {completed}/{len(rows)}")

    if len(rows) == 0:
        print("[FAIL] 无Phase 0任务卡")
        return 1

    print("[PASS] Phase 0任务卡列表生成完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
