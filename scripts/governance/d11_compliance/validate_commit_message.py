# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_commit_message.py | §
# [MODULE] scripts.governance.d11_compliance.validate_commit_message
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
validate_commit_message.py — Conventional Commits 校验（commit-msg hook）+ AI 归因 trailer 检测（warn-only）



对标: Conventional Commits v1.0.0 (conventionalcommits.org)
     feat/fix/docs/style/refactor/perf/test/chore/ci/build/revert

合法格式:
  type(scope): description
  type: description

AI 归因 trailer（裁定4：2026-06-25，warn-only）:
  检测 commit message 是否包含 AI 归因 trailer，缺失时仅警告不阻断。
  合法 trailer 格式（git trailer convention）:
    Co-Authored-By: Trae AI <trae@example.com>
    AI-Generated-By: GLM-5.2
  目的: AI 生成 commit 的可追溯性——100% AI 开发项目需区分人工与 AI commit。

exit codes: 0=合法, 1=不合法
"""

from __future__ import annotations

from _shared.constants import EXIT_FINDINGS, EXIT_PASS

__manifest__ = """
args:
- --warn-only
description: Conventional Commits 格式校验（commit-msg hook）— type ∈ {feat,fix,docs,style,refactor,perf,test,chore,ci,build,revert}
dimensions:
- D11
priority: P1
timeout_seconds: 5
warn_only: false
"""


import argparse
import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)" r"(\([a-zA-Z0-9_.-]+\))?" r": .{1,200}$"
)

# AI 归因 trailer 模式（git trailer convention: Key: Value）
AI_TRAILER_PATTERN = re.compile(r"^(Co-Authored-By|AI-Generated-By|Generated-By):\s*.+", re.MULTILINE)

# AI 归因 trailer 建议：邮箱可经环境变量覆盖（默认 ai 归因地址）
_COAUTHOR_EMAIL = os.getenv("TRAE_AI_EMAIL", "trae-ai@local")
_COAUTHOR_TEMPLATE = f"Co-Authored-By: Trae AI <{_COAUTHOR_EMAIL}>"


def check_ai_attribution(full_msg: str) -> bool:
    """检查 commit message 是否包含 AI 归因 trailer。返回 True=存在。"""
    return bool(AI_TRAILER_PATTERN.search(full_msg))


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="Conventional Commits 格式校验（commit-msg hook）")
    parser.add_argument(
        "msg_file",
        nargs="?",
        help="commit message 文件路径（commit-msg hook 自动传入）",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="警告模式：发现违规不阻塞（exit 0）— 用于质量合规扫描",
    )
    args = parser.parse_args()

    if not args.msg_file:
        print("[ERROR] commit-msg hook: 缺少 commit message 文件路径", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)

    try:
        with open(args.msg_file, encoding="utf-8") as f:
            full_msg = f.read()
        msg = full_msg.splitlines()[0].strip() if full_msg.strip() else ""
    except (OSError, FileNotFoundError):
        print(f"[ERROR] 无法读取 commit message: {args.msg_file}", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)

    if not msg:
        print("[ERROR] commit message 为空", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)

    if msg.startswith("Merge "):
        sys.exit(EXIT_PASS)

    if not PATTERN.match(msg):
        print(f"\n[COMMIT-MSG] 不合法的 commit message 格式: {msg}", file=sys.stderr)
        print("合法格式: type(scope): description", file=sys.stderr)
        print("合法 type: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert\n", file=sys.stderr)
        if args.warn_only:
            print("⚠ --warn-only 模式: 仅报告，不阻断", file=sys.stderr)
            sys.exit(EXIT_PASS)
        sys.exit(EXIT_FINDINGS)

    # AI 归因 trailer 检测（裁定4：warn-only，不阻断 commit）
    if not check_ai_attribution(full_msg):
        print("[COMMIT-MSG] ⚠ 缺少 AI 归因 trailer", file=sys.stderr)
        print("  建议在 commit message 末尾添加:", file=sys.stderr)
        print(f"    {_COAUTHOR_TEMPLATE}", file=sys.stderr)
        print("  目的: 100% AI 开发项目的 commit 可追溯性\n", file=sys.stderr)

    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
