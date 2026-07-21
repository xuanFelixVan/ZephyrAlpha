# [A_test] module_id: MOD-GOV_cold_start_booster | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_cold_start_booster
# [INVARIANTS] cold_start_when_below_min;auto_seed_strategy;manual_tune_when_sufficient
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_cold_start_booster.py
# [TTL] task_bound

from zephyr.autonomy_core.context.cold_start_booster import ColdStartBooster, ColdStartProfile


class TestColdStartProfile:
    def test_creation(self):
        p = ColdStartProfile(ke_count=3, strategy="auto_seed", estimated_commit_count=200)
        assert p.ke_count == 3
        assert p.strategy == "auto_seed"
        assert p.estimated_commit_count == 200


class TestColdStartBooster:
    def test_cold_start_detected(self):
        booster = ColdStartBooster()
        profile = booster.detect_cold_start(ke_count=2, min_count=5)
        assert profile.strategy == "auto_seed"
        assert profile.ke_count == 2
        assert profile.estimated_commit_count > 0

    def test_no_cold_start(self):
        booster = ColdStartBooster()
        profile = booster.detect_cold_start(ke_count=10, min_count=5)
        assert profile.strategy == "manual_tune"
        assert profile.estimated_commit_count == 0

    def test_exactly_at_threshold(self):
        booster = ColdStartBooster()
        profile = booster.detect_cold_start(ke_count=5, min_count=5)
        assert profile.strategy == "manual_tune"

    def test_one_below_threshold(self):
        booster = ColdStartBooster()
        profile = booster.detect_cold_start(ke_count=4, min_count=5)
        assert profile.strategy == "auto_seed"
        assert profile.estimated_commit_count == 100

    def test_zero_ke_count(self):
        booster = ColdStartBooster()
        profile = booster.detect_cold_start(ke_count=0, min_count=5)
        assert profile.strategy == "auto_seed"
        assert profile.estimated_commit_count == 500

    def test_custom_min_count(self):
        booster = ColdStartBooster()
        profile = booster.detect_cold_start(ke_count=8, min_count=10)
        assert profile.strategy == "auto_seed"

    def test_estimated_commit_formula(self):
        booster = ColdStartBooster()
        profile = booster.detect_cold_start(ke_count=3, min_count=5)
        assert profile.estimated_commit_count == 100 * (5 - 3)
