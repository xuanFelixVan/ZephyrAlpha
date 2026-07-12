# [A_test] module_id: SRC-TST-1294 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_monoculture_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.monoculture_guard import (
    BlastRadiusScore,
    MonocultureGuard,
)


class TestMonocultureGuard:
    def test_instantiation(self):
        guard = MonocultureGuard()
        assert guard is not None

    def test_compute_brs(self):
        guard = MonocultureGuard()
        result = guard.compute_brs(caller_count=10, cross_layer_count=2)
        assert isinstance(result, BlastRadiusScore)
        assert result.blast_radius_score >= 0

    def test_should_block_dedup(self):
        guard = MonocultureGuard()
        brs = guard.compute_brs(caller_count=10, cross_layer_count=2)
        result = guard.should_block_dedup(brs)
        assert isinstance(result, bool)

    def test_generate_report_returns_str(self):
        guard = MonocultureGuard()
        brs = guard.compute_brs(caller_count=10, cross_layer_count=2)
        result = guard.generate_report("shared_func", brs)
        assert isinstance(result, str)

    def test_compute_brs_zero_callers(self):
        guard = MonocultureGuard()
        result = guard.compute_brs(caller_count=0, cross_layer_count=0)
        assert isinstance(result, BlastRadiusScore)
        assert result.level == "SAFE"

    def test_compute_brs_dangerous(self):
        guard = MonocultureGuard()
        result = guard.compute_brs(
            caller_count=20,
            cross_layer_count=5,
            on_critical_path=True,
            has_independent_unit_test=False,
        )
        assert result.level == "DANGEROUS"
        assert guard.should_block_dedup(result) is True
