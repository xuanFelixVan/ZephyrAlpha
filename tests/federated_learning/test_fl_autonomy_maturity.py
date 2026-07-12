# [A_test] module_id: SRC-TST-0935 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_autonomy_maturity
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.autonomy_maturity
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_autonomy_maturity.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.autonomy_maturity import AutonomyMaturity


class TestAutonomyMaturityInstantiation:
    def test_default_construction(self):
        am = AutonomyMaturity()
        assert am.level == 0

    def test_custom_level(self):
        am = AutonomyMaturity(level=3)
        assert am.level == 3


class TestLevelProgression:
    def test_level_starts_at_zero(self):
        am = AutonomyMaturity()
        assert am.level == 0

    def test_level_can_advance(self):
        am = AutonomyMaturity()
        am.level = 1
        assert am.level == 1
        am.level = 2
        assert am.level == 2

    def test_max_level_is_four(self):
        am = AutonomyMaturity(level=4)
        assert am.level == 4


class TestBoundaries:
    def test_level_below_zero(self):
        am = AutonomyMaturity(level=-1)
        assert am.level == -1

    def test_level_above_max(self):
        am = AutonomyMaturity(level=5)
        assert am.level == 5
