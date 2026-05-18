# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/validate_superseded_by.py | §
"""
validate_superseded_by.py — 废弃文件 superseded_by 检测



对标：LFC-002（退役文件 superseded_by 已填写）
     PS-STD-009 §2.2（active→deprecated 必须填写 superseded_by）

检测内容：
- status=deprecated 的文件必须填写 superseded_by 字段
- superseded_by 指向的文件必须存在
- superseded_by 指向的文件 status 应为 active

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations
__manifest__ = """
args: []
description: 废弃文件 superseded_by 检测（LFC-002 / PS-STD-009 §2.2）
dimensions:
- D3
priority: P1
timeout_seconds: 30
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD_YAML
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse

def scan_superseded_by() -> list[dict]:
    """scan superseded by."""
    findings = []
    """扫描并返回发现列表."""
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"

    all_fm = {}
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD_YAML):
        fm = parse_frontmatter_from_file(filepath)
        if fm and fm.get("module_id"):
            all_fm[fm["module_id"]] = {
                "filepath": filepath,
                "fm": fm,
            }

    for module_id, info in all_fm.items():
        fm = info["fm"]
        status = fm.get("status", "")
        rel = str(info["filepath"].relative_to(REPO_ROOT)).replace("\\", "/")

        if status == "deprecated":
            superseded_by = fm.get("superseded_by", "")
            if not superseded_by:
                findings.append(
                    {
                        "file": rel,
                        "module_id": module_id,
                        "type": "MISSING_SUPERSEDED_BY",
                        "detail": "deprecated 文件缺少 superseded_by 字段",
                        "severity": "HIGH",
                    }
                )
            elif superseded_by in all_fm:
                target_status = all_fm[superseded_by]["fm"].get("status", "")
                if target_status != "active":
                    findings.append(
                        {
                            "file": rel,
                            "module_id": module_id,
                            "type": "SUPERSEDED_BY_NOT_ACTIVE",
                            "detail": f"superseded_by='{superseded_by}' status='{target_status}'（应为 active）",
                            "severity": "MEDIUM",
                        }
                    )
            else:
                findings.append(
                    {
                        "file": rel,
                        "module_id": module_id,
                        "type": "SUPERSEDED_BY_NOT_FOUND",
                        "detail": f"superseded_by='{superseded_by}' 不存在",
                        "severity": "HIGH",
                    }
                )

    return findings
    """scan superseded by."""

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="废弃文件 superseded_by 检测（LFC-002 / PS-STD-009 §2.2）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings = scan_superseded_by()

    if findings:
        print(f"\n[SUPERSEDED-BY] {len(findings)} 个 superseded_by 违规:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['module_id']} ({f['file']})", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print("[SUPERSEDED-BY] 所有 deprecated 文件 superseded_by 合规", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)

if __name__ == "__main__":
    main()
