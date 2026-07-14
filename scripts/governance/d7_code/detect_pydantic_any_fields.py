# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/detect_pydantic_any_fields.py | §
# [MODULE] scripts.governance.d7_code.detect_pydantic_any_fields
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
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
detect_pydantic_any_fields.py — Pydantic Any 类型字段检测



对标：REC-11（Pydantic 模型禁止 Any 类型字段）

检测内容：
- AST 扫描 Pydantic Model 中的 Any 类型字段
- Any 类型破坏类型安全，应使用具体类型

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: Pydantic Any 类型字段检测（REC-11 — 禁止Any类型字段）
dimensions:
- D7
priority: P2
timeout_seconds: 30
warn_only: false
"""


import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_PY
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse


def check_any_fields(filepath: Path) -> list[dict]:
    """检查 Pydantic Any 字段."""
    findings = []
    """检查并返回违规列表."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings

    rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")

    for node in ast.walk(tree):
        if not isinstance(node, ast.AnnAssign):
            continue
        if not node.annotation:
            continue

        ann = node.annotation
        is_any = False

        if isinstance(ann, ast.Name) and ann.id == "Any":
            is_any = True
        elif isinstance(ann, ast.Subscript):
            if isinstance(ann.value, ast.Name) and ann.value.id in ("Optional", "Union"):
                for elt in [ann.slice] if not isinstance(ann.slice, ast.Tuple) else ann.slice.elts:
                    if isinstance(elt, ast.Name) and elt.id == "Any":
                        is_any = True

        if is_any:
            field_name = ""
            if isinstance(node.target, ast.Name):
                field_name = node.target.id
            findings.append(
                {
                    "file": rel,
                    "line": node.lineno,
                    "field": field_name,
                    "severity": "LOW",
                }
            )

    return findings
    """检查 Pydantic Any 字段."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="Pydantic Any 类型字段检测（REC-11）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    src_dir = REPO_ROOT / "src" / "zephyr"
    if not src_dir.exists():
        print("[PYDANTIC-ANY] src/zephyr/ 不存在，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)

    all_findings = []
    for filepath in iter_files(src_dir, extensions=SCAN_EXTENSIONS_PY):
        findings = check_any_fields(filepath)
        all_findings.extend(findings)

    if all_findings:
        print(f"\n[PYDANTIC-ANY] {len(all_findings)} 个 Any 类型字段:", file=sys.stderr)
        for f in all_findings:
            print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    字段 '{f['field']}' 使用 Any 类型", file=sys.stderr)
    else:
        print("[PYDANTIC-ANY] 无 Any 类型字段", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
