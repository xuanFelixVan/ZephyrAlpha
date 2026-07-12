# [A_test] module_id: SRC-TST-1577 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_sensitivity_sweeper
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.sensitivity_sweeper import (
    SensitivitySweeper,
    SweepResult,
)


class TestSensitivitySweeper:
    def test_instantiation(self):
        sweeper = SensitivitySweeper()
        assert sweeper is not None

    def test_sweep(self):
        sweeper = SensitivitySweeper()
        result = sweeper.sweep(threshold=0.8, detected=10, confirmed_clones=8, false_positives=2)
        assert isinstance(result, SweepResult)
        assert result.threshold == 0.8

    def test_get_baseline(self):
        sweeper = SensitivitySweeper()
        result = sweeper.get_baseline()
        assert isinstance(result, float)

    def test_sweep_zero_values(self):
        sweeper = SensitivitySweeper()
        result = sweeper.sweep(threshold=0.0, detected=0, confirmed_clones=0, false_positives=0)
        assert isinstance(result, SweepResult)

    def test_sweep_updates_best_threshold(self):
        sweeper = SensitivitySweeper()
        sweeper.sweep(0.8, 10, 9, 1)
        sweeper.sweep(0.9, 8, 8, 0)
        assert sweeper.best_threshold in (0.8, 0.9)
