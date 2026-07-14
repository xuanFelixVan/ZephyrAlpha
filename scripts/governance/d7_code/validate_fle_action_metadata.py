# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_fle_action_metadata.py | §
# [MODULE] scripts.governance.d7_code.validate_fle_action_metadata
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
validate_fle_action_metadata.py — FLE Action 元数据校验



对标：COND-44（FLE Action 不记录 effective_from + ttl 为条件禁止）

检测内容：
- AST 扫描 FLE Action 类
- 检查是否包含 effective_from 和 ttl 字段

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: FLE Action 元数据校验（COND-44 — effective_from+ttl必填）
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

REQUIRED_ACTION_FIELDS = {"effective_from", "ttl"}


def check_fle_actions(filepath: Path) -> list[dict]:
    """检查 FLE action 元数据."""
    findings = []
    """检查并返回违规列表."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings

    rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        is_action = False
        for base in node.bases:
            if (isinstance(base, ast.Name) and "Action" in base.id) or (
                isinstance(base, ast.Attribute) and "Action" in base.attr
            ):
                is_action = True

        if not is_action:
            continue

        class_fields = set()
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                class_fields.add(item.target.id)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_fields.add(target.id)

        missing = REQUIRED_ACTION_FIELDS - class_fields
        if missing:
            findings.append(
                {
                    "file": rel,
                    "line": node.lineno,
                    "class": node.name,
                    "missing": sorted(missing),
                    "severity": "MEDIUM",
                }
            )

    return findings
    """检查 FLE action 元数据."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="FLE Action 元数据校验（COND-44）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    src_dir = REPO_ROOT / "src" / "zephyr"
    if not src_dir.exists():
        print("[FLE-ACTION] src/zephyr/ 不存在，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)

    all_findings = []
    for filepath in iter_files(src_dir, extensions=SCAN_EXTENSIONS_PY):
        findings = check_fle_actions(filepath)
        all_findings.extend(findings)

    if all_findings:
        print(f"\n[FLE-ACTION] {len(all_findings)} 个 FLE Action 缺少元数据:", file=sys.stderr)
        for f in all_findings:
            print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    类 '{f['class']}' 缺少字段: {', '.join(f['missing'])}", file=sys.stderr)
    else:
        print("[FLE-ACTION] FLE Action 元数据合规", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
