"""
validate_commit_message.py — Conventional Commits 校验（commit-msg hook）

对标: Conventional Commits v1.0.0 (conventionalcommits.org)
     feat/fix/docs/style/refactor/perf/test/chore/ci/build/revert

合法格式:
  type(scope): description
  type: description

exit codes: 0=合法, 1=不合法
"""

from __future__ import annotations

import argparse
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
        sys.exit(1)

    try:
        with open(args.msg_file, encoding="utf-8") as f:
            msg = f.readline().strip()
    except (OSError, FileNotFoundError):
        print(f"[ERROR] 无法读取 commit message: {args.msg_file}", file=sys.stderr)
        sys.exit(1)

    if not msg:
        print("[ERROR] commit message 为空", file=sys.stderr)
        sys.exit(1)

    if msg.startswith("Merge "):
        sys.exit(0)

    if not PATTERN.match(msg):
        print(f"\n[COMMIT-MSG] 不合法的 commit message 格式: {msg}", file=sys.stderr)
        print("合法格式: type(scope): description", file=sys.stderr)
        print("合法 type: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert\n", file=sys.stderr)
        if args.warn_only:
            print("⚠ --warn-only 模式: 仅报告，不阻断", file=sys.stderr)
            sys.exit(0)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
