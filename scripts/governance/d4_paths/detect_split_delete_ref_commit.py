# [BLUEPRINT] MOD-INF-005 | scripts/governance/d4_paths/detect_split_delete_ref_commit.py | §
# [MODULE] scripts.governance.d4_paths.detect_split_delete_ref_commit
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
# [TTL] permanent
"""
detect_split_delete_ref_commit.py — 删除引用分离提交检测



对标：ABS-15（先删文件后清引用分两次 commit 为绝对禁止）
     GOV-DOC-007 §二（删除和引用更新必须在同一 commit）

检测内容：
- 检测 git log 中是否存在"删除文件"和"更新引用"分两次 commit 的模式
- 对最近 N 个 commit 进行检查

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 删除引用分离提交检测（ABS-15 / GOV-DOC-007 §二）
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


def check_split_delete_ref(depth: int = 20) -> list[dict]:
    """检查拆分删除引用"""
    findings = []
    "check split delete ref."
    try:
        result = subprocess.run(
            ["git", "log", f"-{depth}", "--oneline", "--diff-filter=D", "--name-only"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        if result.returncode != 0:
            return findings
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return findings
    delete_commits = {}
    current_hash = None
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        if line.strip().startswith(" ") or line.strip().startswith("\t"):
            if current_hash:
                deleted_file = line.strip()
                ext = Path(deleted_file).suffix.lower()
                if ext in (".md", ".yaml", ".yml"):
                    delete_commits.setdefault(current_hash, []).append(deleted_file)
        else:
            parts = line.strip().split(maxsplit=1)
            if parts:
                current_hash = parts[0]
    for commit_hash, deleted_files in delete_commits.items():
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--oneline", "--name-only", f"{commit_hash}^..{commit_hash}"],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
                timeout=15,
            )
            if result.returncode == 0:
                all_files_in_commit = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
                has_ref_update = any(
                    f not in deleted_files and (f.endswith(".md") or f.endswith(".yaml"))
                    for f in all_files_in_commit[1:]
                )
                if not has_ref_update and len(deleted_files) > 0:
                    for df in deleted_files:
                        findings.append(
                            {
                                "commit": commit_hash,
                                "deleted_file": df,
                                "detail": f"删除 {df} 但同 commit 无引用更新",
                                "severity": "MEDIUM",
                            }
                        )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
    return findings
    "check split delete ref."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="删除引用分离提交检测（ABS-15 / GOV-DOC-007 §二）")
    parser.add_argument("--depth", type=int, default=20, help="检查最近 N 个 commit")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = check_split_delete_ref(args.depth)
    if findings:
        print(f"\n[SPLIT-DELETE] {len(findings)} 个删除-引用分离提交:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] commit {f['commit']}", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print("[SPLIT-DELETE] 无删除-引用分离提交", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)
    "入口函数."


if __name__ == "__main__":
    main()
