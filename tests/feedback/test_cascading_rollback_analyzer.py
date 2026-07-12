# [A_test] module_id: SRC-TST-0499 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_cascading_rollback_analyzer
# [INVARIANTS] max_cascade_depth=5; min_dependency_confidence=0.5
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_cascading_rollback_analyzer.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.cascading_rollback_analyzer import (
    CascadingRollbackAnalyzer,
    RollbackSafety,
)


class TestCascadingRollbackAnalyzerInstantiation:
    def test_default_construction(self):
        cra = CascadingRollbackAnalyzer()
        assert cra.max_cascade_depth == 5
        assert cra.min_dependency_confidence == pytest.approx(0.5)

    def test_custom_params(self):
        cra = CascadingRollbackAnalyzer(max_cascade_depth=10, min_dependency_confidence=0.8)
        assert cra.max_cascade_depth == 10


class TestRecordActionDependency:
    def test_record_single(self):
        cra = CascadingRollbackAnalyzer()
        cra.record_action_dependency("action-1", ["action-0"])
        assert "action-1" in cra.action_dependencies
        assert cra.action_dependencies["action-1"] == ["action-0"]

    def test_record_multiple_deps(self):
        cra = CascadingRollbackAnalyzer()
        cra.record_action_dependency("action-2", ["action-0", "action-1"])
        assert len(cra.action_dependencies["action-2"]) == 2


class TestAnalyzeRollback:
    def test_no_dependencies_safe(self):
        cra = CascadingRollbackAnalyzer()
        result = cra.analyze_rollback("unknown-action")
        assert result["safety"] == RollbackSafety.SAFE.value
        assert result["cascade"] == []

    def test_cascade_required(self):
        cra = CascadingRollbackAnalyzer()
        cra.record_action_dependency("action-1", [])
        cra.record_action_dependency("action-2", ["action-1"])
        result = cra.analyze_rollback("action-1")
        assert result["safety"] == RollbackSafety.CASCADE_REQUIRED.value
        assert "action-2" in result["cascade_targets"]

    def test_deep_cascade_unsafe(self):
        cra = CascadingRollbackAnalyzer(max_cascade_depth=2)
        cra.record_action_dependency("a", [])
        cra.record_action_dependency("b", ["a"])
        cra.record_action_dependency("c", ["b"])
        cra.record_action_dependency("d", ["c"])
        result = cra.analyze_rollback("a")
        assert result["depth"] > 0

    def test_empty_action_id(self):
        cra = CascadingRollbackAnalyzer()
        result = cra.analyze_rollback("")
        assert result["safety"] == RollbackSafety.SAFE.value


class TestBuildDependencyGraph:
    def test_empty_graph(self):
        cra = CascadingRollbackAnalyzer()
        graph = cra.build_dependency_graph()
        assert graph["nodes"] == []
        assert graph["edges"] == []

    def test_graph_with_deps(self):
        cra = CascadingRollbackAnalyzer()
        cra.record_action_dependency("a", [])
        cra.record_action_dependency("b", ["a"])
        graph = cra.build_dependency_graph()
        assert len(graph["nodes"]) == 2
        assert len(graph["edges"]) == 1


class TestGetMostDependedUpon:
    def test_empty(self):
        cra = CascadingRollbackAnalyzer()
        result = cra.get_most_depended_upon()
        assert result == []

    def test_ranked(self):
        cra = CascadingRollbackAnalyzer()
        cra.record_action_dependency("b", ["a"])
        cra.record_action_dependency("c", ["a"])
        cra.record_action_dependency("d", ["a", "b"])
        result = cra.get_most_depended_upon(top_n=3)
        assert result[0]["action_id"] == "a"
        assert result[0]["dependent_count"] == 3


class TestVerifyPostRollbackConsistency:
    def test_consistent(self):
        cra = CascadingRollbackAnalyzer()
        cra.record_action_dependency("a", [])
        result = cra.verify_post_rollback_consistency("a")
        assert result["consistent"] is True

    def test_orphaned_dependents(self):
        cra = CascadingRollbackAnalyzer(max_cascade_depth=2)
        cra.record_action_dependency("a", [])
        cra.record_action_dependency("b", ["a"])
        cra.record_action_dependency("c", ["b"])
        cra.record_action_dependency("d", ["c"])
        result = cra.verify_post_rollback_consistency("a")
        assert result["consistent"] is False
        assert "d" in result["orphaned_dependents"]
