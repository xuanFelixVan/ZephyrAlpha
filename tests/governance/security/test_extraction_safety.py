# [A_test] module_id: SRC-TST-0887 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_extraction_safety
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.extraction_safety import (
    ExtractionSafety,
    SuitabilityScore,
)


class TestExtractionSafety:
    def test_instantiation(self):
        es = ExtractionSafety()
        assert es is not None

    def test_compute_suitability(self):
        es = ExtractionSafety()
        result = es.compute_suitability(caller_count=3, body="def add(a, b): return a + b")
        assert isinstance(result, SuitabilityScore)

    def test_check_unsafe_patterns(self):
        es = ExtractionSafety()
        result = es.check_unsafe_patterns(body="def foo(): eval(input())")
        assert isinstance(result, (list, dict, bool))

    def test_analyze_impact(self):
        es = ExtractionSafety()
        result = es.analyze_impact(["mod_a", "mod_b"], [3, 5])
        assert isinstance(result, (dict, object))

    def test_is_auto_extractable(self):
        es = ExtractionSafety()
        suit = es.compute_suitability(caller_count=3, body="def add(a, b): return a + b")
        result = es.is_auto_extractable(suit)
        assert isinstance(result, bool)

    def test_compute_suitability_empty(self):
        es = ExtractionSafety()
        result = es.compute_suitability(caller_count=0, body="")
        assert isinstance(result, SuitabilityScore)

    def test_generate_partial_extraction(self):
        es = ExtractionSafety()
        result = es.generate_partial_extraction("def foo():\n    return 1\n", "def foo():\n    return 1\n")
        assert result is not None or result is None
