# [BLUEPRINT] MOD-INF-005 | scripts/governance/d2_links/detect_relative_references.py | §
# [MODULE] scripts.governance.d2_links.detect_relative_references
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d2_links.__init__
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
detect_relative_references.py — 相对路径引用检测



对标：DOC-004（引用使用绝对路径，非仅 module_id 或相对路径）

检测内容：
- 扫描 Markdown 中的引用链接
- 检测仅使用 module_id 的引用（如 [XXX](PS-STD-001)）
- 检测相对路径引用（如 [XXX](../other.md)）
- 推荐使用绝对路径

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 相对路径引用检测（DOC-004 — 应使用绝对路径）
dimensions:
- D2
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

from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse

MODULE_ID_PATTERN = re.compile(
    r"^[A-Z]{2,5}-(?:STD|REG|IDX|GLS|TERM|VOC|ARCH|MOD|DOC|SEC|DATA|TASK|DEV|MIG|VC|CMP|L\d{2})-\d{3}", re.IGNORECASE
)

RELATIVE_PATH_PATTERN = re.compile(r"^\.\.?[\\/]")


def scan_relative_references() -> list[dict]:
    """scan relative references."""
    findings = []
    """扫描并返回发现列表."""
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"

    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD):
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue

        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            for match in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", line):
                link_text = match.group(1)
                link_target = match.group(2)

                if link_target.startswith("http") or link_target.startswith("#") or link_target.startswith("mailto"):
                    continue

                if MODULE_ID_PATTERN.match(link_target):
                    findings.append(
                        {
                            "file": rel,
                            "line": i,
                            "link": f"[{link_text}]({link_target})",
                            "type": "MODULE_ID_ONLY",
                            "detail": "仅使用 module_id 引用（应使用绝对路径）",
                            "severity": "LOW",
                        }
                    )

                if RELATIVE_PATH_PATTERN.match(link_target):
                    findings.append(
                        {
                            "file": rel,
                            "line": i,
                            "link": f"[{link_text}]({link_target})",
                            "type": "RELATIVE_PATH",
                            "detail": "使用相对路径引用（应使用绝对路径）",
                            "severity": "LOW",
                        }
                    )

    return findings
    """scan relative references."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="相对路径引用检测（DOC-004）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings = scan_relative_references()

    if findings:
        print(f"\n[REL-REF] {len(findings)} 个非绝对路径引用:", file=sys.stderr)
        for f in findings[:30]:
            print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    {f['link']} — {f['detail']}", file=sys.stderr)
        if len(findings) > 30:
            print(f"  ... 还有 {len(findings) - 30} 个", file=sys.stderr)
    else:
        print("[REL-REF] 所有引用均使用绝对路径", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
