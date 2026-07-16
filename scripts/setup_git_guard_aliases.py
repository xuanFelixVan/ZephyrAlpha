#!/usr/bin/env python3
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §concurrency_guard
# [MODULE] scripts.setup_git_guard_aliases
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.git_guard
# [CONSUMERS] AI session 冷启动序列；手动执行
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只修改本地 git config（--local）；不修改全局 config
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=失败
# [TESTS] tests/red_blue/test_concurrency_guard_red_blue.py
# [A_script] module_id=MOD-GOV_setup_git_guard_aliases | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Setup/Remove Git Aliases for Git Guard — 自动化集成入口。

将危险 git 命令（reset/checkout/stash/revert/restore）的 alias 设置为通过 git_guard.py 执行，
实现自动拦截。设置后，执行 `git reset --hard` 会自动调用 `python scripts/git_guard.py reset --hard`。

使用方式:
    # 安装 alias（一次性）
    python scripts/setup_git_guard_aliases.py install

    # 移除 alias
    python scripts/setup_git_guard_aliases.py uninstall

    # 查看当前状态
    python scripts/setup_git_guard_aliases.py status

原理:
    git config alias.reset '!python scripts/git_guard.py reset'
    → 执行 `git reset --hard` 时，git 实际执行 `python scripts/git_guard.py reset --hard`
    → git_guard.py 检查 .ailocks/ 冲突，有冲突则阻断（exit 1），无冲突则透传给真实 git

注意:
    - alias 是 --local 级别，只影响当前仓库
    - alias 以 `!` 开头表示执行 shell 命令（非 git 子命令）
    - 设置 alias 后，`git reset` 会先经过 git_guard.py 检查
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# 危险子命令列表（与 git_guard.py DANGEROUS_SUBCOMMANDS 对齐）
DANGEROUS_SUBCOMMANDS = ["reset", "checkout", "stash", "revert", "restore", "mv"]

# git_guard.py 的相对路径（相对于仓库根目录）
GIT_GUARD_SCRIPT = "scripts/git_guard.py"


def _get_repo_root() -> Path:
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


def _git_config_get(key: str) -> str:
    """获取 git config 值。"""
    result = subprocess.run(
        ["git", "config", "--local", "--get", key],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def _git_config_set(key: str, value: str) -> bool:
    """设置 git config 值。"""
    result = subprocess.run(
        ["git", "config", "--local", key, value],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _git_config_unset(key: str) -> bool:
    """移除 git config 值。"""
    result = subprocess.run(
        ["git", "config", "--local", "--unset", key],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def install_aliases() -> int:
    """安装 git alias，将危险命令重定向到 git_guard.py。"""
    repo_root = _get_repo_root()
    guard_path = repo_root / GIT_GUARD_SCRIPT

    if not guard_path.is_file():
        print(f"[ERROR] git_guard.py 不存在: {guard_path}", file=sys.stderr)
        return 1

    print("[SETUP] 安装 git alias（--local 级别）...")
    installed = 0
    for cmd in DANGEROUS_SUBCOMMANDS:
        alias_key = f"alias.{cmd}"
        alias_value = f"!python {GIT_GUARD_SCRIPT} {cmd}"
        if _git_config_set(alias_key, alias_value):
            print(f"  [OK] git {cmd} → {alias_value}")
            installed += 1
        else:
            print(f"  [FAIL] git {cmd} 设置失败", file=sys.stderr)

    print(f"\n[完成] 已安装 {installed}/{len(DANGEROUS_SUBCOMMANDS)} 个 alias")
    print("\n现在执行以下命令会自动经过 git_guard.py 检查:")
    for cmd in DANGEROUS_SUBCOMMANDS:
        print(f"  git {cmd} ...")
    print("\n绕过检查（紧急情况）: git -c alias.reset= reset --hard ...")
    return 0 if installed == len(DANGEROUS_SUBCOMMANDS) else 1


def uninstall_aliases() -> int:
    """移除 git alias。"""
    print("[REMOVE] 移除 git alias...")
    removed = 0
    for cmd in DANGEROUS_SUBCOMMANDS:
        alias_key = f"alias.{cmd}"
        current = _git_config_get(alias_key)
        if current:
            if _git_config_unset(alias_key):
                print(f"  [OK] 移除 git alias.{cmd}")
                removed += 1
            else:
                print(f"  [FAIL] 移除 git alias.{cmd} 失败", file=sys.stderr)
        else:
            print(f"  [SKIP] git alias.{cmd} 不存在")
    print(f"\n[完成] 已移除 {removed} 个 alias")
    return 0


def status_aliases() -> int:
    """查看当前 alias 状态。"""
    print("[STATUS] git alias 状态:")
    active = 0
    for cmd in DANGEROUS_SUBCOMMANDS:
        alias_key = f"alias.{cmd}"
        current = _git_config_get(alias_key)
        if current:
            print(f"  [ACTIVE] git {cmd} → {current}")
            active += 1
        else:
            print(f"  [INACTIVE] git {cmd}（未设置 alias）")
    print(f"\n活跃 alias: {active}/{len(DANGEROUS_SUBCOMMANDS)}")
    if active == len(DANGEROUS_SUBCOMMANDS):
        print("状态: 全部启用（危险命令自动拦截）")
    elif active == 0:
        print("状态: 全部禁用（危险命令不拦截）")
    else:
        print("状态: 部分启用")
    return 0


def main() -> int:
    """入口。

    Usage:
        python scripts/setup_git_guard_aliases.py install    # 安装
        python scripts/setup_git_guard_aliases.py uninstall  # 移除
        python scripts/setup_git_guard_aliases.py status    # 查看状态
    """
    if len(sys.argv) < 2:
        print("Usage: python scripts/setup_git_guard_aliases.py [install|uninstall|status]")
        return 1

    action = sys.argv[1].lower()
    if action == "install":
        return install_aliases()
    elif action == "uninstall":
        return uninstall_aliases()
    elif action == "status":
        return status_aliases()
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        print("Usage: python scripts/setup_git_guard_aliases.py [install|uninstall|status]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
