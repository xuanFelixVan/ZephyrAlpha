# [BLUEPRINT] MOD-INF-005 | scripts/governance/check_audit_rbac_isolation.py | §
# [MODULE] scripts.governance.check_audit_rbac_isolation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
#!/usr/bin/env python
"""
check_audit_rbac_isolation.py — 静态分析 audit-trail 是否直接 import agent-rbac.

DOM-GOV-001 §5 裁定: Audit 不依赖 RBAC，RBAC 单向调用 Audit.
用法: python scripts/governance/check_audit_rbac_isolation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import ast
import sys
from pathlib import Path

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

PROJECT_ROOT = REPO_ROOT
AUDIT_DIR = PROJECT_ROOT / "src" / "zephyr" / "governance" / "audit-trail"


def scan_file(filepath: Path) -> list[str]:
    """scan_file implementation."""
    violations = []
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return violations
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "rbac" in alias.name.lower() or "agent-rbac" in alias.name.lower():
                    violations.append(f"IMPORT: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and ("rbac" in node.module.lower() or "agent-rbac" in node.module.lower()):
                violations.append(f"IMPORT_FROM: {node.module}")
    return violations


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    if not AUDIT_DIR.exists():
        print(f"ERROR: audit-trail directory not found: {AUDIT_DIR}")
        return EXIT_FINDINGS

    all_violations: dict[str, list[str]] = {}
    for py_file in AUDIT_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        violations = scan_file(py_file)
        if violations:
            all_violations[str(py_file.relative_to(PROJECT_ROOT))] = violations

    if all_violations:
        print(f"FAILED: Audit 模块违规 import RBAC ({len(all_violations)} files):")
        for f, v in sorted(all_violations.items()):
            print(f"  {f}: {v}")
        return EXIT_FINDINGS
    else:
        print("PASSED: Audit 模块无 RBAC import (符合 §5 裁定)")
        return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
