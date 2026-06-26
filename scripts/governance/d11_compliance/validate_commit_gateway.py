# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_commit_gateway.py | §gate-commit-gw
# [MODULE] scripts.governance.d11_compliance.validate_commit_gateway
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__; zephyr.governance.git_commit_gateway
# [CONSUMERS] .pre-commit-config.yaml (GATE-COMMIT-GW hook)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 检测裸 git commit（未经 GitCommitGateway）；经 gateway 的 commit 用 --no-verify 绕过本门禁；裸 commit 被阻断 exit 1
# [MODIFY-GUARD] 检测逻辑：环境变量 ZEPHYR_COMMIT_GATEWAY=1 或 commit message 含 [GW:...] 标记
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=经gateway放行; exit 1=裸commit阻断; exit 2=脚本错误
# [TESTS] tests/test_git_commit_gateway.py
# [A_module] module_id=MOD-GOV-validate_commit_gateway | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""validate_commit_gateway.py — GATE-COMMIT-GW 门禁（OPS-2026062513）

检测裸 git commit，强制走 GitCommitGateway（根治幽灵提交）。

检测逻辑（任一满足即放行）:
1. 环境变量 ZEPHYR_COMMIT_GATEWAY=1（GitCommitGateway.commit() 设置）
2. commit message 含 [GW:<session_id>] 标记（GitCommitGateway 自动追加）

工作原理:
- GitCommitGateway.commit() 用 git commit --no-verify 绕过 pre-commit hooks
  → 本门禁对 gateway commit 不触发（fast path）
- 裸 git commit（无 --no-verify）会触发 pre-commit hooks
  → 本门禁检测到 env var 未设置 → 阻断 exit 1

对标: validate_commit_message.py（Conventional Commits 校验，commit-msg stage）
区别: 本脚本检测 commit 路径（是否经 gateway），非 message 格式

exit codes: 0=经gateway放行, 1=裸commit阻断, 2=脚本错误
"""

from __future__ import annotations

__manifest__ = """
args:
- --commit-msg-file
description: GATE-COMMIT-GW门禁——检测裸git commit，强制走GitCommitGateway（环境变量或GW标记）
dimensions:
- D11
priority: P1
timeout_seconds: 5
warn_only: false
"""

import os
import re
import sys
from pathlib import Path

# sys.path 必须在 from _shared 导入之前设置（namespace package 需父目录在 path 中）
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

_GATEWAY_ENV = "ZEPHYR_COMMIT_GATEWAY"
_GW_MARKER_PATTERN = re.compile(r"\[GW:[^\]]+\]")


def _check_env_var() -> bool:
    """检测环境变量 ZEPHYR_COMMIT_GATEWAY=1。"""
    return os.environ.get(_GATEWAY_ENV) == "1"


def _check_commit_message(msg_file: str | None) -> bool:
    """检测 commit message 是否含 [GW:...] 标记。

    Args:
        msg_file: commit-msg 文件路径（commit-msg stage 传入），None 则跳过。

    Returns:
        True=含 GW 标记, False=不含或无法读取。
    """
    if not msg_file:
        return False
    try:
        content = Path(msg_file).read_text(encoding="utf-8", errors="replace")
        return bool(_GW_MARKER_PATTERN.search(content))
    except OSError:
        return False


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="GATE-COMMIT-GW: 检测裸 git commit，强制走 GitCommitGateway",
    )
    parser.add_argument(
        "--commit-msg-file",
        default=None,
        help="commit-msg 文件路径（commit-msg stage 传入，可选）",
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="pre-commit 传入的文件列表（本门禁不使用，仅兼容）",
    )
    args = parser.parse_args()

    # 检测 1: 环境变量
    if _check_env_var():
        print("GATE-COMMIT-GW: PASS (ZEPHYR_COMMIT_GATEWAY=1)")
        return EXIT_PASS

    # 检测 2: commit message GW 标记
    if _check_commit_message(args.commit_msg_file):
        print("GATE-COMMIT-GW: PASS (commit message 含 [GW:...] 标记)")
        return EXIT_PASS

    # 阻断：裸 commit
    print(
        "GATE-COMMIT-GW: BLOCKED — 检测到裸 git commit（未经 GitCommitGateway）\n"
        "  根因: 多 AI session 共享 git index，裸 commit 会导致幽灵提交\n"
        "  治本: 所有 commit MUST 经 GitCommitGateway\n"
        "  正确方式:\n"
        "    python scripts/git_commit.py --session <id> --files <f1,f2> --message <msg>\n"
        "  或代码调用:\n"
        "    from zephyr.governance.git_commit_gateway import GitCommitGateway\n"
        "    GitCommitGateway().commit(session_id, files, message)\n"
        "  如确需绕过（如修复历史）: git commit --no-verify（ consciously bypass）",
        file=sys.stderr,
    )
    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
