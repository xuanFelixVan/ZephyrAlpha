# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/fix_shared_bypass.py | §
# [MODULE] scripts.governance.d11_compliance.fix_shared_bypass
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
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
fix_shared_bypass.py - D-D-07 auto-fix tool (validate_script_quality.py --fix companion)
Aligns with AGENTS.md section 6.5 (script self-creation repository mandatory convention)
and SCRIPT-QUALITY-001 D-D-07 (prohibits bypassing _shared utilities).
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_FINDINGS, EXIT_PASS

__manifest__ = """
args:
- --fix
- --dry-run
- --no-backup
description: D-D-07 auto-fix - detect and repair local redefinitions of _shared API violations
dimensions:
- D11
- D7
priority: P2
timeout_seconds: 30
warn_only: true
"""

import ast
import sys
from pathlib import Path

_PROJ = Path(__file__).resolve().parents[2]
if str(_PROJ) not in sys.path:
    sys.path.insert(0, str(_PROJ))

KNOWN_SYMBOLS = {
    "REPO_ROOT",
    "EXCLUDE_DIRS",
    "SRC_DIR",
    "SCAN_EXTENSIONS",
    "load_yaml",
    "save_yaml",
}

# 豁免文件：自身和 _shared/constants.py（REPO_ROOT 真源，需 bootstrap）
_EXEMPT_FILES = {
    "scripts/governance/_shared/constants.py",
    "scripts/governance/d11_compliance/fix_shared_bypass.py",
}


def _detect_parents_of_dunder_file(node: ast.Assign) -> str | None:
    """检测赋值节点是否包含 Path(__file__).parents[N] 模式（不限变量名）。

    匹配 Path(__file__).resolve().parents[N] / Path(__file__).parents[N] 等。
    返回变量名或 None。豁免：_shared/constants.py 和本文件（bootstrap 需求）。
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Subscript):
            if isinstance(child.value, ast.Attribute) and child.value.attr == "parents":
                inner = child.value.value
                # resolve() 调用 → 剥一层
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == "resolve":
                    inner = inner.func.value
                # Path(__file__) 调用
                if isinstance(inner, ast.Call):
                    if isinstance(inner.func, ast.Name) and inner.func.id == "Path":
                        if inner.args and isinstance(inner.args[0], ast.Name) and inner.args[0].id == "__file__":
                            t = node.targets[0] if node.targets else None
                            return t.id if isinstance(t, ast.Name) else "<expr>"
    return None


def main() -> int:
    """Detect local redefinitions of _shared API symbols + Path(__file__).parents[N] pattern."""
    gov_dir = _PROJ / "scripts" / "governance"
    violations = 0
    parents_warnings = 0

    for fpath in gov_dir.rglob("*.py"):
        rel_str = str(fpath.relative_to(_PROJ)).replace("\\", "/")
        if rel_str in _EXEMPT_FILES:
            continue
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                rel = fpath.relative_to(_PROJ)
                # 原有检测：KNOWN_SYMBOLS 重定义（exit 1 阻断）
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in KNOWN_SYMBOLS:
                        print(f"  WARN: {rel} redefines {target.id} locally")
                        violations += 1
                # 新增检测：Path(__file__).parents[N] 模式（warn-only，不阻断）
                var = _detect_parents_of_dunder_file(node)
                if var:
                    print(f"  INFO: {rel} uses Path(__file__).parents[N] (var={var}) — import REPO_ROOT from _shared.constants instead")
                    parents_warnings += 1

    if parents_warnings:
        print(f"\nINFO: {parents_warnings} Path(__file__).parents[N] usage(s) detected (warn-only, not blocking)")

    if violations:
        print(f"\nFAIL: {violations} shared API bypass(es)")
        return EXIT_FINDINGS

    print("OK: No _shared API bypass detected")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
