#!/usr/bin/env python3
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §concurrency_guard
# [MODULE] scripts.git_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.rollback.concurrency_guard
# [CONSUMERS] AI session 执行 git reset/checkout/stash/revert 前调用
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读扫描 .ailocks/；不修改锁状态；BLOCKED 时 exit 1 不执行 git 命令
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=pass-through; exit 1=blocked; exit 2=internal error
# [TESTS] tests/red_blue/test_concurrency_guard_red_blue.py
# [A_script] module_id=MOD-GOV-git_guard | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
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

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 确保 src 在 path 中
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.infrastructure.runtime.concurrency_guard import (
    ConcurrencyConflictError,
    check_rollback_conflict,
    scan_active_locks,
)

# 5.154.10 修复: 声明 __all__, 明确公共API边界
# _EXTRACTORS/_scan_untracked_in_dir 等下划线前缀符号为内部实现, 不在公共 API 内
__all__ = [
    "DANGEROUS_SUBCOMMANDS",
    "PLUMBING_BLOCKED_SUBCOMMANDS",
    "SERIALIZER_MODE_ENV",
    "MV_STRATEGY_ENV",
    "check_and_execute",
    "handle_mv",
    "scan_untracked_in_dir",
    "get_project_root",
    "get_session_id",
    "passthrough",
]

# 危险子命令集合
# clean (2026-08-08 #ARCH-GIT-CLEAN-GUARD-FIX): git clean -f* 删除 untracked 文件，
# 完全绕过 .ailocks/ 锁系统（untracked 文件不在锁管辖范围）。手动 git clean -fd 曾误删
# 15 个 untracked 文件（experiment_tracking .py + 7 docs）。纳入 DANGEROUS_SUBCOMMANDS
# 触发 self-harm 检测——有 untracked 文件 + 未授权 → 阻断。
DANGEROUS_SUBCOMMANDS = {"reset", "checkout", "stash", "revert", "restore", "mv", "clean"}

# 66 memo 裁定 7（2026-08-12 事故 6 根因）：plumbing 命令直接操纵共享 index/对象库，
# 不受 pre-commit/post-commit/reference-transaction 任何 hook 管辖——read-tree 曾隐形
# 重置共享 index、清空全部 staged 元数据。默认硬阻断；Serializer P2 形态经白名单放行。
PLUMBING_BLOCKED_SUBCOMMANDS = {"read-tree", "update-index", "write-tree", "hash-object"}
# Serializer 合法 plumbing 通道白名单（66 memo §6.3 P2 形态）
SERIALIZER_MODE_ENV = "ZEPHYR_SERIALIZER_MODE"

# stash 只读子命令（不影响工作区文件）
STASH_READONLY = {"list", "show", "drop"}
# stash 会覆盖工作区的子命令（pop/apply/branch 会写回文件）
STASH_OVERWRITE = {"pop", "apply", "branch"}

# 强制 stash 的环境变量（self_healer 等合法场景）
FORCE_STASH_ENV = "ZEPHYR_FORCE_STASH"
# GitCommitGateway 授权标记（P0-ENV 契约统一：gateway commit 流程设置此 env）
GATEWAY_ENV = "ZEPHYR_COMMIT_GATEWAY"

# Fast-path 授权标记（ARCH-GIT-CALL-BUDGET P1.3，2026-07-19）
# 由可信内部调用方（session_worktree / GitCommitGateway）设置，表示调用方已自行完成
# .ailocks/ 冲突检查与 held_files 登记，git_guard 跳过冗余的 ls-files/rev-parse 全扫，
# 直接透传。根因：alias 拦截每次 checkout/reset 触发 2-3x git 子进程 spawn，在 14 万文件
# 工作区 + fscache/fsmonitor 路径上是 git.exe 崩溃（0xc0000005 @ 0x13e4d4）的放大源。
FAST_PATH_ENV = "ZEPHYR_GIT_GUARD_FAST_PATH"


def _is_fast_path_authorized() -> bool:
    """检测调用方是否为已自检的可信内部代码（session_worktree / GitCommitGateway）。

    Fast-path 语义：调用方声明"我已对该 git 操作涉及的文件做过 .ailocks/ 冲突检查与
    held_files 登记"，git_guard 跳过自身的 ls-files 全扫 + rev-parse + 冲突检测，
    直接透传给真实 git。安全前提：调用方是 session_worktree（物理隔离 worktree +
    held_files claim）或 GitCommitGateway（自有 7 gates）。
    """
    return os.environ.get(FAST_PATH_ENV) == "1"


