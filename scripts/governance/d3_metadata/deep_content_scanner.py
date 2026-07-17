# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/deep_content_scanner.py | §
# [MODULE] scripts.governance.d3_metadata.deep_content_scanner
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
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
deep_content_scanner.py — 深度内容扫描器



对标：PS-STD-012 §7.3（doc_type 与正文关键词启发式不匹配）

检测内容：
- 启发式检测 doc_type 与正文关键词不匹配
- 如 doc_type=policy(declarative) 但正文含"Step 1→N"（应为 procedural policy）
- 如 doc_type=policy(declarative) 但正文含步骤性内容（应为 procedural policy）
- 结果需人工复核

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 深度内容扫描器（PS-STD-012 §7.3 — doc_type与内容启发式匹配）
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse

PROCEDURAL_KEYWORDS = re.compile(r"(?:Step\s+\d|步骤\s*\d|第一步|第二步|第三步|操作步骤|执行流程|1\.\s|2\.\s|3\.\s)")
POLICY_KEYWORDS = re.compile(r"(?:如果.*则|如果.*那么|当.*时|若.*则|条件|触发条件|适用场景)")
DECLARATIVE_KEYWORDS = re.compile(r"(?:定义|规范|标准|枚举|合法值|格式|模板|约束)")


def scan_content_type_mismatch() -> list[dict]:
    """scan content type mismatch."""
    findings = []
    """扫描并返回发现列表."""
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"

    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue

        doc_type = fm.get("doc_type", "")
        if not doc_type or doc_type in ("index", "template"):  # noqa: gate-vocab  业务逻辑：跳过 index/template 文档类型（非内容扫描目标，非词表成员校验）
            continue

        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue

        body = content
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                body = content[end + 3 :]

        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")

        has_procedural = bool(PROCEDURAL_KEYWORDS.search(body))
        has_policy = bool(POLICY_KEYWORDS.search(body))
        has_declarative = bool(DECLARATIVE_KEYWORDS.search(body))

        if doc_type in ("policy",) and has_procedural and not has_policy and not has_declarative:
            findings.append(
                {
                    "file": rel,
                    "doc_type": doc_type,
                    "hint": "正文含步骤式关键词（Step/步骤），可能应为 procedural policy（rule_form=procedural）",
                    "severity": "LOW",
                }
            )

    return findings
    """scan content type mismatch."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="深度内容扫描器（PS-STD-012 §7.3）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings = scan_content_type_mismatch()

    if findings:
        print(f"\n[DEEP-SCAN] {len(findings)} 个 doc_type 与内容可能不匹配（需人工复核）:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['file']}", file=sys.stderr)
            print(f"    doc_type={f['doc_type']} — {f['hint']}", file=sys.stderr)
    else:
        print("[DEEP-SCAN] doc_type 与内容匹配", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
