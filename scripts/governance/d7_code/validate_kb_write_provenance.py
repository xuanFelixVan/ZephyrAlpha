# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_kb_write_provenance.py | §
# [MODULE] scripts.governance.d7_code.validate_kb_write_provenance
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
validate_kb_write_provenance.py — 知识库写入 provenance 校验



对标：COND-46（知识库写入不传 provenance 为条件禁止）

检测内容：
- AST 扫描 kb.write() / knowledge_base.write() 调用
- 检查是否传入 provenance 参数

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 知识库写入 provenance 校验（COND-46 — kb.write()必须传provenance）
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


def check_kb_write_provenance(filepath: Path) -> list[dict]:
    """检查 KB 写入溯源."""
    findings = []
    """检查并返回违规列表."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings

    rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        is_kb_write = False

        if isinstance(func, ast.Attribute):
            if func.attr in ("write", "add", "store", "insert", "save"):
                if isinstance(func.value, ast.Name) and any(
                    k in func.value.id.lower() for k in ("kb", "knowledge", "knowledge_base")
                ):
                    is_kb_write = True
                if isinstance(func.value, ast.Attribute) and any(
                    k in func.value.attr.lower() for k in ("kb", "knowledge")
                ):
                    is_kb_write = True

        if not is_kb_write:
            continue

        has_provenance = False
        for kw in node.keywords:
            if kw.arg == "provenance":
                has_provenance = True
                break

        if not has_provenance:
            findings.append(
                {
                    "file": rel,
                    "line": node.lineno,
                    "severity": "MEDIUM",
                }
            )

    return findings
    """检查 KB 写入溯源."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="知识库写入 provenance 校验（COND-46）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    src_dir = REPO_ROOT / "src" / "zephyr"
    if not src_dir.exists():
        print("[KB-PROVENANCE] src/zephyr/ 不存在，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)

    all_findings = []
    for filepath in iter_files(src_dir, extensions=SCAN_EXTENSIONS_PY):
        findings = check_kb_write_provenance(filepath)
        all_findings.extend(findings)

    if all_findings:
        print(f"\n[KB-PROVENANCE] {len(all_findings)} 个知识库写入缺少 provenance:", file=sys.stderr)
        for f in all_findings:
            print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
    else:
        print("[KB-PROVENANCE] 知识库写入 provenance 合规", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
