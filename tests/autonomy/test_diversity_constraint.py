# [A_test] module_id: MOD-GOV_diversity_constraint | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_diversity_constraint
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_diversity_constraint.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.autonomy_core.context.diversity_constraint import DiversityConstraint, DiversityReport


class TestDiversityReport:
    def test_instantiation_with_all_fields(self):
        dr = DiversityReport(
            source_distribution={"a": 3, "b": 2},
            gini_coefficient=0.45,
            overrepresented=[],
            action="OK",
        )
        assert dr.source_distribution == {"a": 3, "b": 2}
        assert dr.gini_coefficient == 0.45
        assert dr.overrepresented == []
        assert dr.action == "OK"

    def test_equality(self):
        a = DiversityReport(source_distribution={}, gini_coefficient=0.0, overrepresented=[], action="OK")
        b = DiversityReport(source_distribution={}, gini_coefficient=0.0, overrepresented=[], action="OK")
        assert a == b


class TestDiversityConstraint:
    def test_instantiation(self):
        dc = DiversityConstraint()
        assert dc is not None

    def test_analyze_returns_diversity_report(self):
        dc = DiversityConstraint()
        result = dc.analyze(["src_a", "src_b", "src_c"])
        assert isinstance(result, DiversityReport)

    def test_analyze_source_distribution_counts(self):
        dc = DiversityConstraint()
        result = dc.analyze(["a", "a", "b", "c"])
        assert result.source_distribution == {"a": 2, "b": 1, "c": 1}

    def test_analyze_single_source(self):
        dc = DiversityConstraint()
        result = dc.analyze(["only_one", "only_one", "only_one"])
        assert result.source_distribution == {"only_one": 3}

    def test_analyze_action_is_ok(self):
        dc = DiversityConstraint()
        result = dc.analyze(["x", "y"])
        assert result.action == "OK"

    def test_analyze_overrepresented_is_empty_list(self):
        dc = DiversityConstraint()
        result = dc.analyze(["x", "y", "z"])
        assert result.overrepresented == []

    def test_analyze_gini_coefficient_is_float(self):
        dc = DiversityConstraint()
        result = dc.analyze(["a", "b", "c"])
        assert isinstance(result.gini_coefficient, float)

    def test_analyze_empty_sources(self):
        dc = DiversityConstraint()
        result = dc.analyze([])
        assert result.source_distribution == {}
        assert result.gini_coefficient == 0.0
        assert result.action == "OK"

    def test_analyze_single_element_list(self):
        dc = DiversityConstraint()
        result = dc.analyze(["solo"])
        assert result.source_distribution == {"solo": 1}
        assert result.gini_coefficient == 0.0

    def test_analyze_many_sources_distribution(self):
        dc = DiversityConstraint()
        sources = ["a"] * 10 + ["b"] * 10 + ["c"] * 10
        result = dc.analyze(sources)
        assert result.source_distribution == {"a": 10, "b": 10, "c": 10}

    def test_analyze_gini_rounded_to_two_decimals(self):
        dc = DiversityConstraint()
        result = dc.analyze(["a", "b", "c", "d"])
        assert result.gini_coefficient == round(result.gini_coefficient, 2)
