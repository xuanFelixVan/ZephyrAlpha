#!/usr/bin/env python3
# [A_script] module_id=MOD-GOV_git_guard | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md | §concurrency_guard
# [MODULE] scripts.git_guard
# [INVARIANTS] 只读扫描 .ailocks/；不修改锁状态；BLOCKED 时 exit 1 不执行 git 命令
# [CONSUMERS] AI session 执行 git reset/checkout/stash/revert 前调用
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=pass-through; exit 1=blocked; exit 2=internal error
# [TESTS] tests/red_blue/test_concurrency_guard_red_blue.py
"""
Git Guard — 拦截危险 git 命令，防止破坏其他 session 的文件锁。

根因：git reset --hard / git checkout -- / git stash 等命令会覆盖工作区文件，
完全绕过 RollbackExecutor 的 concurrency_guard 检查。本脚本作为 git wrapper，
在执行危险命令前扫描 .ailocks/registry.json，如果有活跃锁且操作的文件与锁冲突，阻断。

使用方式：
    # 直接调用（手动）
    python scripts/git_guard.py reset --hard HEAD~1

    # 设置为 git alias（自动拦截）
    git config alias.reset '!python scripts/git_guard.py reset'
    git config alias.checkout '!python scripts/git_guard.py checkout'
    git config alias.stash '!python scripts/git_guard.py stash'
    git config alias.revert '!python scripts/git_guard.py revert'
    git config alias.restore '!python scripts/git_guard.py restore'

拦截的命令：
    - git reset --hard          → 检查所有 tracked 文件
    - git checkout -- <file>    → 检查指定文件
    - git stash                 → 检查所有未提交文件
    - git revert <commit>       → 检查 commit 涉及的文件
    - git restore <file>        → 检查指定文件

退出码：
    0 = 无冲突，已透传给 git 执行
    1 = 有冲突，命令被阻断
    2 = 内部错误
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# 确保 src 在 path 中
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.infrastructure.rollback.concurrency_guard import (
    ConcurrencyConflictError,
    check_rollback_conflict,
    scan_active_locks,
)

# 危险子命令集合
DANGEROUS_SUBCOMMANDS = {"reset", "checkout", "stash", "revert", "restore"}

# 环境变量名，用于获取当前 session_id
SESSION_ID_ENV = "ZEPHYR_SESSION_ID"


def _get_session_id() -> str:
    """获取当前 session_id，用于区分自己 vs 其他 session 的锁。"""
    return os.environ.get(SESSION_ID_ENV, "git-guard-unknown")


def _get_project_root() -> Path:
    """获取 git 仓库根目录。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except Exception:
        return Path.cwd()


