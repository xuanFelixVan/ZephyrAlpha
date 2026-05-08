"""Phase 1 Gate 检查测试 — DOM-GOV-001 §7.2 门禁检查."""
from __future__ import annotations

import pytest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "src" / "zephyr" / "governance"

PHASE1_REQUIRED_FILES = [
    "governance/__init__.py",
    "governance/agent_rbac/__init__.py",
    "governance/agent_spec/__init__.py",
    "governance/audit_trail/__init__.py",
    "governance/rollback/__init__.py",
    "governance/escalation/__init__.py",
    "governance/drift_detector/__init__.py",
    "governance/budget_enforcer/__init__.py",
    "governance/a2a/__init__.py",
]

EIGHT_MODULES = [
    "agent_rbac", "agent_spec", "audit_trail", "rollback",
    "escalation", "drift_detector", "budget_enforcer", "a2a",
]


class TestPhase1Gate:
    """Phase 1 Gate: 8 模块目录 + SYS-MASTER/MOD-MASTER 注册."""

    def test_eight_module_dirs_exist(self):
        for mod in EIGHT_MODULES:
            mod_dir = GOVERNANCE_DIR / mod
            assert mod_dir.exists(), f"Missing: governance/{mod}/"
            assert mod_dir.is_dir(), f"Not a directory: governance/{mod}/"

    def test_each_module_has_init(self):
        for mod in EIGHT_MODULES:
            init = GOVERNANCE_DIR / mod / "__init__.py"
            assert init.exists(), f"Missing: governance/{mod}/__init__.py"

    def test_gct_blueprint_registered(self):
        bp = GOVERNANCE_DIR / "__init__.py"
        content = bp.read_text(encoding="utf-8")
        for i in range(1, 9):
            assert f"G-CT-00{i}" in content, f"G-CT-00{i} not referenced in governance/__init__.py"

    def test_no_orphan_directories(self):
        children = [d.name for d in GOVERNANCE_DIR.iterdir() if d.is_dir() and not d.name.startswith("_") and not d.name.startswith(".")]
        for child in children:
            assert child in EIGHT_MODULES or child == "__pycache__", f"Orphan directory: governance/{child}/"
