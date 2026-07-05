# [BLUEPRINT] MOD-INF-005 | scripts/governance/_sync/fix_orphan_deps.py | §
# [MODULE] scripts.governance._sync.fix_orphan_deps
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance._sync.check_p0_status
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
"""
fix_orphan_deps.py — 一次性修复孤儿依赖引用
=============================================
3类修复：
1. 范围记号展开: TASK-INF-0101~0130 → [INF-0101, INF-0102, ..., INF-0130]
2. 蓝图模块引用清除: MOD-MASTER_BLUEPRINT / MOD-INF-011 / MOD-LLM_SECURITY 不是 task_id
3. COMPLETED 任务孤儿清理: 移除不存在的依赖
"""

import json
import logging
import re
import sqlite3
from datetime import UTC, datetime

logger = logging.getLogger(__name__)

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


DB = "data/databases/governance.db"
NOW = datetime.now(UTC).isoformat()

conn = sqlite3.connect(DB)
try:
    all_ids = {r[0] for r in conn.execute("SELECT task_id FROM tasks WHERE is_deleted=0").fetchall()}

    rows = conn.execute(
        "SELECT task_id, depends_on, status FROM tasks WHERE is_deleted=0 AND depends_on != '[]'"
    ).fetchall()

    _RANGE_RE = re.compile(r"^([A-Z]+-[A-Z]+(?:-\d+)?-(\d+))~(\d+)$")
    _MODULE_RE = re.compile(r"^MOD-[A-Z]+-\d+$")

    fixes = {
        "range_expanded": 0,
        "module_ref_removed": 0,
        "dead_ref_removed": 0,
        "total_tasks_updated": 0,
    }

    for r in rows:
        tid = r[0]
        status = r[2]
        try:
            deps = json.loads(r[1]) if isinstance(r[1], str) else r[1]
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            # Phase 2 P2 修复（异常处理 HIGH）：bare except 吞噬 JSON 解析异常=孤儿检测全部失真
            logger.warning("fix_orphan_deps: task %s depends_on 解析失败(%s: %s)，按空依赖处理", r[0], type(e).__name__, e)
            deps = []

        new_deps = []
        changed = False

        for dep in deps:
            if dep in all_ids:
                new_deps.append(dep)
                continue

            m = _RANGE_RE.match(dep)
            if m:
                prefix = m.group(1)
                start = int(m.group(2))
                end = int(m.group(3))
                expanded = []
                for i in range(start, end + 1):
                    candidate = f"{prefix.rsplit('-', 1)[0]}-{i:04d}"
                    if candidate in all_ids:
                        expanded.append(candidate)
                if expanded:
                    new_deps.extend(expanded)
                    fixes["range_expanded"] += 1
                    changed = True
                    print(f"  [RANGE] {tid}: {dep} → {expanded[:5]}{'...' if len(expanded) > 5 else ''}")
                else:
                    print(f"  [RANGE-EMPTY] {tid}: {dep} → no matches, dropping")
                    changed = True
                continue

            if _MODULE_RE.match(dep):
                fixes["module_ref_removed"] += 1
                changed = True
                print(f"  [MODULE] {tid}: dropping module ref {dep}")
                continue

            if status == "COMPLETED":
                fixes["dead_ref_removed"] += 1
                changed = True
                continue

            new_deps.append(dep)

        if changed:
            new_json = json.dumps(new_deps, ensure_ascii=False)
            conn.execute("UPDATE tasks SET depends_on=?, updated_at=? WHERE task_id=?", (new_json, NOW, tid))
            fixes["total_tasks_updated"] += 1

    conn.commit()

    print("\n=== Fix Summary ===")
    print(f"  Range notations expanded: {fixes['range_expanded']}")
    print(f"  Module refs removed: {fixes['module_ref_removed']}")
    print(f"  Dead refs removed (COMPLETED tasks): {fixes['dead_ref_removed']}")
    print(f"  Total tasks updated: {fixes['total_tasks_updated']}")

    # Verify remaining orphans
    all_ids2 = {r[0] for r in conn.execute("SELECT task_id FROM tasks WHERE is_deleted=0").fetchall()}
    rows2 = conn.execute(
        "SELECT task_id, depends_on, status FROM tasks WHERE is_deleted=0 AND depends_on != '[]'"
    ).fetchall()
    remaining = 0
    for r in rows2:
        try:
            deps = json.loads(r[1]) if isinstance(r[1], str) else r[1]
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            # Phase 2 P2 修复（异常处理 HIGH）：bare except 吞噬 JSON 解析异常=孤儿统计失真
            logger.warning("fix_orphan_deps: verify task %s depends_on 解析失败(%s: %s)，按空依赖处理", r[0], type(e).__name__, e)
            deps = []
        for dep in deps:
            if dep not in all_ids2:
                remaining += 1

    print(f"\n  Remaining orphan refs: {remaining}")
finally:
    conn.close()
