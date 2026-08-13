#!/usr/bin/env python3
# [MODULE] scripts.session_worktree
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] subprocess (git worktree)
# [CONSUMERS] AI session 创建/切换/合并 worktree 前调用
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] worktree 在 .worktrees/ 下；分支前缀 ai/；merge 需用户确认
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=success; exit 1=error; exit 2=internal error
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI会话按需调用的CLI worktree协调工具，人工触发非常驻服务/非cron/非daemon
"""
Session Worktree — 每 AI 独立 checkout + 分支（§11.3.1 v2.1.0 简化版）

设计文档: 65_git_safety_governance.md §11.3.1
关联议题: #ARCH-AICOLLAB-001

v2.1.0 简化:
  - 去 7 天告警（22 路审查是一次性的，merge 后立即 abort 清理）
  - create/exec/merge/abort/list 五命令

目录结构:
    d:\\ZephyrAlpha\\
    └── .worktrees\\          # worktree 根目录（.gitignore）
        ├── AI-01\\           # AI-01 的独立 checkout
        │   └── (完整项目副本，branch=ai/AI-01/<task-id>)
        └── AI-02\\

CLI:
    python scripts/session_worktree.py create <session-id> <task-id>
    python scripts/session_worktree.py exec <session-id> -- <command...>
    python scripts/session_worktree.py merge <session-id> [--to main] [--squash] [--yes]
    python scripts/session_worktree.py abort <session-id>
    python scripts/session_worktree.py list
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKTREE_ROOT = REPO_ROOT / ".worktrees"
BRANCH_PREFIX = "ai/"


def _run_git(args: list[str], cwd: str | Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    """执行 git 命令（run_subprocess_hidden 统一入口，无窗口闪现，不受 PowerShell wrapper 影响）。"""
    cmd = ["git"] + args
    return run_subprocess_hidden(cmd, capture_output=True, text=True, check=check, cwd=cwd or str(REPO_ROOT))


def _worktree_path(session_id: str) -> Path:
    """获取 session 的 worktree 路径。"""
    return WORKTREE_ROOT / session_id


def _branch_name(session_id: str, task_id: str) -> str:
    """生成分支名: ai/<session-id>/<task-id>。"""
    return f"{BRANCH_PREFIX}{session_id}/{task_id}"


def _find_branch_for_session(session_id: str) -> str | None:
    """查找 session 对应的分支（通过 git worktree list）。"""
    try:
        result = _run_git(["worktree", "list", "--porcelain"], check=False)
        if result.returncode != 0:
            return None
        wt_path = str(_worktree_path(session_id))
        for line in result.stdout.splitlines():
            if line.startswith("worktree ") and session_id in line:
                # 找到对应的 worktree，查找其分支
                for l2 in result.stdout.splitlines():
                    if l2.startswith("branch ") and session_id in l2:
                        return l2.split(" ", 1)[1].strip()
        return None
    except Exception:
        return None


# ============================================================================
# CLI 命令
# ============================================================================


def cmd_create(args: argparse.Namespace) -> int:
    """创建 worktree + 分支。"""
    session_id = args.session_id
    task_id = args.task_id
    wt_path = _worktree_path(session_id)
    branch = _branch_name(session_id, task_id)

    if wt_path.exists():
        print(f"[WORKTREE] 错误: worktree 已存在: {wt_path}", file=sys.stderr)
        print(f"  如需重建，先执行: python scripts/session_worktree.py abort {session_id}", file=sys.stderr)
        return 1

    # 创建 worktree 根目录
    WORKTREE_ROOT.mkdir(parents=True, exist_ok=True)

    # git worktree add <path> -b <branch>
    print(f"[WORKTREE] 创建 worktree: {session_id}")
    print(f"  路径: {wt_path}")
    print(f"  分支: {branch}")
    try:
        result = _run_git(
            ["worktree", "add", str(wt_path), "-b", branch],
            check=False,
        )
        if result.returncode != 0:
            print(f"[WORKTREE] git worktree add 失败:", file=sys.stderr)
            print(result.stderr, file=sys.stderr, end="")
            return 1
        print(f"[WORKTREE] 创建成功")
        print(f"  进入 worktree: cd {wt_path}")
        return 0
    except Exception as e:
        print(f"[WORKTREE] 内部错误: {e}", file=sys.stderr)
        return 2


def cmd_exec(args: argparse.Namespace) -> int:
    """在 worktree 中执行命令。"""
    session_id = args.session_id
    wt_path = _worktree_path(session_id)

    if not wt_path.exists():
        print(f"[WORKTREE] 错误: worktree 不存在: {wt_path}", file=sys.stderr)
        print(f"  先创建: python scripts/session_worktree.py create {session_id} <task-id>", file=sys.stderr)
        return 1

    if not args.command:
        print(f"[WORKTREE] 错误: 未指定要执行的命令", file=sys.stderr)
        return 1

    # 在 worktree 目录中执行命令
    print(f"[WORKTREE] 在 {session_id} 中执行: {' '.join(args.command)}")
    try:
        result = run_subprocess_hidden(args.command, cwd=str(wt_path))
        return result.returncode
    except Exception as e:
        print(f"[WORKTREE] 执行失败: {e}", file=sys.stderr)
        return 2


def cmd_merge(args: argparse.Namespace) -> int:
    """合并 worktree 分支回主分支（需用户确认）。"""
    session_id = args.session_id
    target = args.to
    wt_path = _worktree_path(session_id)

    if not wt_path.exists():
        print(f"[WORKTREE] 错误: worktree 不存在: {wt_path}", file=sys.stderr)
        return 1

    # 查找分支名
    branch = _find_branch_for_session(session_id)
    if not branch:
        print(f"[WORKTREE] 错误: 无法找到 {session_id} 的分支", file=sys.stderr)
        return 1

    # 用户确认
    if not args.yes:
        print(f"[WORKTREE] 即将合并: {branch} → {target}")
        print(f"  squash: {'是' if args.squash else '否'}")
        response = input("  确认合并？(yes/no): ").strip().lower()
        if response != "yes":
            print("[WORKTREE] 合并已取消")
            return 0

    print(f"[WORKTREE] 合并 {branch} → {target}")
    try:
        # 切换到主工作区合并
        merge_cmd = ["merge", "--no-ff"]
        if args.squash:
            merge_cmd = ["merge", "--squash"]

        result = _run_git(merge_cmd + [branch], check=False)
        if result.returncode != 0:
            print(f"[WORKTREE] 合并失败:", file=sys.stderr)
            print(result.stderr, file=sys.stderr, end="")
            print(f"  可能需要解决冲突后 git commit", file=sys.stderr)
            return 1

        if args.squash:
            # squash merge 需要手动 commit
            _run_git(["commit", "-m", f"merge(ai): {session_id} squashed"], check=False)

        print(f"[WORKTREE] 合并成功")
        # §11.3.1 v2.1.0: merge 后立即 abort 清理
        print(f"[WORKTREE] 自动清理 worktree...")
        return cmd_abort_inner(session_id)
    except Exception as e:
        print(f"[WORKTREE] 内部错误: {e}", file=sys.stderr)
        return 2


def cmd_abort_inner(session_id: str) -> int:
    """清理 worktree（内部函数，无用户确认）。"""
    wt_path = _worktree_path(session_id)

    if not wt_path.exists():
        print(f"[WORKTREE] worktree 不存在: {session_id}")
        return 0

    # git worktree remove --force
    result = _run_git(["worktree", "remove", "--force", str(wt_path)], check=False)
    if result.returncode != 0:
        # 如果 git worktree remove 失败，尝试手动删除目录
        import shutil

        shutil.rmtree(wt_path, ignore_errors=True)

    # 删除分支（如果还存在）
    branch = _find_branch_for_session(session_id)
    if branch:
        _run_git(["branch", "-D", branch], check=False)

    print(f"[WORKTREE] 已清理: {session_id}")
    return 0


def cmd_abort(args: argparse.Namespace) -> int:
    """清理 worktree（放弃修改）。"""
    return cmd_abort_inner(args.session_id)


def cmd_list(args: argparse.Namespace) -> int:
    """列出所有 worktree。"""
    try:
        result = _run_git(["worktree", "list"], check=False)
        if result.returncode != 0:
            print(f"[WORKTREE] git worktree list 失败:", file=sys.stderr)
            print(result.stderr, file=sys.stderr, end="")
            return 1
        print("[WORKTREE] 当前 worktree 列表:")
        print(result.stdout, end="")
        return 0
    except Exception as e:
        print(f"[WORKTREE] 内部错误: {e}", file=sys.stderr)
        return 2


# ============================================================================
# 入口
# ============================================================================


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Session Worktree — 每 AI 独立 checkout+分支（§11.3.1 v2.1.0）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = sub.add_parser("create", help="创建 worktree + 分支")
    p_create.add_argument("session_id", help="session ID（如 AI-01）")
    p_create.add_argument("task_id", help="任务 ID（如 task-factor-registry）")
    p_create.set_defaults(func=cmd_create)

    # exec
    p_exec = sub.add_parser("exec", help="在 worktree 中执行命令")
    p_exec.add_argument("session_id", help="session ID")
    p_exec.add_argument("command", nargs=argparse.REMAINDER, help="要执行的命令（-- 之后）")
    p_exec.set_defaults(func=cmd_exec)

    # merge
    p_merge = sub.add_parser("merge", help="合并 worktree 分支回主分支")
    p_merge.add_argument("session_id", help="session ID")
    p_merge.add_argument("--to", default="main", help="目标分支（默认 main）")
    p_merge.add_argument("--squash", action="store_true", help="squash merge")
    p_merge.add_argument("--yes", action="store_true", help="跳过确认")
    p_merge.set_defaults(func=cmd_merge)

    # abort
    p_abort = sub.add_parser("abort", help="清理 worktree（放弃修改）")
    p_abort.add_argument("session_id", help="session ID")
    p_abort.set_defaults(func=cmd_abort)

    # list
    p_list = sub.add_parser("list", help="列出所有 worktree")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as e:
        print(f"[WORKTREE] 内部错误: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