def _run_git_silent(args: list[str]) -> str:
    """静默执行 git 命令，返回输出。"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _extract_files_reset(args: list[str]) -> list[str]:
    """git reset --hard → 所有 tracked 文件。"""
    # 只有 --hard 才危险（--soft/--mixed 只动 index）
    if "--hard" not in args:
        return []
    return [f for f in _run_git_silent(["ls-files"]).split("\n") if f]


def _extract_files_checkout(args: list[str]) -> list[str]:
    """git checkout -- <file> 或 git checkout <branch> → 提取文件。"""
    # git checkout <branch>（切换分支）→ 检查所有 tracked 文件
    # git checkout -- <file> → 检查指定文件
    # git checkout <file> → 检查指定文件
    if "--" in args:
        idx = args.index("--")
        files = [f for f in args[idx + 1 :] if not f.startswith("-")]
        return files
    # 没有 -- 的情况：git checkout <branch> 或 git checkout <file>
    # 如果只有一个参数且不是文件，可能是分支切换 → 检查所有文件
    positional = [a for a in args if not a.startswith("-")]
    if len(positional) <= 1:
        # 可能是分支切换，检查所有 tracked 文件
        return [f for f in _run_git_silent(["ls-files"]).split("\n") if f]
    # 多个位置参数，可能是文件列表
    return positional[1:]


def _extract_files_stash(args: list[str]) -> list[str]:
    """git stash → 所有未提交文件（unstaged + staged）。"""
    unstaged = [f for f in _run_git_silent(["diff", "--name-only", "HEAD"]).split("\n") if f]
    staged = [f for f in _run_git_silent(["diff", "--cached", "--name-only"]).split("\n") if f]
    return list(set(unstaged + staged))


def _extract_files_revert(args: list[str]) -> list[str]:
    """git revert <commit> → commit 涉及的文件。"""
    positional = [a for a in args if not a.startswith("-")]
    if not positional:
        return []
    commit = positional[0]
    return [f for f in _run_git_silent(["diff", "--name-only", f"{commit}..HEAD"]).split("\n") if f]


def _extract_files_restore(args: list[str]) -> list[str]:
    """git restore <file> → 指定文件。"""
    if "--" in args:
        idx = args.index("--")
        return [f for f in args[idx + 1 :] if not f.startswith("-")]
    positional = [a for a in args if not a.startswith("-")]
    return positional


_EXTRACTORS = {
    "reset": _extract_files_reset,
    "checkout": _extract_files_checkout,
    "stash": _extract_files_stash,
    "revert": _extract_files_revert,
    "restore": _extract_files_restore,
}


def check_and_execute(git_args: list[str]) -> int:
    """检查 git 命令是否安全，安全则透传执行。

    Args:
        git_args: git 命令参数（不含 'git' 本身），如 ['reset', '--hard', 'HEAD~1']

    Returns:
        0 = 已执行（无冲突或无危险）
        1 = 被阻断（有冲突）
        2 = 内部错误
    """
    if not git_args:
        # 无参数，直接透传
        return _passthrough(git_args)

    subcommand = git_args[0]

    # 非危险命令，直接透传
    if subcommand not in DANGEROUS_SUBCOMMANDS:
        return _passthrough(git_args)

    # 危险命令，提取文件范围
    extractor = _EXTRACTORS.get(subcommand)
    if extractor is None:
        return _passthrough(git_args)

    try:
        files_in_scope = extractor(git_args[1:])
    except Exception as e:
        print(f"[GIT-GUARD] 内部错误（文件提取失败）: {e}", file=sys.stderr)
        # 内部错误时选择安全透传（不阻断正常工作）
        return _passthrough(git_args)

    # 无文件需要检查（如 git stash list）
    if not files_in_scope:
        return _passthrough(git_args)

    # 检查 .ailocks/ 冲突
    project_root = _get_project_root()
    session_id = _get_session_id()

    try:
        conflict = check_rollback_conflict(files_in_scope, session_id, project_root)
    except Exception as e:
        print(f"[GIT-GUARD] 冲突检查内部错误: {e}", file=sys.stderr)
        return _passthrough(git_args)

    if conflict.has_conflict:
        # 阻断！
        print("", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print("[GIT-GUARD] 命令被阻断——检测到其他 session 持有文件锁", file=sys.stderr)
        print(f"  命令: git {' '.join(git_args)}", file=sys.stderr)
        print(f"  冲突文件 ({len(conflict.blocked_files)}):", file=sys.stderr)
        for f in conflict.blocked_files:
            owner = conflict.locked_by.get(f, "unknown")
            print(f"    {f}  (locked by {owner})", file=sys.stderr)
        print("", file=sys.stderr)
        print("  解决方案:", file=sys.stderr)
        print("    1. 等待其他 session 释放锁（TTL 30分钟自动过期）", file=sys.stderr)
        print("    2. 手动释放锁: python scripts/lock_files.py release <file> <session_id>", file=sys.stderr)
        print("    3. 确认安全后强制执行: ZEPHYR_SESSION_ID=<owner> python scripts/git_guard.py ...", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        return 1

    # 无冲突，透传执行
    return _passthrough(git_args)


def _passthrough(git_args: list[str]) -> int:
    """透传给真实 git 执行。"""
    result = subprocess.call(["git"] + git_args)
    return result


def main() -> int:
    """入口。"""
    # sys.argv[0] 是脚本名，sys.argv[1:] 是 git 参数
    git_args = sys.argv[1:]
    exit_code = check_and_execute(git_args)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
