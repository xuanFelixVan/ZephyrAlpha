"""
detect_deprecated_overdue.py — 废弃超期检测

对标：PS-STD-009 §7（status:deprecated 距今 >= 180 天应自动归档）

检测内容：
- 扫描所有 status=deprecated 的文件
- 计算距今天数，>= 180 天标记为待归档

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT, SCAN_EXTENSIONS_MD_YAML
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse
from datetime import datetime

ARCHIVE_THRESHOLD_DAYS = 180

def scan_deprecated_overdue() -> list[dict]:
    """scan deprecated overdue."""
    findings = []
    """扫描并返回发现列表."""
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"

    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD_YAML):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue

        status = fm.get("status", "")
        if status != "deprecated":
            continue

        date_str = fm.get("date", "")
        if not date_str:
            continue

        try:
            dep_date = datetime.strptime(str(date_str), "%Y-%m-%d")
        except ValueError:
            continue

        days = (datetime.now() - dep_date).days
        if days >= ARCHIVE_THRESHOLD_DAYS:
            rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
            findings.append(
                {
                    "file": rel,
                    "module_id": fm.get("module_id", ""),
                    "days": days,
                    "date": str(date_str),
                    "severity": "MEDIUM",
                }
            )

    return findings
    """scan deprecated overdue."""

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="废弃超期检测（PS-STD-009 §7）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings = scan_deprecated_overdue()

    if findings:
        print(f"\n[DEPR-OVERDUE] {len(findings)} 个废弃文件超过 {ARCHIVE_THRESHOLD_DAYS} 天未归档:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['module_id']} ({f['file']})", file=sys.stderr)
            print(f"    已废弃 {f['days']} 天（日期: {f['date']}）", file=sys.stderr)
    else:
        print("[DEPR-OVERDUE] 无超期废弃文件", file=sys.stderr)

    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if findings else 0)

if __name__ == "__main__":
    main()