def _is_gateway_authorized() -> bool:
    """检测当前进程是否经 GitCommitGateway 或显式强制授权（P0-ENV 契约统一）。

    统一两个 env：
    - ZEPHYR_FORCE_STASH：self_healer 等合法场景显式强制 stash
    - ZEPHYR_COMMIT_GATEWAY：GitCommitGateway 内部 commit 流程设置
      （git_commit_gateway.py L429/L690 设此 env，validate_commit_gateway.py L62/L67 检测）

    根因：gateway 直接调 git 子进程做 stash push（git_commit_gateway.py L584-585），
    设置的是 ZEPHYR_COMMIT_GATEWAY，但本文件原只识别 ZEPHYR_FORCE_STASH，
    两者不互认。本函数统一契约，使 gateway 的 stash 操作也被识别为授权。
    """
    return os.environ.get(FORCE_STASH_ENV) == "1" or os.environ.get(GATEWAY_ENV) == "1"


# git mv 目录重命名策略环境变量
# block (默认): 检测到未跟踪文件 → 阻断
# move: 将未跟踪文件一并移动到目标目录
# stage: 将未跟踪文件移到 .aidrafts/ 安全暂存
# force: 强制跳过检查（不推荐）
MV_STRATEGY_ENV = "ZEPHYR_MV_STRATEGY"

# 环境变量名，用于获取当前 session_id
SESSION_ID_ENV = "ZEPHYR_SESSION_ID"


def get_session_id() -> str:
    """获取当前 session_id，用于区分自己 vs 其他 session 的锁（Stage 4 公共化，primary）。"""
    return os.environ.get(SESSION_ID_ENV, "git-guard-unknown")


def _get_session_id() -> str:
    """向后兼容 thin wrapper（Stage 4 公共化）。"""
    return get_session_id()


def get_project_root() -> Path:
    """获取 git 仓库根目录（Stage 4 公共化，primary）。"""
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


def _get_project_root() -> Path:
    """向后兼容 thin wrapper（Stage 4 公共化）。"""
    return get_project_root()


def run_git_silent(args: list[str]) -> str:
    """静默执行 git 命令，返回输出（Stage 4 公共化，primary）。"""
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


def _run_git_silent(args: list[str]) -> str:
    """向后兼容 thin wrapper（Stage 4 公共化）。"""
    return run_git_silent(args)


def _extract_files_reset(args: list[str]) -> list[str]:
    """git reset --hard → 所有 tracked 文件。"""
    # 只有 --hard 才危险（--soft/--mixed 只动 index）
    if "--hard" not in args:
        return []
    return [f for f in run_git_silent(["ls-files"]).split("\n") if f]


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
        return [f for f in run_git_silent(["ls-files"]).split("\n") if f]
    # 多个位置参数，可能是文件列表
    return positional[1:]


def _extract_files_stash(args: list[str]) -> list[str]:
    """git stash → 所有未提交文件（unstaged + staged）。"""
    unstaged = [f for f in run_git_silent(["diff", "--name-only", "HEAD"]).split("\n") if f]
    staged = [f for f in run_git_silent(["diff", "--cached", "--name-only"]).split("\n") if f]
    return list(set(unstaged + staged))


def _extract_files_revert(args: list[str]) -> list[str]:
    """git revert <commit> → commit 涉及的文件。"""
    positional = [a for a in args if not a.startswith("-")]
    if not positional:
        return []
    commit = positional[0]
    return [f for f in run_git_silent(["diff", "--name-only", f"{commit}..HEAD"]).split("\n") if f]


def _extract_files_restore(args: list[str]) -> list[str]:
    """git restore <file> → 指定文件。"""
    if "--" in args:
        idx = args.index("--")
        return [f for f in args[idx + 1 :] if not f.startswith("-")]
    positional = [a for a in args if not a.startswith("-")]
    return positional


def _extract_files_mv(args: list[str]) -> list[str]:
    """git mv → 由 handle_mv 特殊处理，extractor 返回空（不走锁冲突检查）。"""
    return []


_EXTRACTORS = {
    "reset": _extract_files_reset,
    "checkout": _extract_files_checkout,
    "stash": _extract_files_stash,
    "revert": _extract_files_revert,
    "restore": _extract_files_restore,
    "mv": _extract_files_mv,
}


