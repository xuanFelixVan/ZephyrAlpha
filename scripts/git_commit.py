# [BLUEPRINT] MOD-INF-005 | scripts/git_commit.py | §ghost-commit-gateway-cli
# [MODULE] scripts.git_commit
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 全项目唯一合法 git commit CLI 入口；封装 GitCommitGateway；禁止裸 git commit（GATE-COMMIT-GW 门禁）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=commit成功; exit 1=commit失败/无变更; exit 2=锁超时/stash冲突; exit 3=永久区晋升阻断
# [TESTS] tests/test_git_commit_gateway.py
# [A_module] module_id=MOD-GOV-git_commit_cli | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""git_commit.py — GitCommitGateway CLI 封装（OPS-2026062512）

全项目唯一合法 git commit 命令行入口。封装 GitCommitGateway，串行化所有 commit。

用法::

    python scripts/git_commit.py --session <id> --files <f1,f2> --message <msg>
    python scripts/git_commit.py --session sess-001 --files src/a.py,src/b.py --message "feat: add"

对标: scripts/git_guard.py（git 命令透传封装），区别：
- git_guard.py 透传 git 子命令（绕过 Trae 弹窗）
- git_commit.py 强制走 GitCommitGateway（串行锁+stash 隔离+GW 标记）

exit codes: 0=commit成功, 1=commit失败/无变更, 2=锁超时/stash冲突
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.git_commit_gateway import (  # noqa: E402
    CommitStatus,
    GitCommitGateway,
)

logger = logging.getLogger(__name__)


def _parse_files(files_arg: str) -> list[str]:
    """解析逗号分隔的文件列表，归一化为绝对路径。"""
    if not files_arg:
        return []
    parts = [f.strip() for f in files_arg.split(",") if f.strip()]
    # 归一化为绝对路径（相对路径基于 cwd 解析）
    return [str(Path(f).resolve()) for f in parts]


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="git_commit.py",
        description="GitCommitGateway CLI——全项目唯一合法 git commit 入口（串行锁+stash隔离+GW标记）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            '  python scripts/git_commit.py --session sess-001 --files src/a.py,src/b.py --message "feat: add"\n'
            "\n"
            "对标 git_guard.py: git_guard 透传 git 子命令；本脚本强制走 GitCommitGateway。\n"
            "exit codes: 0=成功, 1=失败/无变更, 2=锁超时/stash冲突, 3=永久区晋升阻断"
        ),
    )
    parser.add_argument(
        "--session",
        required=True,
        help="AI session 标识（用于 GW 标记 + stash message）",
    )
    parser.add_argument(
        "--files",
        required=True,
        help="本次 commit 的文件列表，逗号分隔（相对路径基于 cwd 解析）",
    )
    parser.add_argument(
        "--message",
        required=True,
        help="commit message（不含 GW 标记，自动追加 [GW:<session>]）",
    )
    parser.add_argument(
        "--project-root",
        default=str(_PROJECT_ROOT),
        help="项目根目录（默认: 脚本所在仓库根）",
    )
    parser.add_argument(
        "--allow-promote",
        action="store_true",
        default=False,
        help="批准新文件晋升到永久区（docs/01_policies/、02_enterprise_architecture/、"
             "03_modules/、08_knowledge/）。AI 不得自行使用——须用户终端手动指定。",
    )
    args = parser.parse_args()

    files = _parse_files(args.files)
    if not files:
        print("ERROR: --files 不能为空", file=sys.stderr)
        return 1

    # 校验文件存在（允许已跟踪但工作区已删除的文件，用于 rename/delete 场景）
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        import subprocess as _sp
        truly_missing = []
        for f in missing:
            rel = os.path.relpath(f, args.project_root)
            chk = _sp.run(
                ["git", "ls-files", "--error-unmatch", "--", rel],
                capture_output=True, cwd=args.project_root,
            )
            if chk.returncode != 0:
                truly_missing.append(f)
        if truly_missing:
            print(f"ERROR: 文件不存在且未被 git 跟踪: {truly_missing}", file=sys.stderr)
            return 1
        logger.info("以下文件已跟踪但工作区已删除（将作为删除提交）: %s", missing)

    try:
        gw = GitCommitGateway(project_root=args.project_root)
    except Exception as e:
        print(f"ERROR: GitCommitGateway 初始化失败: {e}", file=sys.stderr)
        return 2

    # Phase 2: claim files 激活 session 隔离 stash
    claimed = gw.claim_files(args.session, files)
    try:
        result = gw.commit(
            session_id=args.session,
            files=files,
            message=args.message,
            allow_promote=args.allow_promote,
        )
    finally:
        gw.release_files(args.session, claimed)

    if result.status == CommitStatus.OK:
        print(f"OK: {result.message} (hash={result.commit_hash[:8]})")
        return 0
    elif result.status == CommitStatus.NOTHING_TO_COMMIT:
        print(f"SKIP: {result.message}")
        return 1
    elif result.status == CommitStatus.LOCK_TIMEOUT:
        print(f"LOCK_TIMEOUT: {result.message}", file=sys.stderr)
        return 2
    elif result.status == CommitStatus.STASH_CONFLICT:
        print(f"STASH_CONFLICT: {result.message}", file=sys.stderr)
        print(f"  stash_ref={result.stash_ref} (数据保留在 stash，未丢失)", file=sys.stderr)
        return 2
    elif result.status == CommitStatus.PROMOTION_BLOCKED:
        print(f"PROMOTION_BLOCKED: {result.message}", file=sys.stderr)
        print(
            "  如确认晋升到永久区，请在终端手动添加 --allow-promote 重新执行。",
            file=sys.stderr,
        )
        return 3
    else:  # COMMIT_FAILED
        print(f"FAILED: {result.message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
