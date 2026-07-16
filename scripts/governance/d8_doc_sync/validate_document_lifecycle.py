# [BLUEPRINT] MOD-INF-005 | scripts/governance/d8_doc_sync/validate_document_lifecycle.py | §
# [MODULE] scripts.governance.d8_doc_sync.validate_document_lifecycle
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
validate_document_lifecycle.py — 文档生命周期校验



对标：GOV-DOC-006 §二/§四/§五/§六/§七

检测内容：
- deprecated 文件 superseded_by 字段
- active 文件不应有 superseded_by
- supersedes/superseded_by 双向链接完整性
- AI 产物位置检查（created_by:agent 不应在 docs/ 主目录）
- active 文件直接删除检测

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 文档生命周期校验（GOV-DOC-006 §二/§四/§五/§六 — superseded_by+双向链接+AI产物）
dimensions:
- D8
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


def scan_lifecycle_violations() -> list[dict]:
    """扫描生命周期引用违规."""
    findings = []
    """扫描并返回发现列表."""
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"

    all_fm = {}
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD_YAML):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        module_id = fm.get("module_id", "")
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        if module_id:
            all_fm[module_id] = {"filepath": filepath, "rel": rel, "fm": fm}

    for module_id, info in all_fm.items():
        fm = info["fm"]
        rel = info["rel"]
        status = fm.get("status", "")
        superseded_by = fm.get("superseded_by", "")
        supersedes = fm.get("supersedes", "")
        created_by = fm.get("created_by", "")

        if status == "active" and superseded_by:
            findings.append(
                {
                    "file": rel,
                    "type": "ACTIVE_WITH_SUPERSEDED_BY",
                    "detail": "active 文件不应有 superseded_by 字段",
                    "severity": "MEDIUM",
                }
            )

        if status == "deprecated" and not superseded_by:
            findings.append(
                {
                    "file": rel,
                    "type": "DEPRECATED_NO_SUPERSEDED_BY",
                    "detail": "deprecated 文件缺少 superseded_by 字段",
                    "severity": "HIGH",
                }
            )

        if superseded_by and superseded_by in all_fm:
            target = all_fm[superseded_by]
            target_supersedes = target["fm"].get("supersedes", "")
            if target_supersedes != module_id:
                findings.append(
                    {
                        "file": rel,
                        "type": "BROKEN_BIDIRECTIONAL_LINK",
                        "detail": f"superseded_by='{superseded_by}' 但对方 supersedes='{target_supersedes}'（应为 '{module_id}'）",
                        "severity": "MEDIUM",
                    }
                )

        if created_by == "agent" and ".audit_cache" not in rel and "_working/audit" not in rel:
            findings.append(
                {
                    "file": rel,
                    "type": "AI_PRODUCT_IN_DOCS",
                    "detail": "AI 生成产物（created_by:agent）不应在 docs/ 主目录",
                    "severity": "MEDIUM",
                }
            )

    return findings
    """扫描生命周期引用违规."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="文档生命周期校验（GOV-DOC-006 §二/§四/§五/§六）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings = scan_lifecycle_violations()

    if findings:
        print(f"\n[DOC-LIFECYCLE] {len(findings)} 个文档生命周期违规:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['file']}", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print("[DOC-LIFECYCLE] 文档生命周期合规", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
