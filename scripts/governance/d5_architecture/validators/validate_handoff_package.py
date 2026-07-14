# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_handoff_package.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_handoff_package
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
"""validate_handoff_package.py — HandoffPackage 完整性校验



对标：COND-47（HandoffPackage 8 必填字段缺失为条件禁止）

检测内容：
- AST 扫描 HandoffPackage 数据类
- 检查是否包含 8 个必填字段

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: HandoffPackage 完整性校验（COND-47 — 8必填字段）
dimensions:
- D5
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

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_PY
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse

REQUIRED_handoff_FIELDS = {
    "session_id",
    "timestamp",
    "context_summary",
    "pending_tasks",
    "decisions_made",
    "files_modified",
    "next_steps",
    "owner_notes",
}


def check_handoff_package(filepath: Path) -> list[dict]:
    """检查交接包完整性."""
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
        if node.name != "HandoffPackage":
            continue

        class_fields = set()
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                class_fields.add(item.target.id)

        missing = REQUIRED_handoff_FIELDS - class_fields
        if missing:
            findings.append(
                {
                    "file": rel,
                    "line": node.lineno,
                    "missing": sorted(missing),
                    "severity": "MEDIUM",
                }
            )

    return findings
    """检查交接包完整性."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="HandoffPackage 完整性校验（COND-47）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    src_dir = REPO_ROOT / "src" / "zephyr"
    if not src_dir.exists():
        print("[handoff] src/zephyr/ 不存在，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)

    all_findings = []
    for filepath in iter_files(src_dir, extensions=SCAN_EXTENSIONS_PY):
        findings = check_handoff_package(filepath)
        all_findings.extend(findings)

    if all_findings:
        print(f"\n[handoff] {len(all_findings)} 个 HandoffPackage 缺少字段:", file=sys.stderr)
        for f in all_findings:
            print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    缺少: {', '.join(f['missing'])}", file=sys.stderr)
    else:
        print("[handoff] HandoffPackage 完整性合规", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if all_findings else EXIT_PASS)


if __name__ == "__main__":
    main()
