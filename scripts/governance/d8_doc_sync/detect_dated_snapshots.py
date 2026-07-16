# [BLUEPRINT] MOD-INF-005 | scripts/governance/d8_doc_sync/detect_dated_snapshots.py | §
# [MODULE] scripts.governance.d8_doc_sync.detect_dated_snapshots
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d8_doc_sync.__init__
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
detect_dated_snapshots.py — 带日期快照文件检测



对标：GOV-DOC-006 §三（状态快照文件必须使用 LATEST 命名）

检测内容：
- 扫描 _working/audit/ 和 02_enterprise_architecture/snapshots/ 下带日期的快照文件
- 状态快照应使用 *-LATEST.json/yaml/md 命名

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 带日期快照文件检测（GOV-DOC-006 §三 — 应使用LATEST命名）
dimensions:
- D8
priority: P2
timeout_seconds: 30
warn_only: false
"""


import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_DATA
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse

DATED_PATTERN = re.compile(r"-\d{4}-\d{2}-\d{2}\.(json|yaml|yml|md)$", re.IGNORECASE)


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="带日期快照文件检测（GOV-DOC-006 §三）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings = []
    scan_dirs = [
        REPO_ROOT / "" / "docs" / "_working" / "audit",
        REPO_ROOT / "" / "docs" / "02_enterprise_architecture",
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for filepath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_DATA):
            if DATED_PATTERN.search(filepath.name):
                rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                findings.append(
                    {
                        "file": rel,
                        "name": filepath.name,
                        "severity": "LOW",
                    }
                )

    if findings:
        print(f"\n[DATED-SNAPSHOT] {len(findings)} 个带日期的快照文件:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['file']}", file=sys.stderr)
            print(f"    应使用 LATEST 命名替代 {f['name']}", file=sys.stderr)
    else:
        print("[DATED-SNAPSHOT] 无带日期的快照文件", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
