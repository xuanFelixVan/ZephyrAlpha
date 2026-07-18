# [A_test] module_id: SRC-TST-1833 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-461 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.context_engine.test_context_evaluator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for context_evaluator.py (TASK-014 beta b)."""

from zephyr.autonomy_core.context.context_evaluator import ContextEvaluator


class TestContextEvaluator:
    def test_full_citation(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(["KE-001", "KE-002"], ["KE-001", "KE-002"])
        assert report.citation_rate == 1.0
        assert report.efficiency_score == 100.0

    def test_partial_citation(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(["KE-001", "KE-002", "KE-003"], ["KE-001"])
        assert report.citation_rate < 1.0

    def test_no_citation(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(["KE-001"], [])
        assert report.citation_rate == 0.0

    def test_unused_ke_ids(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(["KE-001", "KE-002"], ["KE-001"])
        assert "KE-002" in report.unused_ke_ids

    def test_batch_evaluate(self):
        evaluator = ContextEvaluator()
        turns = [
            (["A", "B"], ["A"]),
            (["C"], ["C"]),
        ]
        reports = evaluator.batch_evaluate(turns)
        assert len(reports) == 2
        assert reports[1].citation_rate == 1.0
