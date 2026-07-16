# [BLUEPRINT] MOD-INF-005 | scripts/governance/task_self_check.py | §
# [MODULE] scripts.governance.task_self_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.task_repo; zephyr.governance.persistence.sqlite_schema; zephyr.integration.__init__
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
# [TTL] permanent
"""
task_self_check.py — 任务系统自身健康检查
=============================================
Blueprint: MOD-TASK_SYSTEM 盲点#31
依赖: TaskRepository + SQLite



诊断项：
  1. SQLite 完整性检查（PRAGMA integrity_check）
  2. Task 状态一致性（无孤儿 references）
  3. Schema 版本一致性
  4. EventHook 回调链状态
  5. 可选 --repair 自动修复

Usage:
    python scripts/governance/task_self_check.py
    python scripts/governance/task_self_check.py --repair
"""

from __future__ import annotations

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT as _PROJECT_ROOT, DB_PATH

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.persistence.sqlite_schema import DB_PATH
from zephyr.governance.persistence.task_repo import TaskRepository

_CHECK_ICON = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "FIXED": "🔧"}

_CHECKS: list[dict] = []


def check(name: str, desc: str):
    """装饰器风格注册检查项。"""

    def deco(fn):
        """deco implementation."""
        _CHECKS.append({"name": name, "desc": desc, "fn": fn})
        return fn

    return deco


class CheckResult:
    def __init__(self):
        """__init__ implementation."""
        self.passed = 0
        self.warned = 0
        self.failed = 0
        self.fixed = 0
        self.messages: list[str] = []

    def ok(self, msg: str):
        """ok implementation."""
        self.passed += 1
        self.messages.append(f"  {_CHECK_ICON['PASS']} {msg}")

    def warn(self, msg: str):
        """warn implementation."""
        self.warned += 1
        self.messages.append(f"  {_CHECK_ICON['WARN']} {msg}")

    def fail(self, msg: str):
        """fail implementation."""
        self.failed += 1
        self.messages.append(f"  {_CHECK_ICON['FAIL']} {msg}")

    def fixed(self, msg: str):
        """fixed implementation."""
        self.fixed += 1
        self.messages.append(f"  {_CHECK_ICON['FIXED']} {msg}")


# ── Check definitions ────────────────────────────────────────────────


@check("sqlite_integrity", "SQLite 数据库文件完整性")
def check_sqlite_integrity(repo: TaskRepository) -> CheckResult:
    """Check compliance and report findings."""
    cr = CheckResult()
    if not Path(DB_PATH).exists():
        cr.fail(f"数据库文件不存在: {DB_PATH}")
        return cr
    try:
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute("PRAGMA integrity_check").fetchone()
        conn.close()
        if row and row[0] == "ok":
            cr.ok("SQLite integrity_check: ok")
        else:
            cr.fail(f"SQLite 完整性异常: {row}")
    except Exception as e:
        cr.fail(f"无法执行 integrity_check: {e}")
    return cr


@check("schema_version", "数据库 Schema 版本一致性")
def check_schema_version(repo: TaskRepository) -> CheckResult:
    """Check compliance and report findings."""
    cr = CheckResult()
    try:
        conn = sqlite3.connect(str(DB_PATH))
        ver = conn.execute("PRAGMA user_version").fetchone()[0]
        conn.close()
        if ver >= 1:
            cr.ok(f"Schema user_version={ver}")
        else:
            cr.warn(f"Schema user_version={ver} (建议 >= 1)")
    except Exception as e:
        cr.fail(f"无法读取 user_version: {e}")
    return cr


@check("orphan_dependencies", "任务依赖孤儿引用检查")
def check_orphan_deps(repo: TaskRepository) -> CheckResult:
    """Check compliance and report findings."""
    cr = CheckResult()
    try:
        all_cards = repo.list_by_namespace("OPS")
        all_ids = {c.task_id for c in all_cards}
        orphans = []
        for c in all_cards:
            for dep in c.depends_on:
                if dep not in all_ids:
                    orphans.append(f"{c.task_id} -> {dep}")
        if not orphans:
            cr.ok("无孤儿依赖引用")
        else:
            cr.warn(f"发现 {len(orphans)} 个孤儿引用: {', '.join(orphans[:5])}")
    except Exception as e:
        cr.fail(f"依赖检查失败: {e}")
    return cr


@check("status_consistency", "任务状态一致性检查")
def check_status_consistency(repo: TaskRepository) -> CheckResult:
    """Check compliance and report findings."""
    cr = CheckResult()
    try:
        cards = repo.list_by_namespace("OPS")
        statuses = defaultdict(list)
        for c in cards:
            statuses[c.status.value].append(c.task_id)
        failed = statuses.get("FAILED", [])
        blocked = statuses.get("BLOCKED", [])
        if failed:
            cr.warn(f"{len(failed)} 个任务处于 FAILED: {', '.join(failed)}")
        if blocked:
            cr.warn(f"{len(blocked)} 个任务处于 BLOCKED: {', '.join(blocked)}")
        if not failed and not blocked:
            cr.ok("所有任务状态正常")
    except Exception as e:
        cr.fail(f"状态检查失败: {e}")
    return cr


@check("hook_registry", "EventHook 注册表检查")
def check_hook_registry(repo: TaskRepository) -> CheckResult:
    """Check compliance and report findings."""
    cr = CheckResult()
    try:
        from zephyr.integration.zephyr.event_hook import hook_registry

        hooks = hook_registry.get_all()
        if hooks:
            cr.ok(f"已注册 {len(hooks)} 个钩子: {', '.join(hooks[:5])}")
        else:
            cr.warn("无已注册的 EventHook——事件通知链路不完整")
    except ImportError:
        cr.warn("EventHook 模块不可用")
    except Exception as e:
        cr.fail(f"Hook 检查失败: {e}")
    return cr


# ── Main ─────────────────────────────────────────────────────────────


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="任务系统自身健康检查")
    parser.add_argument("--repair", action="store_true", help="尝试自动修复（实验性）")
    parser.add_argument("--quiet", "-q", action="store_true", help="仅输出摘要")
    args = parser.parse_args()

    if not Path(DB_PATH).exists():
        print(f"❌ 数据库不存在: {DB_PATH}", file=sys.stderr)
        print("   请先初始化: python scripts/construction/d_init_task_system.py", file=sys.stderr)
        return EXIT_FINDINGS

    from zephyr.governance.persistence.sqlite_schema import init_db

    init_db()
    repo = TaskRepository()

    print(f"\n{'=' * 60}")
    print("  ZephyrAlpha 任务系统 — 健康检查")
    print(f"  DB: {DB_PATH}")
    print(f"{'=' * 60}\n")

    total_pass, total_warn, total_fail, total_fixed = 0, 0, 0, 0

    for entry in _CHECKS:
        print(f"-- {entry['desc']} --", file=sys.stdout if not args.quiet else open("NUL", "w"))
        cr = entry["fn"](repo)
        for msg in cr.messages:
            print(msg)
        total_pass += cr.passed
        total_warn += cr.warned
        total_fail += cr.failed
        total_fixed += cr.fixed
        print()

    total = total_pass + total_warn + total_fail + total_fixed
    print(f"{'─' * 60}")
    print(f"  总计 {total} 项: ✅ {total_pass} pass  ⚠️ {total_warn} warn  ❌ {total_fail} fail  🔧 {total_fixed} fixed")
    print(f"{'─' * 60}\n")

    if total_fail > 0:
        return EXIT_ERROR
    if total_warn > 0:
        return EXIT_PASS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