def _check_conflict_or_passthrough(git_args: list[str], files_in_scope: list[str]) -> int:
    """检查锁冲突，无冲突则透传执行。"""
    if not files_in_scope:
        return passthrough(git_args)
    project_root = get_project_root()
    session_id = get_session_id()
    try:
        conflict = check_rollback_conflict(files_in_scope, session_id, project_root)
    except Exception as e:
        print(f"[GIT-GUARD] 冲突检查内部错误: {e}", file=sys.stderr)
        return passthrough(git_args)
    if conflict.has_conflict:
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
    return passthrough(git_args)


# ============================================================================
# 自伤检测（L1+L2，#ARCH-GIT-SELF-HARM-GUARD，2026-08-04）
# 根因：git reset --hard / checkout -- / restore 覆盖工作区未提交修改，
# 而 .ailocks/ 为空时锁冲突检测全部放行。自伤检测补上"有未提交修改 + 未授权 → 阻断"。
# 逃生通道：ZEPHYR_FORCE_STASH / ZEPHYR_COMMIT_GATEWAY（与 stash 阻断对齐）
# ============================================================================


def _get_dirty_tracked_files() -> set[str] | None:
    """获取有未提交修改的 tracked 文件集合（忽略 untracked）。

    Returns:
        set[str] = 有修改的文件集合（可能为空集）
        None = git status 失败（fail-open，调用方应跳过自伤检测）
    """
    try:
        dirty_r = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:  # noqa: BLE001 — fail-open
        print("[GIT-GUARD] git status 失败，自伤检测跳过（fail-open）", file=sys.stderr)
        return None
    if dirty_r.returncode != 0:
        return None
    dirty: set[str] = set()
    for line in dirty_r.stdout.splitlines():
        # porcelain 格式: "XY filename"（X/Y 各1字符 + 空格 + 文件名）
        # 不用 .strip()——会去掉行首空格导致 line[3:] 切片错位
        line = line.rstrip()
        if len(line) < 4 or line.startswith("??"):
            continue
        fname = line[3:]
        if fname:
            dirty.add(fname)
    return dirty


def _get_untracked_files() -> set[str] | None:
    """获取 untracked 文件集合（git clean 的删除目标）。

    Returns:
        set[str] = untracked 文件集合（可能为空集）
        None = git status 失败（fail-open，调用方应跳过自伤检测）
    """
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:  # noqa: BLE001 — fail-open
        print("[GIT-GUARD] git status 失败，clean 自伤检测跳过（fail-open）", file=sys.stderr)
        return None
    if r.returncode != 0:
        return None
    untracked: set[str] = set()
    for line in r.stdout.splitlines():
        line = line.rstrip()
        if line.startswith("??"):
            fname = line[3:]
            if fname:
                untracked.add(fname)
    return untracked


def _audit_self_harm(
    action: str,
    had_uncommitted: bool,
    forced: bool,
    file_count: int,
    dirty_files: list[str],
) -> None:
    """自伤检测审计写入（非阻断，jsonl 追加）。

    审计文件: .runtime/gate_audit/git_guard_self_harm.jsonl
    """
    import time  # 局部 import 避免修改顶部 import 区

    audit_dir = get_project_root() / ".runtime" / "gate_audit"
    try:
        audit_dir.mkdir(parents=True, exist_ok=True)
    except Exception:  # noqa: BLE001 — 审计不阻断
        return
    record = {
        "timestamp": time.time(),
        "session_id": get_session_id(),
        "action": action,
        "had_uncommitted": had_uncommitted,
        "forced": forced,
        "file_count": file_count,
        "files": dirty_files,
    }
    audit_file = audit_dir / "git_guard_self_harm.jsonl"
    try:
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计不阻断
        pass


