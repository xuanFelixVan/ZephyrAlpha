# [A_test] module_id: MOD-GOV_e_gap_analyzer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_gap_analyzer
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.architecture_governance.gap_analyzer import GapAnalyzer


class TestGapAnalyzerInit:
    def test_default_state(self):
        ga = GapAnalyzer()
        assert ga._covered_operations == set()
        assert ga._observed_operations == set()

    def test_register_coverage(self):
        ga = GapAnalyzer()
        ga.register_coverage("file_write")
        assert "file_write" in ga._covered_operations

    def test_observe_operation(self):
        ga = GapAnalyzer()
        ga.observe_operation("network_call")
        assert "network_call" in ga._observed_operations


class TestGapAnalyzerFindGaps:
    def test_no_gaps_when_all_covered(self):
        ga = GapAnalyzer()
        ga.register_coverage("op1")
        ga.observe_operation("op1")
        assert ga.find_gaps() == []

    def test_finds_uncovered_operations(self):
        ga = GapAnalyzer()
        ga.register_coverage("op1")
        ga.observe_operation("op1")
        ga.observe_operation("op2")
        gap = ga.find_gaps()
        assert "op2" in gap

    def test_empty_observed_no_gaps(self):
        ga = GapAnalyzer()
        ga.register_coverage("op1")
        assert ga.find_gaps() == []


class TestGapAnalyzerCoverageRatio:
    def test_full_coverage(self):
        ga = GapAnalyzer()
        ga.register_coverage("op1")
        ga.observe_operation("op1")
        assert ga.coverage_ratio() == 1.0

    def test_partial_coverage(self):
        ga = GapAnalyzer()
        ga.register_coverage("op1")
        ga.observe_operation("op1")
        ga.observe_operation("op2")
        assert ga.coverage_ratio() == 0.5

    def test_zero_observed(self):
        ga = GapAnalyzer()
        ga.register_coverage("op1")
        assert ga.coverage_ratio() == 1.0
