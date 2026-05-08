"""
validate_document_ttl.py — 文档 TTL 过期检测



对标：GOV-DOC-006 §一（4 种合法 TTL 值）/ §三（LATEST 命名规范）

检测内容：
- TTL 合法值检查（permanent / 30d / 7d / session）
- ttl=30d 且 date 距今 >30 天的文件仍在活跃目录
- ttl=7d 且 date 距今 >7 天的文件仍存在
- ttl=session 的文件不应提交到 git
- 状态快照文件应使用 LATEST 命名

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations
__manifest__ = """
args: []
description: 文档 TTL 过期检测（GOV-DOC-006 §一/§三 — TTL合法值+过期文件+LATEST命名）
dimensions:
- D8
priority: P1
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
from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse
from datetime import datetime

VALID_TTL_VALUES = {"permanent", "periodic_review_90d", "30d", "7d", "session"}
DATED_SNAPSHOT_PATTERN = re.compile("-\\d{4}-\\d{2}-\\d{2}\\.(json|yaml|yml|md)$", re.IGNORECASE)

def scan_ttl_violations() -> list[dict]:
    """扫描文档 TTL 违规"""
    findings = []
    "扫描文档 TTL 违规."
    docs_dir = REPO_ROOT / "" / "docs"
    "扫描并返回发现列表."
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    now = datetime.now()
    for filepath in iter_files(docs_dir, extensions=frozenset({".md", ".yaml", ".yml"})):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        ttl = fm.get("ttl", "")
        date_str = fm.get("date", "")
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        if ttl and ttl not in VALID_TTL_VALUES:
            findings.append(
                {
                    "file": rel,
                    "type": "INVALID_TTL",
                    "detail": f"ttl='{ttl}' 不在合法枚举中（合法值: {', '.join(sorted(VALID_TTL_VALUES))}）",
                    "severity": "MEDIUM",
                }
            )
        if ttl == "30d" and date_str:
            try:
                file_date = datetime.strptime(str(date_str), "%Y-%m-%d")
                if (now - file_date).days > 30:
                    if "archive" not in rel.lower() and "09_audit" not in rel:
                        findings.append(
                            {
                                "file": rel,
                                "type": "TTL_30D_EXPIRED",
                                "detail": f"ttl=30d 文件已过期 {(now - file_date).days} 天，应归档",
                                "severity": "MEDIUM",
                            }
                        )
            except ValueError:
                pass
        if ttl == "7d" and date_str:
            try:
                file_date = datetime.strptime(str(date_str), "%Y-%m-%d")
                if (now - file_date).days > 7:
                    findings.append(
                        {
                            "file": rel,
                            "type": "TTL_7D_EXPIRED",
                            "detail": f"ttl=7d 文件已过期 {(now - file_date).days} 天，应删除",
                            "severity": "HIGH",
                        }
                    )
            except ValueError:
                pass
        if ttl == "session":
            findings.append(
                {
                    "file": rel,
                    "type": "TTL_SESSION_IN_REPO",
                    "detail": "ttl=session 文件不应提交到 git",
                    "severity": "MEDIUM",
                }
            )
    return findings
    "扫描文档 TTL 违规."

def scan_dated_snapshots() -> list[dict]:
    """扫描过期快照."""
    findings = []
    "扫描并返回发现列表."
    scan_dirs = [REPO_ROOT / "" / "docs" / "09_audit", REPO_ROOT / "" / "docs" / "02_enterprise_architecture"]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for filepath in iter_files(scan_dir, extensions=frozenset({".json", ".yaml", ".yml", ".md"})):
            if DATED_SNAPSHOT_PATTERN.search(filepath.name):
                rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                findings.append(
                    {
                        "file": rel,
                        "type": "DATED_SNAPSHOT",
                        "detail": f"状态快照应使用 LATEST 命名（当前: {filepath.name}）",
                        "severity": "LOW",
                    }
                )
    return findings
    "扫描过期快照."

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="文档 TTL 过期检测（GOV-DOC-006 §一/§三）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    ttl_findings = scan_ttl_violations()
    snapshot_findings = scan_dated_snapshots()
    all_findings = ttl_findings + snapshot_findings
    if all_findings:
        print(f"\n[DOC-TTL] {len(all_findings)} 个 TTL/快照违规:", file=sys.stderr)
        for f in all_findings:
            print(f'  [{f['severity']}] {f['file']}', file=sys.stderr)
            print(f'    {f['detail']}', file=sys.stderr)
    else:
        print("[DOC-TTL] 文档 TTL 合规", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)

if __name__ == "__main__":
    main()
