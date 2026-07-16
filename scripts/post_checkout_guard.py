#!/usr/bin/env python3
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §concurrency_guard
# [MODULE] scripts.post_checkout_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.rollback.concurrency_guard
# [CONSUMERS] .git/hooks/post-checkout
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读扫描 .ailocks/；不修改锁状态；只警告不阻断（事后检测）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=无冲突或仅警告; 永不 exit 1（不阻断 checkout）
# [TESTS] tests/red_blue/test_concurrency_guard_red_blue.py
# [A_script] module_id=MOD-GOV_post_checkout_guard | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Post-checkout Guard — 事后检测 checkout 是否覆盖了其他 session 的文件锁。

根因：git_guard.py 是事前拦截，但 git checkout -- <file> 不触发 pre-checkout hook，
只有 post-checkout hook。本脚本作为事后检测，在 checkout 完成后扫描 .ailocks/，
如果发现被锁文件被覆盖，发出警告（无法阻止，但提醒用户恢复）。

调用方式（由 .git/hooks/post-checkout 自动调用）:
    python scripts/post_checkout_guard.py <pre_head> <post_head> <is_branch_switch>

参数:
    pre_head: checkout 前的 HEAD ref
    post_head: checkout 后的 HEAD ref
    is_branch_switch: 1=分支切换, 0=文件检出

退出码:
    0 = 无冲突 或 有冲突但仅警告（不阻断 checkout）
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

from zephyr.infrastructure.runtime.concurrency_guard import scan_active_locks


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


def _get_changed_files(pre_head: str, post_head: str) -> list[str]:
    """获取 checkout 涉及的文件列表。"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", pre_head, post_head],
            capture_output=True,
            text=True,
            check=False,
        )
        return [f for f in result.stdout.strip().split("\n") if f]
    except Exception:
        return []


def _normalize(path: str) -> str:
    return str(path).replace("\\", "/")


def check_checkout_conflict(
    pre_head: str, post_head: str, is_branch_switch: int
) -> int:
    """检测 checkout 是否覆盖了其他 session 的文件锁。

    Returns:
        0 = 无冲突或有冲突（仅警告，不阻断）
    """
    project_root = _get_project_root()

    # 扫描活跃锁
    active_locks = scan_active_locks(project_root)
    if not active_locks:
        return 0  # 无活跃锁，无需检测

    lock_map = {_normalize(l.file_path): l for l in active_locks}

    # 获取 checkout 涉及的文件
    changed_files = _get_changed_files(pre_head, post_head)
    if not changed_files:
        return 0  # 无文件变更

    # 检测交集
    overwritten: list[str] = []
    for f in changed_files:
        norm_f = _normalize(f)
        if norm_f in lock_map:
            overwritten.append(f)

    if not overwritten:
        return 0  # 无冲突

    # 发出警告
    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("[POST-CHECKOUT-GUARD] 警告：checkout 可能覆盖了其他 session 的文件锁", file=sys.stderr)
    print(f"  checkout: {pre_head[:8]}... -> {post_head[:8]}...", file=sys.stderr)
    print(f"  分支切换: {'是' if is_branch_switch else '否'}", file=sys.stderr)
    print(f"  被覆盖的锁定文件 ({len(overwritten)}):", file=sys.stderr)
    for f in overwritten:
        lock = lock_map.get(_normalize(f))
        owner = lock.owner_id if lock else "unknown"
        task = lock.task if lock else ""
        print(f"    {f}  (locked by {owner}, task: {task})", file=sys.stderr)
    print("", file=sys.stderr)
    print("  恢复建议:", file=sys.stderr)
    print("    1. 检查文件内容是否被破坏: git diff HEAD~1 -- <file>", file=sys.stderr)
    print("    2. 如果被破坏，从 reflog 恢复: git reflog", file=sys.stderr)
    print("    3. 通知锁持有者: python scripts/lock_files.py status", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    return 0  # 事后检测，不阻断


def main() -> int:
    """入口。

    sys.argv:
        [1] = pre_head (checkout 前的 HEAD ref)
        [2] = post_head (checkout 后的 HEAD ref)
        [3] = is_branch_switch (1=分支切换, 0=文件检出)
    """
    if len(sys.argv) < 4:
        # 参数不足，静默退出（不阻断）
        return 0

    pre_head = sys.argv[1]
    post_head = sys.argv[2]
    try:
        is_branch_switch = int(sys.argv[3])
    except ValueError:
        is_branch_switch = 0

    return check_checkout_conflict(pre_head, post_head, is_branch_switch)


if __name__ == "__main__":
    sys.exit(main())
