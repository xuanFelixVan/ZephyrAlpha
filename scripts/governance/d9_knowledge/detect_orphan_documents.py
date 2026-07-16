# [BLUEPRINT] MOD-INF-005 | scripts/governance/d9_knowledge/detect_orphan_documents.py | §
# [MODULE] scripts.governance.governance.d9_knowledge.detect_orphan_documents
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d9_knowledge.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] read-only audit script; no file modifications
# [MODIFY-GUARD] header fields; core validation logic
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
detect_orphan_documents.py — 孤立文档检测



对标：DOC-008#4（自创建后 > 30 天无任何文件依赖/引用的文件应审查）

检测内容：
- 构建反向引用图（哪些文件被其他文件 depends_on 引用）
- 无入边的文件 = 孤立文档
- 排除 index 文件（index.md 本身就是入口，不需要被引用）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 孤立文档检测（DOC-008#4 — 无入边引用的文件）
dimensions:
- D9
priority: P1
timeout_seconds: 60
warn_only: false
"""


import re
import sys
from collections import defaultdict
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


def build_reference_graph() -> tuple[dict[str, set[str]], dict[str, str]]:
    """构建引用关系图."""
    referenced_by: dict[str, set[str]] = defaultdict(set)
    """构建数据结构."""
    module_to_file: dict[str, str] = {}

    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"

    all_files = []
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD_YAML):
        fm_result = parse_frontmatter_from_file(filepath)
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        fm = fm_result[0] if fm_result else {}
        module_id = fm.get("module_id", "") if fm else ""
        depends_on = fm.get("depends_on", []) if fm else []

        if module_id:
            module_to_file[module_id] = rel

        all_files.append(
            {
                "rel": rel,
                "module_id": module_id,
                "depends_on": depends_on,
                "filepath": filepath,
            }
        )

        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
            for match in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", content):
                link = match.group(2)
                if not link.startswith("http") and not link.startswith("#"):
                    referenced_by[link].add(rel)
        except (OSError, UnicodeDecodeError):
            pass

    for info in all_files:
        deps = info["depends_on"]
        if isinstance(deps, list):
            for dep in deps:
                if isinstance(dep, dict):
                    target = dep.get("target", dep.get("module_id", ""))
                elif isinstance(dep, str):
                    target = dep
                else:
                    continue
                if target:
                    referenced_by[target].add(info["rel"])

    return dict(referenced_by), module_to_file, all_files
    """构建引用关系图."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="孤立文档检测（DOC-008#4）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    referenced_by, module_to_file, all_files = build_reference_graph()

    findings = []
    for info in all_files:
        rel = info["rel"]
        module_id = info["module_id"]

        if rel.endswith("index.md"):
            continue

        has_incoming = False
        if module_id and module_id in referenced_by:
            has_incoming = True
        if rel in referenced_by:
            has_incoming = True
        basename = Path(rel).name
        if basename in referenced_by:
            has_incoming = True

        if not has_incoming:
            findings.append(
                {
                    "file": rel,
                    "module_id": module_id,
                    "severity": "LOW",
                }
            )

    if findings:
        print(f"\n[ORPHAN-DOC] {len(findings)} 个孤立文档（无入边引用）:", file=sys.stderr)
        for f in findings[:30]:
            mid = f" ({f['module_id']})" if f["module_id"] else ""
            print(f"  [{f['severity']}] {f['file']}{mid}", file=sys.stderr)
        if len(findings) > 30:
            print(f"  ... 还有 {len(findings) - 30} 个", file=sys.stderr)
    else:
        print("[ORPHAN-DOC] 无孤立文档", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