def _check_self_harm_reset_hard(git_args: list[str]) -> int | None:
    """reset --hard 自伤检测（L1 止血，#ARCH-GIT-SELF-HARM-GUARD，2026-08-04）。

    工作区有 tracked 未提交修改 + 未授权 → fail-closed 阻断。
    授权（ZEPHYR_FORCE_STASH / ZEPHYR_COMMIT_GATEWAY）或无未提交修改 → 放行（return None）。

    Returns:
        None = 放行，继续后续流程（锁冲突检查）
        1 = 阻断
    """
    if "--hard" not in git_args:
        return None  # --soft/--mixed 不覆盖工作区，不触发自伤检测

    dirty_files = _get_dirty_tracked_files()
    if dirty_files is None:
        return None  # fail-open

    had_uncommitted = len(dirty_files) > 0
    authorized = _is_gateway_authorized()

    if authorized or not had_uncommitted:
        _audit_self_harm(
            action="reset --hard",
            had_uncommitted=had_uncommitted,
            forced=authorized,
            file_count=len(dirty_files),
            dirty_files=sorted(dirty_files)[:10],
        )
        if authorized and had_uncommitted:
            print(
                f"[GIT-GUARD] reset --hard 授权放行（{FORCE_STASH_ENV}|{GATEWAY_ENV}），"
                f"将丢弃 {len(dirty_files)} 个未提交文件",
                file=sys.stderr,
            )
        return None  # 继续锁冲突检查

    # 阻断
    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("[GIT-GUARD] git reset --hard 被阻断——会丢弃未提交的 AI 编辑（自伤防护）", file=sys.stderr)
    print(f"  未提交文件 ({len(dirty_files)}):", file=sys.stderr)
    for f in sorted(dirty_files)[:10]:
        print(f"    {f}", file=sys.stderr)
    if len(dirty_files) > 10:
        print(f"    ... 及其他 {len(dirty_files) - 10} 个文件", file=sys.stderr)
    print("", file=sys.stderr)
    print("  解决方案:", file=sys.stderr)
    print("    1. 先 commit 你的修改（经 GitCommitGateway）", file=sys.stderr)
    print(f"    2. 强制 reset（确认丢弃未提交修改）：{FORCE_STASH_ENV}=1 git reset --hard", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    _audit_self_harm(
        action="reset --hard",
        had_uncommitted=True,
        forced=False,
        file_count=len(dirty_files),
        dirty_files=sorted(dirty_files)[:10],
    )
    return 1


def _check_self_harm_files(
    git_args: list[str],
    files_in_scope: list[str],
    action: str,
) -> int | None:
    """checkout -- / restore 自伤检测（L2.1，#ARCH-GIT-SELF-HARM-GUARD，2026-08-04）。

    目标文件有未提交修改 + 未授权 → fail-closed 阻断。
    checkout <branch>（无 --）不触发（切分支的修改处理由 git 本身负责）。

    Returns:
        None = 放行，继续后续流程（锁冲突检查）
        1 = 阻断
    """
    # checkout <branch>（无 --）不触发自伤检测
    if action == "checkout" and "--" not in git_args:
        return None

    if not files_in_scope:
        return None

    dirty_files = _get_dirty_tracked_files()
    if dirty_files is None:
        return None  # fail-open

    # 交集：目标文件中有未提交修改的
    at_risk = [f for f in files_in_scope if f in dirty_files]
    authorized = _is_gateway_authorized()

    if authorized or not at_risk:
        _audit_self_harm(
            action=f"{action} --",
            had_uncommitted=bool(at_risk),
            forced=authorized,
            file_count=len(at_risk),
            dirty_files=at_risk[:10],
        )
        if authorized and at_risk:
            print(
                f"[GIT-GUARD] {action} 授权放行（{FORCE_STASH_ENV}|{GATEWAY_ENV}），将丢弃 {len(at_risk)} 个未提交文件",
                file=sys.stderr,
            )
        return None  # 继续锁冲突检查

    # 阻断
    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"[GIT-GUARD] git {action} 被阻断——会丢弃未提交的 AI 编辑（自伤防护）", file=sys.stderr)
    print(f"  at-risk 文件 ({len(at_risk)}):", file=sys.stderr)
    for f in at_risk[:10]:
        print(f"    {f}", file=sys.stderr)
    if len(at_risk) > 10:
        print(f"    ... 及其他 {len(at_risk) - 10} 个文件", file=sys.stderr)
    print("", file=sys.stderr)
    print("  解决方案:", file=sys.stderr)
    print("    1. 先 commit 你的修改（经 GitCommitGateway）", file=sys.stderr)
    print(f"    2. 强制执行（确认丢弃）：{FORCE_STASH_ENV}=1 git {action} ...", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    _audit_self_harm(
        action=f"{action} --",
        had_uncommitted=True,
        forced=False,
        file_count=len(at_risk),
        dirty_files=at_risk[:10],
    )
    return 1


def _check_self_harm_clean(git_args: list[str]) -> int | None:
    """git clean 自伤检测（#ARCH-GIT-CLEAN-GUARD-FIX，2026-08-11）。

    根因：_EXTRACTORS 没有 clean 条目 → extractor=None → 直接 passthrough，
    等于零拦截。clean 删除 untracked 文件，完全绕过 .ailocks/ 锁系统
    （untracked 文件不在锁管辖范围）。2026-08-11 灾难：AI 执行 git clean -fd
    误删 AI_review_instructions.md 等多个 untracked 文件。

    防护策略：有 untracked 文件 + 未授权 → fail-closed 阻断。
    授权（ZEPHYR_FORCE_STASH / ZEPHYR_COMMIT_GATEWAY）或无 untracked → 放行。

    Returns:
        None = 放行（无 untracked 或已授权）
        1 = 阻断
    """
    # 只读子命令直接放行
    args = git_args[1:]  # 去掉 'clean'
    if args and args[0] in {"-n", "--dry-run"}:
        return None  # dry-run 只列出不删除

    # 获取 untracked 文件
    untracked_files = _get_untracked_files()
    if untracked_files is None:
        return None  # fail-open（git status 失败）

    has_untracked = len(untracked_files) > 0
    authorized = _is_gateway_authorized()

    if authorized or not has_untracked:
        _audit_self_harm(
            action="clean",
            had_uncommitted=has_untracked,
            forced=authorized,
            file_count=len(untracked_files),
            dirty_files=sorted(untracked_files)[:10],
        )
        if authorized and has_untracked:
            print(
                f"[GIT-GUARD] clean 授权放行（{FORCE_STASH_ENV}|{GATEWAY_ENV}），"
                f"将删除 {len(untracked_files)} 个 untracked 文件",
                file=sys.stderr,
            )
        return None  # 放行

    # 阻断
    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("[GIT-GUARD] git clean 被阻断——会删除 untracked 文件（自伤防护）", file=sys.stderr)
    print(f"  untracked 文件 ({len(untracked_files)}):", file=sys.stderr)
    for f in sorted(untracked_files)[:10]:
        print(f"    {f}", file=sys.stderr)
    if len(untracked_files) > 10:
        print(f"    ... 及其他 {len(untracked_files) - 10} 个文件", file=sys.stderr)
    print("", file=sys.stderr)
    print("  解决方案:", file=sys.stderr)
    print("    1. 先 commit 或 git add 你的文件", file=sys.stderr)
    print(f"    2. 强制 clean（确认删除）：{FORCE_STASH_ENV}=1 git clean -fd", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    _audit_self_harm(
        action="clean",
        had_uncommitted=True,
        forced=False,
        file_count=len(untracked_files),
        dirty_files=sorted(untracked_files)[:10],
    )
    return 1


def _handle_stash(git_args: list[str]) -> int:
    """stash 特殊处理：push 移走修改，pop/apply 覆盖工作区，list/show 只读。"""
    args = git_args[1:]  # 去掉 'stash'
    if args and args[0] in STASH_READONLY:
        return _passthrough(git_args)
    if args and args[0] in STASH_OVERWRITE:
        files_in_scope = _extract_files_stash(args)
        return _check_conflict_or_passthrough(git_args, files_in_scope)
    if args and args[0] == "clear":
        print("[GIT-GUARD] 警告：git stash clear 会删除所有 stash（含未恢复的修改）", file=sys.stderr)
        return _passthrough(git_args)
    # push（含无参数 git stash）：会移走未提交修改
    files_in_scope = _extract_files_stash(args)
    if not files_in_scope:
        return _passthrough(git_args)
    if _is_gateway_authorized():
        print(
            f"[GIT-GUARD] stash 授权（{FORCE_STASH_ENV}|{GATEWAY_ENV}），强制 stash {len(files_in_scope)} 个未提交文件",
            file=sys.stderr,
        )
        return _passthrough(git_args)
    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("[GIT-GUARD] git stash 被阻断——会移走未提交的修改", file=sys.stderr)
    print(f"  未提交文件 ({len(files_in_scope)}):", file=sys.stderr)
    for f in files_in_scope[:10]:
        print(f"    {f}", file=sys.stderr)
    if len(files_in_scope) > 10:
        print(f"    ... 及其他 {len(files_in_scope) - 10} 个文件", file=sys.stderr)
    print("", file=sys.stderr)
    print("  解决方案:", file=sys.stderr)
    print("    1. 先 commit 你的修改：git add <file> && git commit -m '...'", file=sys.stderr)
    print(f"    2. 强制 stash（self_healer 等合法场景）：{FORCE_STASH_ENV}=1 git stash", file=sys.stderr)
    print(f"    3. 经 GitCommitGateway commit（自动设置 {GATEWAY_ENV}=1，本门禁自动放行 stash）", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    return 1


# ============================================================================
# git mv 目录重命名防护（根因修复：git mv 只移动已跟踪文件，未跟踪文件丢失）
# ============================================================================


def scan_untracked_in_dir(dir_rel: str, project_root: Path) -> list[str]:
    """扫描目录中的未跟踪文件（git status --porcelain 筛选 ?? 前缀）（Stage 4 公共化，primary）。

    Args:
        dir_rel: 相对于 project_root 的目录路径
        project_root: 项目根目录

    Returns:
        未跟踪文件列表（相对路径，正斜杠分隔）
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            capture_output=True,
            text=True,
            check=False,
            cwd=str(project_root),
        )
    except Exception:
        return []

    dir_prefix = dir_rel.replace("\\", "/").rstrip("/") + "/"
    untracked: list[str] = []
    for line in result.stdout.split("\n"):
        if not line or not line.startswith("?? "):
            continue
        path_part = line[3:].strip()
        if path_part.startswith('"') and path_part.endswith('"'):
            path_part = path_part[1:-1]
        norm = path_part.replace("\\", "/")
        if norm.startswith(dir_prefix):
            untracked.append(norm)
    return untracked


def _scan_untracked_in_dir(dir_rel: str, project_root: Path) -> list[str]:
    """向后兼容 thin wrapper（Stage 4 公共化）。"""
    return scan_untracked_in_dir(dir_rel, project_root)


def _mv_strategy_block(untracked: list[str], source: str, dest: str, git_args: list[str]) -> int:
    """策略 B (默认): 阻断，报告未跟踪文件。"""
    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("[GIT-GUARD] git mv 被阻断——源目录存在未跟踪文件", file=sys.stderr)
    print(f"  命令: git {' '.join(git_args)}", file=sys.stderr)
    print(f"  源目录: {source}", file=sys.stderr)
    print(f"  目标目录: {dest}", file=sys.stderr)
    print(f"  未跟踪文件 ({len(untracked)}):", file=sys.stderr)
    for f in untracked[:10]:
        print(f"    {f}", file=sys.stderr)
    if len(untracked) > 10:
        print(f"    ... 及其他 {len(untracked) - 10} 个文件", file=sys.stderr)
    print("", file=sys.stderr)
    print("  解决方案:", file=sys.stderr)
    print("    1. 先处理未跟踪文件: git add <file> 或删除", file=sys.stderr)
    print(f"    2. 移动未跟踪文件到目标目录: {MV_STRATEGY_ENV}=move git mv ...", file=sys.stderr)
    print(f"    3. 暂存到 .aidrafts/: {MV_STRATEGY_ENV}=stage git mv ...", file=sys.stderr)
    print(f"    4. 强制跳过检查（不推荐）: {MV_STRATEGY_ENV}=force git mv ...", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    return 1


def _mv_strategy_move(
    untracked: list[str],
    source: str,
    dest: str,
    project_root: Path,
    git_args: list[str],
) -> int:
    """策略 A: 将未跟踪文件一并移动到目标目录。

    执行顺序: 先执行 git mv（移动已跟踪文件）→ 再移动残留的未跟踪文件。
    若 git mv 已重命名整个目录（含未跟踪文件），则源文件不存在，跳过。
    """
    exit_code = passthrough(git_args)
    if exit_code != 0:
        return exit_code

    source_prefix = source.replace("\\", "/").rstrip("/") + "/"
    dest_prefix = dest.replace("\\", "/").rstrip("/") + "/"
    moved: list[str] = []
    failed: list[tuple[str, str]] = []
    for rel_path in untracked:
        src_file = project_root / rel_path
        if not src_file.exists():
            continue
        rel_name = rel_path[len(source_prefix) :]
        dest_file = project_root / (dest_prefix + rel_name)
        try:
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_file), str(dest_file))
            moved.append(dest_prefix + rel_name)
        except Exception as e:
            failed.append((rel_path, str(e)))

    if moved:
        print(f"[GIT-GUARD] 策略=move: 已移动 {len(moved)} 个未跟踪文件到 {dest}", file=sys.stderr)
    if failed:
        print(f"[GIT-GUARD] 警告: {len(failed)} 个文件移动失败:", file=sys.stderr)
        for path, err in failed:
            print(f"    {path}: {err}", file=sys.stderr)
    return exit_code


def _mv_strategy_stage(
    untracked: list[str],
    source: str,
    project_root: Path,
    git_args: list[str],
) -> int:
    """策略 C: 将未跟踪文件移到 .aidrafts/ 安全暂存，记录映射关系。

    执行顺序: 先暂存未跟踪文件（从源目录移除）→ 再执行 git mv（源目录仅剩已跟踪文件）。
    """
    session_id = get_session_id()
    drafts_base = project_root / ".aidrafts" / session_id / "mv_rescue"
    drafts_base.mkdir(parents=True, exist_ok=True)

    mapping: dict[str, str] = {}
    staged: list[str] = []
    failed: list[tuple[str, str]] = []
    for rel_path in untracked:
        src_file = project_root / rel_path
        if not src_file.exists():
            continue
        stage_file = drafts_base / rel_path
        try:
            stage_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_file), str(stage_file))
            stage_rel = str(stage_file.relative_to(project_root)).replace("\\", "/")
            mapping[rel_path] = stage_rel
            staged.append(rel_path)
        except Exception as e:
            failed.append((rel_path, str(e)))

    if mapping:
        mapping_file = drafts_base / "mapping.json"
        mapping_file.write_text(
            json.dumps(
                {"source_dir": source, "files": mapping},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    if staged:
        drafts_rel = str(drafts_base.relative_to(project_root)).replace("\\", "/")
        print(f"[GIT-GUARD] 策略=stage: 已暂存 {len(staged)} 个未跟踪文件到 {drafts_rel}", file=sys.stderr)
        if mapping:
            mapping_rel = str(mapping_file.relative_to(project_root)).replace("\\", "/")
            print(f"  映射文件: {mapping_rel}", file=sys.stderr)
    if failed:
        print(f"[GIT-GUARD] 警告: {len(failed)} 个文件暂存失败:", file=sys.stderr)
        for path, err in failed:
            print(f"    {path}: {err}", file=sys.stderr)

    return passthrough(git_args)


def handle_mv(git_args: list[str]) -> int:
    """git mv 特殊处理：目录重命名时检测未跟踪文件（Stage 4 公共化，primary）。

    根因：git mv old_dir new_dir 只移动已跟踪文件，未跟踪文件留在旧目录，
    随后旧目录被清理时未跟踪文件丢失。

    策略（通过 ZEPHYR_MV_STRATEGY 环境变量选择）:
    - block (默认): 检测到未跟踪文件 → 阻断，报告冲突
    - move: 将未跟踪文件一并移动到目标目录
    - stage: 将未跟踪文件移到 .aidrafts/ 安全暂存，记录映射关系
    - force: 强制跳过检查（不推荐）
    """
    args = git_args[1:]
    positional = [a for a in args if not a.startswith("-")]
    if len(positional) < 2:
        return passthrough(git_args)

    source = positional[0]
    dest = positional[1]

    project_root = get_project_root()
    source_path = project_root / source

    if not source_path.is_dir():
        return passthrough(git_args)

    untracked = scan_untracked_in_dir(source, project_root)
    if not untracked:
        return passthrough(git_args)

    strategy = os.environ.get(MV_STRATEGY_ENV, "block").lower()

    if strategy == "force":
        print(f"[GIT-GUARD] {MV_STRATEGY_ENV}=force，跳过未跟踪文件检查（{len(untracked)} 个）", file=sys.stderr)
        return passthrough(git_args)
    if strategy == "move":
        return _mv_strategy_move(untracked, source, dest, project_root, git_args)
    if strategy == "stage":
        return _mv_strategy_stage(untracked, source, project_root, git_args)
    return _mv_strategy_block(untracked, source, dest, git_args)


def _handle_mv(git_args: list[str]) -> int:
    """向后兼容 thin wrapper（Stage 4 公共化）。"""
    return handle_mv(git_args)


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

    # 66 memo 裁定 7 前置硬阻断：plumbing index/对象库操纵（事故 6 根因）。
    # 不经 _EXTRACTORS 自伤检测——危险性与工作区文件冲突无关，见到即拦；
    # Serializer 合法通道经 ZEPHYR_SERIALIZER_MODE=1 白名单放行（66 memo §6.3）。
    if subcommand in PLUMBING_BLOCKED_SUBCOMMANDS and os.environ.get(SERIALIZER_MODE_ENV) != "1":
        print("", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"[GIT-GUARD] git {subcommand} 被阻断——plumbing 直操纵共享 index/对象库", file=sys.stderr)
        print("  66 号事故 6 根因：read-tree 曾隐形重置共享 index，清空全部 staged 元数据", file=sys.stderr)
        print("  此类命令不受 pre-commit/post-commit/reference-transaction 任何 hook 管辖", file=sys.stderr)
        print("", file=sys.stderr)
        print("  解决方案:", file=sys.stderr)
        print(f"    1. Serializer 合法通道：{SERIALIZER_MODE_ENV}=1 git {subcommand} ...", file=sys.stderr)
        print(
            "    2.  porcelain 替代：read-tree→reset/checkout，write-tree+commit-tree→经 GitCommitGateway",
            file=sys.stderr,
        )
        print("=" * 70, file=sys.stderr)
        _audit_self_harm(
            action=f"plumbing:{subcommand}",
            had_uncommitted=False,
            forced=False,
            file_count=0,
            dirty_files=[],
        )
        return 1

    # 非危险命令，直接透传
    if subcommand not in DANGEROUS_SUBCOMMANDS:
        return _passthrough(git_args)

    # Fast-path（ARCH-GIT-CALL-BUDGET P1.3）：可信内部调用方已自检，跳过 ls-files
    # 全扫 + 冲突检测，直接透传。仅对 checkout/reset/restore/revert 等危险命令生效；
    # stash/mv 仍走原路径（stash 涉及工作区覆盖语义复杂，mv 涉及未跟踪文件策略）。
    if _is_fast_path_authorized() and subcommand in {"checkout", "reset", "restore", "revert"}:
        return _passthrough(git_args)

    # L1 止血：reset --hard 自伤检测（#ARCH-GIT-SELF-HARM-GUARD，2026-08-04）
    # fast-path 命中时已在上面透传；此处对非 fast-path 的 reset --hard 检测未提交修改
    if subcommand == "reset":
        rc = _check_self_harm_reset_hard(git_args)
        if rc is not None:
            return rc

    # stash 特殊处理：push 移走修改，pop/apply 覆盖工作区，list/show 只读
    if subcommand == "stash":
        return _handle_stash(git_args)

    # mv 特殊处理：目录重命名时检测未跟踪文件
    if subcommand == "mv":
        return handle_mv(git_args)

    # clean 自伤检测（#ARCH-GIT-CLEAN-GUARD-FIX，2026-08-11）
    # 根因：clean 在 DANGEROUS_SUBCOMMANDS 但 _EXTRACTORS 无 clean 条目，
    # 走到 L891 extractor=None → 直接 passthrough，等于零拦截。
    # 2026-08-11 灾难：AI 执行 git clean -fd 误删多个 untracked 文件。
    if subcommand == "clean":
        rc = _check_self_harm_clean(git_args)
        if rc is not None:
            return rc
        return _passthrough(git_args)

    # 危险命令，提取文件范围
    extractor = _EXTRACTORS.get(subcommand)
    if extractor is None:
        return _passthrough(git_args)

    try:
        files_in_scope = extractor(git_args[1:])
    except Exception as e:
        print(f"[GIT-GUARD] 内部错误（文件提取失败）: {e}", file=sys.stderr)
        return _passthrough(git_args)

    # L2.1：checkout -- / restore 自伤检测（#ARCH-GIT-SELF-HARM-GUARD，2026-08-04）
    if subcommand in {"checkout", "restore"}:
        rc = _check_self_harm_files(git_args, files_in_scope, subcommand)
        if rc is not None:
            return rc

    # 检查 .ailocks/ 冲突，无冲突则透传
    return _check_conflict_or_passthrough(git_args, files_in_scope)


def passthrough(git_args: list[str]) -> int:
    """透传给真实 git 执行（Stage 4 公共化，primary）。"""
    result = subprocess.call(["git"] + git_args)
    return result


def _passthrough(git_args: list[str]) -> int:
    """向后兼容 thin wrapper（Stage 4 公共化）。"""
    return passthrough(git_args)


def main() -> int:
    """入口。"""
    # sys.argv[0] 是脚本名，sys.argv[1:] 是 git 参数
    git_args = sys.argv[1:]
    exit_code = check_and_execute(git_args)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
