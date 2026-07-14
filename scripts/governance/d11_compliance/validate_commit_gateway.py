# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_commit_gateway.py | §gate-commit-gw
# [MODULE] scripts.governance.d11_compliance.validate_commit_gateway
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS] .pre-commit-config.yaml (GATE-COMMIT-GW hook)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] hook 运行=裸 git commit→阻断 exit 1；gateway 用 --no-verify 绕过 hook；合并提交放行；session worktree 内 commit 放行（FP-ISO.4C：worktree 独立 index 无共享冲突，授权绕过 GitCommitGateway）
# [MODIFY-GUARD] 阻断逻辑：hook 运行本身即说明是裸 commit（gateway 用 --no-verify 不触发 hook）；合并提交检测（.git/MERGE_HEAD）；session worktree 上下文检测（cwd 含 .aidrafts/sess-）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=合并提交放行; exit 1=裸commit阻断; exit 2=脚本错误
# [TESTS] tests/test_git_commit_gateway.py
# [A_module] module_id=MOD-GOV-validate_commit_gateway | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""validate_commit_gateway.py — GATE-COMMIT-GW 门禁（OPS-2026062513）

检测裸 git commit，强制走 GitCommitGateway（根治幽灵提交）。

红蓝修复 RB-6（2026-06-29）:
  旧逻辑（已废除）: env var ZEPHYR_COMMIT_GATEWAY=1 或 commit message 含 [GW:...] 标记 → 放行
  漏洞: env var 在 shell 中持久存在（RB-2），伪造 [GW:fake] 标记可绕过（RB-6）
  新逻辑: hook 运行本身即说明是裸 commit（gateway 用 --no-verify 不触发 hook）→ 阻断

工作原理:
- GitCommitGateway.commit() 用 git commit --no-verify 绕过 pre-commit hooks
  → 本 hook 对 gateway commit 不触发（gateway 路径）
- 裸 git commit（无 --no-verify）会触发 pre-commit hooks
  → 本 hook 运行 = 非 gateway commit = 阻断 exit 1
- 合并提交（.git/MERGE_HEAD 存在）放行（merge 不经 gateway，属正常操作）
- 唯一合法绕过: git commit --no-verify（conscious bypass，由 GATE-COMMIT-GW-AUDIT 审计 reconciler 追踪）

威胁模型:
  pre-commit hook 是本地防线，可被 --no-verify 绕过。纵深防御:
  1. 本 hook: 拦截无意的裸 commit（覆盖所有非 --no-verify 路径）
  2. GATE-COMMIT-GW-AUDIT reconciler: post-commit 审计最近 20 个 commit，标记无 [GW:] 的裸 commit
  3. 过程纪律: code review + AGENTS.md 规范

对标: validate_commit_message.py（Conventional Commits 校验，commit-msg stage）
区别: 本脚本检测 commit 路径（是否经 gateway），非 message 格式

exit codes: 0=合并提交放行, 1=裸commit阻断, 2=脚本错误
"""

from __future__ import annotations

__manifest__ = """
args:
- --commit-msg-file
description: GATE-COMMIT-GW门禁——hook运行=裸commit=阻断（gateway用--no-verify不触发hook）；合并提交放行
dimensions:
- D11
priority: P1
timeout_seconds: 5
warn_only: false
"""

import subprocess
import sys
from pathlib import Path

# sys.path 必须在 from _shared 导入之前设置（namespace package 需父目录在 path 中）
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402


def _is_merge_commit() -> bool:
    """检测当前是否为合并提交（.git/MERGE_HEAD 存在）。

    merge 是正常 git 操作，不经 gateway，属合法放行场景。
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return False
        git_dir = Path(result.stdout.strip())
        return (git_dir / "MERGE_HEAD").exists()
    except Exception:
        return False


def _is_session_worktree_commit() -> bool:
    """检测当前 commit 是否在 session worktree 内（FP-ISO.4C，2026-07-01）。

    session worktree 路径格式: {REPO}/.aidrafts/sess-{id}/
    worktree 有独立 git index，session 独占整个 worktree，不存在共享冲突，
    无需 GitCommitGateway 的全局串行锁。session_worktree_commit 是授权的
    隔离提交，应放行。

    检测方式: cwd 路径含 .aidrafts/sess- 片段（pre-commit hook 的 cwd =
    worktree 根目录）。
    """
    import os
    cwd = Path(os.getcwd()).resolve()
    parts = cwd.parts
    for i, part in enumerate(parts):
        if part == ".aidrafts" and i + 1 < len(parts) and parts[i + 1].startswith("sess-"):
            return True
    return False


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="GATE-COMMIT-GW: 检测裸 git commit，强制走 GitCommitGateway",
    )
    parser.add_argument(
        "--commit-msg-file",
        default=None,
        help="commit-msg 文件路径（commit-msg stage 传入，兼容用，本门禁不依赖）",
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="pre-commit 传入的文件列表（本门禁不使用，仅兼容）",
    )
    args = parser.parse_args()

    # 合并提交放行（merge 不经 gateway，属正常操作）
    if _is_merge_commit():
        print("GATE-COMMIT-GW: SKIP (merge commit)")
        return EXIT_PASS

    # session worktree 内 commit 放行（FP-ISO.4C：worktree 独立 index，授权绕过 gateway）
    if _is_session_worktree_commit():
        print("GATE-COMMIT-GW: SKIP (session worktree commit — isolated index, FP-ISO.4C)")
        return EXIT_PASS

    # hook 运行 = 非 gateway commit = 阻断
    # 原理：GitCommitGateway 用 --no-verify 绕过所有 pre-commit hooks
    # 所以本 hook 运行本身就说明是裸 git commit
    # 唯一合法绕过：git commit --no-verify（conscious bypass，由 post-commit 审计 reconciler 追踪）
    print(
        "GATE-COMMIT-GW: BLOCKED — 检测到裸 git commit（未经 GitCommitGateway）\n"
        "  根因: 多 AI session 共享 git index，裸 commit 会导致幽灵提交\n"
        "  治本: 所有 commit MUST 经 GitCommitGateway\n"
        "  正确方式:\n"
        "    python scripts/git_commit.py --session <id> --files <f1,f2> --message <msg>\n"
        "  或代码调用:\n"
        "    from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway\n"
        "    GitCommitGateway().commit(session_id, files, message)\n"
        "  如确需绕过（如修复历史）: git commit --no-verify（conscious bypass，"
        "由 GATE-COMMIT-GW-AUDIT 审计 reconciler 追踪）",
        file=sys.stderr,
    )
    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
