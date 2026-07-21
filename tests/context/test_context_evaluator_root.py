# [A_test] module_id: MOD-GOV_context_evaluator_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.context.context_evaluator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.context.context_evaluator import (
        ContextEvaluator,
        EvaluationReport,
    )

    _IMPORT_OK = True
    _IMPORT_ERR = None
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_ERR = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_ERR}")


class TestContextEvaluator:
    def test_evaluate_full_citation(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(
            injected_ids=["KE-001", "KE-002", "KE-003"],
            cited_ids=["KE-001", "KE-002", "KE-003"],
        )
        assert report.citation_rate == 1.0
        assert report.efficiency_score == 100.0
        assert report.cited_count == 3
        assert report.injected_count == 3
        assert report.unused_ke_ids == []

    def test_evaluate_partial_citation(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(
            injected_ids=["KE-001", "KE-002", "KE-003"],
            cited_ids=["KE-001", "KE-003"],
        )
        assert report.cited_count == 2
        assert report.citation_rate == pytest.approx(2 / 3, abs=0.01)
        assert "KE-002" in report.unused_ke_ids

    def test_evaluate_no_citation(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(
            injected_ids=["KE-001", "KE-002"],
            cited_ids=["KE-099"],
        )
        assert report.cited_count == 0
        assert report.citation_rate == 0.0
        assert report.efficiency_score == 0.0
        assert len(report.unused_ke_ids) == 2

    def test_evaluate_empty_injected(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(
            injected_ids=[],
            cited_ids=["KE-001"],
        )
        assert report.injected_count == 0
        assert report.citation_rate == 0.0

    def test_evaluate_empty_cited(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(
            injected_ids=["KE-001", "KE-002"],
            cited_ids=[],
        )
        assert report.cited_count == 0
        assert report.citation_rate == 0.0
        assert len(report.unused_ke_ids) == 2

    def test_evaluate_both_empty(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(
            injected_ids=[],
            cited_ids=[],
        )
        assert report.citation_rate == 0.0
        assert report.injected_count == 0

    def test_evaluate_duplicate_injected(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(
            injected_ids=["KE-001", "KE-001", "KE-002"],
            cited_ids=["KE-001"],
        )
        assert report.injected_count == 2

    def test_batch_evaluate(self):
        evaluator = ContextEvaluator()
        turns = [
            (["KE-001", "KE-002"], ["KE-001"]),
            (["KE-003"], ["KE-003"]),
        ]
        reports = evaluator.batch_evaluate(turns)
        assert len(reports) == 2
        assert reports[0].cited_count == 1
        assert reports[1].cited_count == 1
        assert reports[1].citation_rate == 1.0

    def test_batch_evaluate_empty(self):
        evaluator = ContextEvaluator()
        reports = evaluator.batch_evaluate([])
        assert reports == []


class TestEvaluationReport:
    def test_default_values(self):
        report = EvaluationReport()
        assert report.injected_count == 0
        assert report.cited_count == 0
        assert report.citation_rate == 0.0
        assert report.unused_ke_ids == []
        assert report.efficiency_score == 0.0

    def test_efficiency_score_range(self):
        evaluator = ContextEvaluator()
        report = evaluator.evaluate(
            injected_ids=["KE-001", "KE-002", "KE-003", "KE-004"],
            cited_ids=["KE-001"],
        )
        assert 0.0 <= report.efficiency_score <= 100.0
