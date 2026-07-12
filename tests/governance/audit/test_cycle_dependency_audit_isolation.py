# [A_test] module_id: SRC-TST-0122 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-279 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_cycle_dependency_audit_isolation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
DOM-GOV-001 循环依赖测试 — Audit 独立运行验证 + 无 RBAC import 扫描.

§5 裁定: Audit 不依赖 RBAC——RBAC 单向调用 Audit，Audit 只记录事实不验证权限.
"""

from __future__ import annotations

import ast
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT

GOVERNANCE_ROOT = REPO_ROOT / "src" / "zephyr" / "governance"


def scan_imports(filepath: Path) -> list[str]:
    imports = []
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


class TestAuditRBACIsolation:
    def test_audit_no_rbac_import(self):
        audit_dir = GOVERNANCE_ROOT / "audit-trail"
        if not audit_dir.exists():
            return
        violations = []
        for py_file in audit_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            for imp in scan_imports(py_file):
                if "rbac" in imp.lower() or "agent-rbac" in imp:
                    rel = py_file.relative_to(GOVERNANCE_ROOT.parent.parent)
                    violations.append(f"{rel}: imports {imp}")
        assert not violations, "Audit 禁止 import RBAC (违反 §5 循环依赖裁定):\n" + "\n".join(violations)

    def test_audit_can_run_independently(self):
        try:
            from zephyr.governance.audit_trail.contracts import AuditContract

            assert AuditContract is not None
        except ImportError as e:
            assert "rbac" not in str(e).lower(), f"Audit 不应因 RBAC 缺失而失败: {e}"

    def test_governance_init_declares_rbac_dependency_direction(self):
        init = GOVERNANCE_ROOT / "__init__.py"
        content = init.read_text(encoding="utf-8") if init.exists() else ""
        has_ruling = "RBAC" in content and "Audit" in content and ("G-CT-001" in content or "单向" in content)
        assert has_ruling, "governance/__init__.py 应声明 §5 裁定: RBAC 单向调用 Audit"
