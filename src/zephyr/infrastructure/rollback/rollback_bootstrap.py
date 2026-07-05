# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_bootstrap
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_rollback_bootstrap | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackBootstrap — 零依赖自举回滚器。

依据: 蓝图 MOD-INF-021 §6.12 B56, §7 Phase 6.1, 决策 D-021-11

当主回滚器 (rollback_executor.py) 连续 3 次自身操作失败时，
自动将回滚升级到 bootstrap 模式。

设计原则:
    - 零项目依赖——仅使用 subprocess.run git CLI + Python 标准库
    - 不 import 任何 zephyr 模块——确保在项目代码自身损坏时仍可运行
    - chmod 444 (Owner只读) 锁定——防止 AI 篡改 bootstrapper 自身

对标: K8s static pod manifest 自愈模式

Exit Codes:
    0  = 成功回滚
    1  = git 不可用
    2  = 无可回滚历史
    3  = revert 冲突
    10 = BOOTSTRAP_ESCALATED (主回滚器失败→bootstrap接管)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _git(args: list[str], cwd: Path | None = None, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd or Path.cwd()),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _check_git_available() -> bool:
    result = _git(["--version"])
    return result.returncode == 0


def _get_recent_commits(project_root: Path, count: int = 5) -> list[str]:
    result = _git(["log", "--oneline", f"-{count}"], cwd=project_root)
    if result.returncode != 0:
        return []
    return [line.split()[0] for line in result.stdout.strip().split("\n") if line]


def _git_revert(project_root: Path, commit_sha: str) -> bool:
    result = _git(["revert", "--no-edit", commit_sha], cwd=project_root)
    return result.returncode == 0


def _git_status_clean(project_root: Path) -> bool:
    result = _git(["status", "--porcelain"], cwd=project_root)
    return result.stdout.strip() == ""


def _git_head_short(project_root: Path) -> str:
    result = _git(["rev-parse", "--short", "HEAD"], cwd=project_root)
    return result.stdout.strip()


def bootstrap_rollback(project_root: Path | None = None, commit_sha: str = "") -> int:
    project_root = project_root or Path.cwd()

    if not _check_git_available():
        print("BOOTSTRAP ERROR: git not available", file=sys.stderr)
        return 1

    if not commit_sha:
        commits = _get_recent_commits(project_root, 5)
        if not commits:
            print("BOOTSTRAP ERROR: no commits available for rollback", file=sys.stderr)
            return 2
        commit_sha = commits[0]

    print(f"BOOTSTRAP: reverting to {commit_sha}")
    if not _git_revert(project_root, commit_sha):
        print(f"BOOTSTRAP ERROR: revert conflict for {commit_sha}", file=sys.stderr)
        return 3

    head_after = _git_head_short(project_root)
    print(f"BOOTSTRAP: reverted to {head_after}")

    if _git_status_clean(project_root):
        print("BOOTSTRAP: working tree clean after revert")
    else:
        print("BOOTSTRAP WARNING: working tree not clean after revert", file=sys.stderr)

    return 0


def bootstrap_from_failure_log(failure_log_path: Path) -> int:
    if not failure_log_path.exists():
        print("BOOTSTRAP: no failure log found, running normal bootstrap", file=sys.stderr)
        return bootstrap_rollback()

    import json

    try:
        failures = json.loads(failure_log_path.read_text(encoding="utf-8"))
        count = failures.get("consecutive_failures", 0)
        last_commit = failures.get("last_known_good_commit", "")

        if count >= 3 and last_commit:
            print(f"BOOTSTRAP: ESCALATED after {count} consecutive failures")
            print(f"BOOTSTRAP: restoring to last known good commit {last_commit}")
            return bootstrap_rollback(commit_sha=last_commit)
    except (json.JSONDecodeError, FileNotFoundError):
        pass

    return bootstrap_rollback()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Rollback Bootstrap - zero-dependency rollback")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--commit", type=str, default="", help="Target commit SHA to rollback to")
    parser.add_argument("--from-failure-log", type=Path, default=None, help="Read failure log for escalated bootstrap")
    args = parser.parse_args()

    if args.from_failure_log:
        exit_code = bootstrap_from_failure_log(args.from_failure_log)
    else:
        exit_code = bootstrap_rollback(project_root=args.project_root, commit_sha=args.commit)

    if exit_code != 0:
        print(f"BOOTSTRAP exited with code {exit_code}", file=sys.stderr)

    sys.exit(exit_code if exit_code < 10 else 10)
