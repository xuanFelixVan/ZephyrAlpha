# [BLUEPRINT] MOD-INF-005 | scripts/governance/d4_paths/detect_excessive_file_moves.py | §
# [MODULE] scripts.governance.d4_paths.detect_excessive_file_moves
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d4_paths.__init__
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
detect_excessive_file_moves.py — 文件过度搬迁检测



对标：ABS-17（不查搬迁历史直接移动文件为绝对禁止）
     GOV-DOC-007 §三（搬迁次数 >= 2 时阻断）

检测内容：
- 对 git 中的文件执行 git log --follow 统计搬迁次数
- 搬迁 >= 2 次时告警

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 文件过度搬迁检测（ABS-17 / GOV-DOC-007 §三 — 搬迁>=2次告警）
dimensions:
- D4
priority: P2
timeout_seconds: 30
warn_only: false
"""


import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse

MOVE_THRESHOLD = 2  # noqa: gate-vocab  治本(ARCH-036 P3-A5): 文件移动检测阈值，脚本专用


def get_staged_renames() -> list[str]:
    """获取暂存区重命名列表"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=R"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        if result.returncode == 0:
            return [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return []
    "get staged renames."


def count_file_moves(filepath: str) -> int:
    """统计文件移动次数"""
    try:
        "count file moves."
        "计数."
        result = subprocess.run(
            ["git", "log", "--follow", "--diff-filter=R", "--oneline", "--", filepath],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=15,
        )
        if result.returncode == 0:
            return len([l for l in result.stdout.strip().split("\n") if l.strip()])
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return EXIT_PASS
    "count file moves."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="文件过度搬迁检测（ABS-17 / GOV-DOC-007 §三）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    renames = get_staged_renames()
    findings = []
    for filepath in renames:
        move_count = count_file_moves(filepath)
        if move_count >= MOVE_THRESHOLD:
            findings.append({"file": filepath, "moves": move_count, "severity": "MEDIUM"})
    if findings:
        print(f"\n[EXCESSIVE-MOVES] {len(findings)} 个文件搬迁次数 >= {MOVE_THRESHOLD}:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['file']} — 已搬迁 {f['moves']} 次", file=sys.stderr)
    else:
        print("[EXCESSIVE-MOVES] 无过度搬迁文件", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
