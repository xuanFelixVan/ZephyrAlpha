# [BLUEPRINT] MOD-INF-005 | scripts/governance/d4_paths/detect_deprecated_path_writes.py | §
# [MODULE] scripts.governance.d4_paths.detect_deprecated_path_writes
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
detect_deprecated_path_writes.py — 废弃路径写入检测



对标：ABS-18（在废弃路径下写入新文件为绝对禁止）

检测内容：
- git staged/working 新文件是否在废弃路径下
- 废弃路径列表：_DO_NOT_USE_old_tree/、docs/（老树根目录）等

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 废弃路径写入检测（ABS-18 — 禁止在废弃路径下新建文件）
dimensions:
- D1
- D4
priority: P0
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

DEPRECATED_PATH_PREFIXES = [
    "_DO_NOT_USE_old_tree/",
    "_DO_NOT_USE_old_tree\\",
    "docs/00_",
    "docs/01_",
    "docs/02_",
    "docs/03_",
    "docs/04_",
    "docs/05_",
    "docs/06_",
    "docs/07_",
    "docs/08_",
    "docs/09_",
]
ALLOWED_IN_DOCS_ROOT = {"docs/migration-declaration.md", "docs/index.md", "docs/README.md"}


def get_new_files() -> list[str]:
    """获取新增文件列表"""
    new_files = []
    "get new files."
    for flag in ["--cached", ""]:
        "获取数据."
        try:
            cmd = ["git", "diff"]
            if flag:
                cmd.append(flag)
            cmd.extend(["--name-only", "--diff-filter=A"])
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30)
            if result.returncode == 0:
                new_files.extend(line.strip() for line in result.stdout.strip().split("\n") if line.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
    return list(set(new_files))
    "get new files."


def check_deprecated_path_writes() -> list[dict]:
    """check deprecated path writes."""
    findings = []
    "检查并返回违规列表."
    new_files = get_new_files()
    for rel_path in new_files:
        norm = rel_path.replace("\\", "/")
        if norm in ALLOWED_IN_DOCS_ROOT:
            continue
        for prefix in DEPRECATED_PATH_PREFIXES:
            norm_prefix = prefix.replace("\\", "/")
            if norm.startswith(norm_prefix):
                findings.append({"file": rel_path, "deprecated_prefix": prefix.rstrip("/\\"), "severity": "CRITICAL"})
                break
    return findings
    "check deprecated path writes."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="废弃路径写入检测（ABS-18）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = check_deprecated_path_writes()
    if findings:
        print(f"\n[DEPR-PATH-WRITE] {len(findings)} 个新文件写入废弃路径！", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['file']}", file=sys.stderr)
            print(f"    废弃路径: {f['deprecated_prefix']}", file=sys.stderr)
    else:
        print("[DEPR-PATH-WRITE] 无废弃路径写入", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
