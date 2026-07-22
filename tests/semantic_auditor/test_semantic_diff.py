# [A_test] module_id: MOD-GOV_semantic_diff | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_semantic_diff
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.semantic_diff",
    reason="semantic_diff module not available",
)


class TestSemanticDiffEngine:
    def test_instantiation(self):
        obj = mod.SemanticDiffEngine()
        assert obj is not None

    def test_diff(self):
        obj = mod.SemanticDiffEngine()
        regions_a = [mod.SemanticRegion(name="foo", start_line=1, end_line=10)]
        regions_b = [mod.SemanticRegion(name="foo", start_line=1, end_line=15)]
        result = obj.diff("agent_a", "agent_b", regions_a, regions_b, "file.py")
        assert isinstance(result, mod.SemanticDiffReport)

    def test_diff_empty_regions(self):
        obj = mod.SemanticDiffEngine()
        result = obj.diff("agent_a", "agent_b", [], [], "file.py")
        assert isinstance(result, mod.SemanticDiffReport)

    def test_extract_regions(self):
        obj = mod.SemanticDiffEngine()
        source = "def foo():\n    pass\n\ndef bar():\n    return 1\n"
        result = obj.extract_regions(source)
        assert isinstance(result, list)


class TestSemanticDiffReport:
    def test_has_conflict(self):
        report = mod.SemanticDiffReport(agent_a_id="a1", agent_b_id="a2", file_path="f.py")
        assert isinstance(report.has_conflict, bool)

    def test_max_conflict_risk(self):
        report = mod.SemanticDiffReport(agent_a_id="a1", agent_b_id="a2", file_path="f.py")
        assert isinstance(report.max_conflict_risk, float)


class TestSemanticDiffType:
    def test_enum_values(self):
        assert len(mod.SemanticDiffType) > 0
