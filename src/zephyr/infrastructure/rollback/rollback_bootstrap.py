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
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
    10 = BOOTSTRAP_ESCALATED (主回滚器失败->bootstrap接管)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: args 参数
#   fields: 参数 args，类型注解 list[str]
#   code: rollback_bootstrap.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: cwd 参数
#   fields: 参数 cwd，类型注解 Path | None
#   code: rollback_bootstrap.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: timeout 参数
#   fields: 参数 timeout，类型注解 int
#   code: rollback_bootstrap.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 Path
#   code: rollback_bootstrap.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① git
#   name_en: git
#   intro: git(args, cwd, timeout) 源码 L152-L159
#   desc: 源码 L152-L159
#   inputs: args cwd timeout
#   outputs: subprocess.CompletedProcess[str]
# - id: A2
#   name_zh: ② check_git_available
#   name_en: check_git_available
#   intro: check_git_available() 源码 L167-L169
#   desc: 源码 L167-L169
#   inputs: 无参数
#   outputs: bool
# - id: A3
#   name_zh: ③ get_recent_commits
#   name_en: get_recent_commits
#   intro: get_recent_commits(project_root, count) 源码 L177-L181
#   desc: 源码 L177-L181
#   inputs: project_root count
#   outputs: list[str]
# - id: A4
#   name_zh: ④ git_revert
#   name_en: git_revert
#   intro: git_revert(project_root, commit_sha) 源码 L189-L191
#   desc: 源码 L189-L191
#   inputs: project_root commit_sha
#   outputs: bool
# - id: A5
#   name_zh: ⑤ git_status_clean
#   name_en: git_status_clean
#   intro: git_status_clean(project_root) 源码 L199-L201
#   desc: 源码 L199-L201
#   inputs: project_root
#   outputs: bool
# - id: A6
#   name_zh: ⑥ git_head_short
#   name_en: git_head_short
#   intro: git_head_short(project_root) 源码 L209-L211
#   desc: 源码 L209-L211
#   inputs: project_root
#   outputs: str
# - id: A7
#   name_zh: ⑦ bootstrap_rollback
#   name_en: bootstrap_rollback
#   intro: bootstrap_rollback(project_root, commit_sha) 源码 L219-L248
#   desc: 源码 L219-L248
#   inputs: project_root commit_sha
#   outputs: int
# - id: A8
#   name_zh: ⑧ bootstrap_from_failure_log
#   name_en: bootstrap_from_failure_log
#   intro: bootstrap_from_failure_log(failure_log_path) 源码 L251-L270
#   desc: 源码 L251-L270
#   inputs: failure_log_path
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: subprocess.CompletedProcess[str]
#   name_en: subprocess.CompletedProcess[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> O1
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden


def git(args: list[str], cwd: Path | None = None, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return run_subprocess_hidden(
        ["git"] + args,
        cwd=str(cwd or Path.cwd()),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _git(args: list[str], cwd: Path | None = None, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    """Backward-compatible thin wrapper around :func:`git`."""
    return git(args, cwd=cwd, timeout=timeout)


def check_git_available() -> bool:
    result = git(["--version"])
    return result.returncode == 0


def _check_git_available() -> bool:
    """Backward-compatible thin wrapper around :func:`check_git_available`."""
    return check_git_available()


def get_recent_commits(project_root: Path, count: int = 5) -> list[str]:
    result = git(["log", "--oneline", f"-{count}"], cwd=project_root)
    if result.returncode != 0:
        return []
    return [line.split()[0] for line in result.stdout.strip().split("\n") if line]


def _get_recent_commits(project_root: Path, count: int = 5) -> list[str]:
    """Backward-compatible thin wrapper around :func:`get_recent_commits`."""
    return get_recent_commits(project_root, count=count)


def git_revert(project_root: Path, commit_sha: str) -> bool:
    result = git(["revert", "--no-edit", commit_sha], cwd=project_root)
    return result.returncode == 0


def _git_revert(project_root: Path, commit_sha: str) -> bool:
    """Backward-compatible thin wrapper around :func:`git_revert`."""
    return git_revert(project_root, commit_sha)


def git_status_clean(project_root: Path) -> bool:
    result = git(["status", "--porcelain"], cwd=project_root)
    return result.stdout.strip() == ""


def _git_status_clean(project_root: Path) -> bool:
    """Backward-compatible thin wrapper around :func:`git_status_clean`."""
    return git_status_clean(project_root)


def git_head_short(project_root: Path) -> str:
    result = git(["rev-parse", "--short", "HEAD"], cwd=project_root)
    return result.stdout.strip()


def _git_head_short(project_root: Path) -> str:
    """Backward-compatible thin wrapper around :func:`git_head_short`."""
    return git_head_short(project_root)


def bootstrap_rollback(project_root: Path | None = None, commit_sha: str = "") -> int:
    project_root = project_root or Path.cwd()

    if not check_git_available():
        # 保留 print（5.20 B/C 类）：本模块是零依赖灾难恢复 CLI，print 即操作员 UX
        # （恢复场景下 logging 未必已配置，直出 stderr/stdout 是必须的可见性通道）
        print("BOOTSTRAP ERROR: git not available", file=sys.stderr)
        return 1

    if not commit_sha:
        commits = get_recent_commits(project_root, 5)
        if not commits:
            print("BOOTSTRAP ERROR: no commits available for rollback", file=sys.stderr)
            return 2
        commit_sha = commits[0]

    print(f"BOOTSTRAP: reverting to {commit_sha}")
    if not git_revert(project_root, commit_sha):
        print(f"BOOTSTRAP ERROR: revert conflict for {commit_sha}", file=sys.stderr)
        return 3

    head_after = git_head_short(project_root)
    print(f"BOOTSTRAP: reverted to {head_after}")

    if git_status_clean(project_root):
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
