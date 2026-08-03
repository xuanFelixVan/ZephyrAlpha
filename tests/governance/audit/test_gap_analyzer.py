# [A_test] module_id: SRC-TST-1039 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_gap_analyzer
# [DOMAIN] D_GOV_AUDIT
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_gap_analyzer.py -q
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.architecture_governance.gap_analyzer import GapAnalyzer


class TestGapAnalyzerInstantiation:
    def test_init_creates_empty_covered_operations(self):
        ga = GapAnalyzer()
        assert ga.covered_operations == set()

    def test_init_creates_empty_observed_operations(self):
        ga = GapAnalyzer()
        assert ga.observed_operations == set()


class TestGapAnalyzerRegisterCoverage:
    def test_register_single_operation(self):
        ga = GapAnalyzer()
        ga.register_coverage("read")
        assert "read" in ga.covered_operations

    def test_register_multiple_operations(self):
        ga = GapAnalyzer()
        ga.register_coverage("read")
        ga.register_coverage("write")
        assert ga.covered_operations == {"read", "write"}

    def test_register_duplicate_operation_idempotent(self):
        ga = GapAnalyzer()
        ga.register_coverage("read")
        ga.register_coverage("read")
        assert len(ga.covered_operations) == 1


class TestGapAnalyzerObserveOperation:
    def test_observe_single_operation(self):
        ga = GapAnalyzer()
        ga.observe_operation("read")
        assert "read" in ga.observed_operations

    def test_observe_multiple_operations(self):
        ga = GapAnalyzer()
        ga.observe_operation("read")
        ga.observe_operation("write")
        assert ga.observed_operations == {"read", "write"}

    def test_observe_duplicate_idempotent(self):
        ga = GapAnalyzer()
        ga.observe_operation("read")
        ga.observe_operation("read")
        assert len(ga.observed_operations) == 1


class TestGapAnalyzerFindGaps:
    def test_no_gaps_when_fully_covered(self):
        ga = GapAnalyzer()
        ga.observe_operation("read")
        ga.observe_operation("write")
        ga.register_coverage("read")
        ga.register_coverage("write")
        assert ga.find_gaps() == []

    def test_gaps_when_partially_covered(self):
        ga = GapAnalyzer()
        ga.observe_operation("read")
        ga.observe_operation("write")
        ga.observe_operation("delete")
        ga.register_coverage("read")
        gaps = ga.find_gaps()
        assert set(gaps) == {"write", "delete"}

    def test_all_gaps_when_no_coverage(self):
        ga = GapAnalyzer()
        ga.observe_operation("read")
        ga.observe_operation("write")
        assert set(ga.find_gaps()) == {"read", "write"}

    def test_no_gaps_when_nothing_observed(self):
        ga = GapAnalyzer()
        ga.register_coverage("read")
        assert ga.find_gaps() == []

    def test_no_gaps_when_empty(self):
        ga = GapAnalyzer()
        assert ga.find_gaps() == []

    def test_extra_coverage_not_in_gaps(self):
        ga = GapAnalyzer()
        ga.observe_operation("read")
        ga.register_coverage("read")
        ga.register_coverage("write")
        assert ga.find_gaps() == []


class TestGapAnalyzerCoverageRatio:
    def test_full_coverage_ratio(self):
        ga = GapAnalyzer()
        ga.observe_operation("read")
        ga.observe_operation("write")
        ga.register_coverage("read")
        ga.register_coverage("write")
        assert ga.coverage_ratio() == 1.0

    def test_half_coverage_ratio(self):
        ga = GapAnalyzer()
        ga.observe_operation("read")
        ga.observe_operation("write")
        ga.register_coverage("read")
        assert ga.coverage_ratio() == 0.5

    def test_zero_coverage_ratio(self):
        ga = GapAnalyzer()
        ga.observe_operation("read")
        ga.observe_operation("write")
        assert ga.coverage_ratio() == 0.0

    def test_empty_analyzer_ratio_is_zero(self):
        ga = GapAnalyzer()
        assert ga.coverage_ratio() == 0.0

    def test_one_third_coverage_ratio(self):
        ga = GapAnalyzer()
        ga.observe_operation("a")
        ga.observe_operation("b")
        ga.observe_operation("c")
        ga.register_coverage("a")
        assert ga.coverage_ratio() == pytest.approx(1 / 3)
