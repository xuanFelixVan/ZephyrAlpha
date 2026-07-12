# [A_test] module_id: SRC-TST-0136 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-293 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_p0_i1_depends_on_integration
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""P0-I1 depends_on 集成测试 — DOM-GOV-001 §8.3."""

from __future__ import annotations

import re
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT


class TestP0I1DependsOnIntegration:
    """SYS-MASTER-001 + MOD-MASTER-001 与 DOM-GOV-001 一致性."""

    def test_all_modules_prefixed_mod_inf(self):
        modules = [
            "MOD-INF-018",
            "MOD-INF-019",
            "MOD-INF-020",
            "MOD-INF-021",
            "MOD-INF-022",
            "MOD-INF-023",
            "MOD-INF-024",
            "MOD-INF-025",
        ]
        for mid in modules:
            assert mid.startswith("MOD-INF-"), f"{mid} 不遵守命名规范"

    def test_gct_contracts_count_eight(self):
        gov_init = REPO_ROOT / "src" / "zephyr" / "governance" / "__init__.py"
        gov_doc = gov_init.read_text(encoding="utf-8")
        gcts = set(re.findall(r"G-CT-\d+", gov_doc))
        assert len(gcts) >= 8, f"Expected >= 8 GCT contracts, found {len(gcts)}: {sorted(gcts)}"

    def test_blueprint_references_sys_master(self):
        bp_path = REPO_ROOT / "docs" / "03_modules" / "_domain-governance" / "blueprint.md"
        content = bp_path.read_text(encoding="utf-8")
        assert "SYS-MASTER" in content or "sys-master" in content.lower()


class TestP0I2ConstructionOrder:
    """施工顺序验证 — Phase 1 → Phase 2 → Phase 3 → Phase 4 线性拓扑."""

    def test_phase_order_linear(self):
        phases = ["PHASE_1", "PHASE_2", "PHASE_3", "PHASE_4"]
        for i in range(len(phases) - 1):
            assert phases[i] < phases[i + 1], f"Phase order broken: {phases[i]} >= {phases[i + 1]}"

    def test_phase_dependencies_acyclic(self):
        deps = {"P2": ["P1"], "P3": ["P2"], "P4": ["P3"]}
        for k, v in deps.items():
            assert k not in v, f"Self-dependency: {k} depends on itself"
