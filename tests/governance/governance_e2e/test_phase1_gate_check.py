# [A_test] module_id: MOD-GOV_phase1_gate_check | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-297 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_phase1_gate_check
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-297 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""Phase 1 Gate 检查测试 — DOM-GOV-001 §7.2 门禁检查."""

from __future__ import annotations

from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

GOVERNANCE_DIR = REPO_ROOT / "src" / "zephyr" / "governance"

# Phase-1 八模块壳目录现状（2026-09-18 W6 轮2 核实，锚=AI-21 审计批 441852d976）：
# - agent-spec 空壳已删，实现真身在 snake_case 包 agent_spec（连字符目录不可 import）；
# - drift-detector / budget-enforcer 空壳从未落地于 governance/，能力件实际位于
#   src/zephyr/gov_drift 与 src/zephyr/integration/budget_enforcer。
# 本门按"能力模块存在且可 import（含 __init__.py）"断言，路径对齐实测真身。
PHASE1_CAPABILITY_MODULES = [
    ("agent-rbac", "governance/agent-rbac"),
    ("agent-spec", "governance/agent_spec"),
    ("audit-trail", "governance/audit-trail"),
    ("rollback", "governance/rollback"),
    ("escalation", "governance/escalation"),
    ("drift-detector", "gov_drift"),
    ("budget-enforcer", "integration/budget_enforcer"),
    ("a2a", "governance/a2a"),
]

SRC_ROOT = REPO_ROOT / "src" / "zephyr"


class TestPhase1Gate:
    """Phase 1 Gate: 8 能力模块目录 + SYS-MASTER/MOD-MASTER 注册."""

    def test_eight_module_dirs_exist(self):
        for cap, rel in PHASE1_CAPABILITY_MODULES:
            mod_dir = SRC_ROOT / rel
            assert mod_dir.exists(), f"Missing: {cap} -> {rel}/"
            assert mod_dir.is_dir(), f"Not a directory: {cap} -> {rel}/"

    def test_each_module_has_init(self):
        for cap, rel in PHASE1_CAPABILITY_MODULES:
            init = SRC_ROOT / rel / "__init__.py"
            assert init.exists(), f"Missing: {rel}/__init__.py (capability {cap})"

    def test_gct_blueprint_registered(self):
        bp = GOVERNANCE_DIR / "__init__.py"
        content = bp.read_text(encoding="utf-8")
        for i in range(1, 9):
            assert f"G-CT-00{i}" in content, f"G-CT-00{i} not referenced in governance/__init__.py"

    def test_no_orphan_directories(self):
        children = [
            d.name
            for d in GOVERNANCE_DIR.iterdir()
            if d.is_dir() and not d.name.startswith("_") and not d.name.startswith(".")
        ]
        for child in children:
            pinned = {rel.split("/")[-1] for _, rel in PHASE1_CAPABILITY_MODULES if rel.startswith("governance/")}
            assert child in pinned or child == "__pycache__", f"Orphan directory: governance/{child}/"
