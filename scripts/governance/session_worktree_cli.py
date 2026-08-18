# [BLUEPRINT] MOD-INF-005 | scripts/governance/session_worktree_cli.py | §FP-ISO.4C
# [MODULE] scripts.governance.session_worktree_cli
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.session_worktree (session_worktree_sweep); zephyr.gov_enforcement.rule_bridge.worktree_manager (WorktreeManager); zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] AI 对话清理 stale worktree 时调用；运维手动清理
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] CLI 入口——提供 session worktree on-demand 清理与列表能力，治本遗留项#2（2026-07-17）API 完整性缺口；session_worktree.py [CONSUMERS] 头部此前声明本文件但本不存在（文档漂移），本次落地兑现声明；sweep 子命令包装公开函数 session_worktree_sweep，list 子命令包装 WorktreeManager.list_session_worktrees；所有输出走 stdout/exit code，不抛异常；--max-age 控制 sweep 年龄阈值
# [MODIFY-GUARD] 子命令 sweep/list；argparse 入口
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] main() 捕获所有异常输出 stderr + exit 1；sweep/list 成功 exit 0
# [TESTS] tests/governance/rule_bridge/test_session_worktree_cli.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""session_worktree_cli.py — session worktree 管理 CLI（治本遗留项#2，2026-07-17）

治本动机
--------
session_worktree.py 的 [CONSUMERS] 头部声明 ``scripts/governance/session_worktree_cli.py``
为本模块消费者，但该文件此前不存在——文档漂移。同时，stale worktree 清理只有
私有 ``_sweep_stale_worktrees``（仅在 session_worktree_start 内部调用），无公开
on-demand 入口，AI 累积 stale worktree 后被迫误调私有函数导致 AttributeError。

本 CLI 落地两件事：
  1. 兑现 session_worktree.py [CONSUMERS] 头部声明（消除文档漂移）
  2. 提供 AI/运维可调用的 sweep + list 子命令（消除 API 完整性缺口）

子命令
------
  sweep [--max-age MINUTES]   清理 stale session worktree 残留
  list                        列出当前所有 session worktree

Usage::

    python scripts/governance/session_worktree_cli.py sweep
    python scripts/governance/session_worktree_cli.py sweep --max-age 60
    python scripts/governance/session_worktree_cli.py list
"""
from __future__ import annotations

__manifest__ = """
args: []
description: session_worktree_cli.py — session worktree 管理 CLI（治本遗留项#2，2026-07-17）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import sys

from _shared.constants import EXIT_FINDINGS, EXIT_PASS

from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_sweep
from zephyr.gov_enforcement.rule_bridge.worktree_manager import WorktreeManager
from zephyr.shared.io.paths import REPO_ROOT


def _cmd_sweep(args: argparse.Namespace) -> int:
    """sweep 子命令：清理 stale session worktree 残留。"""
    result = session_worktree_sweep(
        project_root=REPO_ROOT,
        max_age_minutes=args.max_age,
    )
    swept = result.get("swept", 0)
    skipped = result.get("skipped", 0)
    warnings = result.get("warnings", [])
    print(f"swept={swept} skipped={skipped}")
    for w in warnings:
        print(f"  WARNING: {w}", file=sys.stderr)
    if warnings and swept == 0:
        # 有 warning 但未清理任何——提示人工评估，但仍 exit 0（清理本身无错）
        print("有需人工评估的 stale worktree，请检查上方 WARNING", file=sys.stderr)
    return EXIT_PASS
def _cmd_list(args: argparse.Namespace) -> int:
    """list 子命令：列出当前所有 session worktree。"""
    manager = WorktreeManager(REPO_ROOT)
    worktrees = manager.list_session_worktrees()
    if args.json:
        # --json 始终输出合法 JSON（空列表输出 []），便于脚本管道解析。
        # 修复（2026-07-17）：此前空 worktree 时先打印中文提示再 return，
        # 导致 --json 输出非合法 JSON（test_cli_list_json 在 registry 空时暴露）。
        print(json.dumps(worktrees, ensure_ascii=False, indent=2))
        return EXIT_PASS
    if not worktrees:
        print("（无 session worktree）")
        return EXIT_PASS
    print(f"共 {len(worktrees)} 个 session worktree:")
    for wt in worktrees:
        dirty_mark = " [dirty]" if wt.get("dirty") else ""
        print(
            f"  {wt.get('session_id', '?')}: {wt.get('path', '?')}"
            f" branch={wt.get('branch', '?')}{dirty_mark}"
        )
    return EXIT_PASS
def main() -> int:
    """CLI 主入口。"""
    parser = argparse.ArgumentParser(
        prog="session_worktree_cli",
        description="session worktree 管理 CLI（治本遗留项#2，2026-07-17）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_sweep = sub.add_parser("sweep", help="清理 stale session worktree 残留")
    p_sweep.add_argument(
        "--max-age", type=int, default=30,
        help="目录年龄阈值（分钟），默认 30（太新的不动，防误清并发 AI 正在创建的）",
    )
    p_sweep.set_defaults(func=_cmd_sweep)

    p_list = sub.add_parser("list", help="列出当前所有 session worktree")
    p_list.add_argument("--json", action="store_true", help="JSON 格式输出")
    p_list.set_defaults(func=_cmd_list)

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as e:  # noqa: BLE001 — CLI 顶层兜底，所有异常转 exit 1
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return EXIT_FINDINGS
if __name__ == "__main__":
    sys.exit(main())
