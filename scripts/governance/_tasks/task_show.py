"""governance/task_show 脚本 — 任务卡详情查询 CLI。

Usage:
    python scripts/governance/task_show.py OPS-2026062109
    python scripts/governance/task_show.py OPS-2026062109 OPS-2026062108
    python scripts/governance/task_show.py --like OPS-2026062
"""

# [BLUEPRINT] MOD-INF-005 | scripts/governance/task_show.py | §
# [MODULE] zephyr.governance.persistence.task_repo.TaskRepository
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] AI session 冷启动查询任务卡详情
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读查询；不修改任务状态
# [MODIFY-GUARD] evolving；可自由扩展输出字段
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任务不存在 → exit 1
# [TESTS] 手动验证：python scripts/governance/task_show.py <existing_task_id>
# [TTL] task_bound

from __future__ import annotations

__manifest__ = """
args: []
description: governance/task_show 脚本 — 任务卡详情查询 CLI。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT as _PROJECT_ROOT, DB_PATH  # noqa: E402

_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.governance.persistence.task_repo import TaskRepository


def _format_task(card) -> None:
    """格式化输出任务卡详情。"""
    print(f"\n{'=' * 70}")
    print(f"任务卡: {card.task_id}")
    print(f"标题: {card.title}")
    print(f"状态: {card.status.value}  优先级: {card.priority.value}  Phase: {card.phase}")
    print(f"{'=' * 70}")

    fields = [
        ("description", "描述"),
        ("deliverables", "产出物"),
        ("acceptance", "验收标准"),
        ("rollback_instructions", "回滚方案"),
        ("allowed_touch", "可修改文件白名单"),
        ("files_in_scope", "范围内文件"),
        ("applicable_rules", "适用规则"),
    ]

    for attr, label in fields:
        value = getattr(card, attr, None)
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            print(f"\n[{label}] ({len(value)} 项):")
            for item in value:
                print(f"  - {item}")
        elif isinstance(value, str) and value:
            print(f"\n[{label}]:")
            for line in value.split("\n"):
                print(f"  {line}")
        else:
            print(f"\n[{label}]: {value}")

    print(f"\n{'─' * 70}")


def main() -> None:
    """入口——查询任务卡详情。"""
    parser = argparse.ArgumentParser(description="查询任务卡详情")
    parser.add_argument("task_ids", nargs="*", help="任务卡 ID 列表")
    parser.add_argument("--like", help="模糊匹配任务卡 ID 前缀")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    init_db()
    repo = TaskRepository()

    if args.like:
        # 模糊查询：列出所有匹配前缀的任务
        import sqlite3
        from zephyr.governance.persistence.sqlite_schema import DB_PATH
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT task_id, title, status, priority FROM tasks WHERE task_id LIKE ? ORDER BY task_id",
            (f"{args.like}%",),
        ).fetchall()
        conn.close()
        if not rows:
            print(f"未找到匹配 '{args.like}' 的任务卡")
            sys.exit(1)
        print(f"\n匹配 '{args.like}' 的任务卡 ({len(rows)} 张):")
        for r in rows:
            print(f"  {r['task_id']:<24} [{r['status']:<12}] {r['priority']:<4} {r['title']}")
        return

    if not args.task_ids:
        parser.print_help()
        sys.exit(1)

    for task_id in args.task_ids:
        card = repo.get(task_id)
        if card is None:
            print(f"任务卡 {task_id} 不存在")
            continue
        if args.json:
            print(json.dumps({
                "task_id": card.task_id,
                "title": card.title,
                "status": card.status.value,
                "priority": card.priority.value,
                "description": card.description,
                "deliverables": card.deliverables,
                "acceptance": card.acceptance,
                "rollback_instructions": card.rollback_instructions,
                "allowed_touch": card.allowed_touch,
                "files_in_scope": card.files_in_scope,
                "applicable_rules": card.applicable_rules,
            }, ensure_ascii=False, indent=2))
        else:
            _format_task(card)

    repo.close()


if __name__ == "__main__":
    main()
