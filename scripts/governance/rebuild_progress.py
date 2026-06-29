# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.rebuild_progress
# [DOMAIN] D_GOVERNANCE
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
[BLUEPRINT] MOD-ARCH-002 | scripts/governance/rebuild_progress.py | §9.3
[MODULE] 无（独立脚本）
[INVARIANTS] 仅查询不修改; 进度真源为governance.db任务卡表
[MODIFY-GUARD] 只读脚本，无修改
[CONSUMERS] autopilot session-20260618-001; §9.3进度检查点
[STABILITY] stable
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] DB不存在→exit 1; 查询异常→exit 1; 成功→exit 0
[TESTS] 执行后验证输出包含进度摘要

P1-2 从任务卡DB重建进度文件
根因：§9.3要求进度重建脚本，原脚本缺失
治根：从governance.db查询任务卡状态生成进度摘要

说明：本脚本从DB生成实时摘要，governance.db任务卡表为权威记录。
"""

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，通过 _shared.constants 获取 PG 连接。
# governance.db 仍为 SQLite（task_repo.py 等仍使用 sqlite3.connect）。
# DB_PATH 真源为 _shared.constants（re-export 自 zephyr.shared.io.paths.REPO_ROOT）。
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection, DB_PATH  # noqa: E402


def main():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] governance.db不存在: {DB_PATH}")
        return 1

    print("=" * 80)
    print("ZephyrAlpha 依赖全景图系统 - 施工进度摘要（实时从DB生成）")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    try:
        conn = sqlite3.connect(DB_PATH)

        phase0_rows = conn.execute(
            "SELECT task_id, status, title FROM tasks "
            "WHERE task_id LIKE 'DM-200%' OR task_id LIKE 'MIG-%' "
            "ORDER BY task_id"
        ).fetchall()

        status_counts = {}
        for _, status, _ in phase0_rows:
            status_counts[status] = status_counts.get(status, 0) + 1

        print(f"\n[Phase 0 任务卡] 共{len(phase0_rows)}张")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")

        conn.close()
    except sqlite3.Error as e:
        print(f"[ERROR] 查询governance.db失败: {e}")
        return 1

    # P2迁移后：depgraph 已迁移到 PostgreSQL（governance.db 仍为 SQLite，上面已查询）
    try:
        dconn = get_depgraph_pg_connection(autocommit=True)
        node_count = dconn.execute("SELECT COUNT(*) AS cnt FROM nodes").fetchone()["cnt"]
        edge_count = dconn.execute("SELECT COUNT(*) AS cnt FROM edges").fetchone()["cnt"]
        design_nodes = dconn.execute(
            "SELECT COUNT(*) AS cnt FROM nodes WHERE design_maturity='design'"
        ).fetchone()["cnt"]
        dconn.close()
        print("\n[depgraph.db 状态]")
        print(f"  节点总数: {node_count}")
        print(f"  边总数: {edge_count}")
        print(f"  设计态节点: {design_nodes}")
    except Exception as e:
        print(f"[WARN] 查询depgraph(PG)失败: {e}")

    print("\n" + "=" * 80)
    completed = status_counts.get("COMPLETED", 0)
    print(f"[结论] Phase 0: {completed}/{len(phase0_rows)} COMPLETED")
    print("[PASS] 进度摘要生成完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
