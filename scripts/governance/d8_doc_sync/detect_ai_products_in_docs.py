# [BLUEPRINT] MOD-INF-005 | scripts/governance/d8_doc_sync/detect_ai_products_in_docs.py | §
# [MODULE] scripts.governance.d8_doc_sync.detect_ai_products_in_docs
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
# [TTL] task_bound
"""
detect_ai_products_in_docs.py — AI 产物位置检测



对标：GOV-DOC-006 §六（AI 生成产物必须写入 .audit_cache/，禁止写入 docs/）

检测内容：
- 扫描 docs/ 下 created_by: agent 的文件
- AI 生成文件应在 .audit_cache/ 而非 docs/ 主目录

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: AI 产物位置检测（GOV-DOC-006 §六 — created_by:agent不应在docs/主目录）
dimensions:
- D8
priority: P2
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


def scan_ai_products() -> list[dict]:
    """扫描文档中的 AI 生成标记."""
    findings = []
    """扫描并返回发现列表."""
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"

    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD_YAML):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue

        created_by = fm.get("created_by", "")
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")

        if created_by == "agent" and ".audit_cache" not in rel and "_working/audit" not in rel:
            findings.append(
                {
                    "file": rel,
                    "severity": "MEDIUM",
                }
            )

    return findings
    """扫描文档中的 AI 生成标记."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="AI 产物位置检测（GOV-DOC-006 §六）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings = scan_ai_products()

    if findings:
        print(f"\n[AI-PRODUCTS] {len(findings)} 个 AI 产物在 docs/ 主目录:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['file']}", file=sys.stderr)
            print("    AI 生成产物应写入 .audit_cache/", file=sys.stderr)
    else:
        print("[AI-PRODUCTS] 无 AI 产物在 docs/ 主目录", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
