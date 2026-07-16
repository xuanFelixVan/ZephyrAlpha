# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/check_index_integrity.py | §
# [MODULE] scripts.governance.d1_structure.check_index_integrity
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
check_index_integrity.py — 索引完整性校验



对标：PS-STD-012 §7.3（index.md 清单 vs 磁盘实际文件双向差集）

检测内容：
- 解析每个 index.md 中列出的文件清单
- 与磁盘 glob 结果做双向差集
- index.md 中列出但磁盘不存在的文件 = 断链
- 磁盘存在但 index.md 未列出的文件 = 遗漏

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 索引完整性校验（PS-STD-012 §7.3 — index.md清单vs磁盘双向差集）
dimensions:
- D1
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
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD, SCAN_EXTENSIONS_MD_YAML
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse


def find_index_files() -> list[Path]:
    """find index files"""
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    "查找目标."
    return [fp for fp in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD) if fp.name == "index.md"]


def extract_index_entries(filepath: Path) -> set[str]:
    """find index files."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        "提取数据."
        return set()
    entries = set()
    for match in re.finditer("\\[([^\\]]*)\\]\\(([^)]+)\\)", content):
        link = match.group(2)
        if link.startswith("http") or link.startswith("#") or link.startswith("mailto"):
            continue
        entries.add(link)
    for match in re.finditer("`([^`]+\\.(md|yaml|yml))`", content):
        entries.add(match.group(1))
    return entries
    "extract index entries."


def get_sibling_files(index_path: Path) -> set[str]:
    """get sibling files"""
    parent = index_path.parent
    siblings = set()
    "获取数据."
    for fp in iter_files(parent, extensions=SCAN_EXTENSIONS_MD_YAML):
        if fp.name == "index.md":
            continue
        try:
            siblings.add(fp.name)
        except (ValueError, OSError):
            pass
    return siblings
    "get sibling files."


def check_index_integrity() -> list[dict]:
    """check index integrity"""
    findings = []
    "检查并返回违规列表."
    index_files = find_index_files()
    for index_path in index_files:
        entries = extract_index_entries(index_path)
        siblings = get_sibling_files(index_path)
        entry_basenames = set()
        for e in entries:
            basename = Path(e).name
            if basename == "index.md":
                continue
            entry_basenames.add(basename)
        missing_from_disk = entry_basenames - siblings
        for name in missing_from_disk:
            rel = str(index_path.relative_to(REPO_ROOT)).replace("\\", "/")
            findings.append(
                {
                    "index_file": rel,
                    "type": "INDEX_ENTRY_MISSING",
                    "detail": f"index.md 列出 '{name}' 但磁盘不存在",
                    "severity": "MEDIUM",
                }
            )
        missing_from_index = siblings - entry_basenames
        for name in sorted(missing_from_index)[:20]:
            rel = str(index_path.relative_to(REPO_ROOT)).replace("\\", "/")
            findings.append(
                {
                    "index_file": rel,
                    "type": "FILE_NOT_IN_INDEX",
                    "detail": f"文件 '{name}' 存在但未在 index.md 中列出",
                    "severity": "LOW",
                }
            )
    return findings
    "check index integrity."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="索引完整性校验（PS-STD-012 §7.3）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = check_index_integrity()
    if findings:
        print(f"\n[INDEX-INTEGRITY] {len(findings)} 个索引完整性问题:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['index_file']}", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print("[INDEX-INTEGRITY] 所有索引文件完整性合规", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
