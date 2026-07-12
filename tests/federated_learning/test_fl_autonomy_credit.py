# [A_test] module_id: SRC-TST-0934 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_autonomy_credit
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.autonomy_credit
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_autonomy_credit.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.autonomy_credit import AutonomyCredit


class TestAutonomyCreditInstantiation:
    def test_default_construction(self):
        ac = AutonomyCredit()
        assert ac.score == 100.0
        assert ac.decay_per_day == 1.0

    def test_custom_construction(self):
        ac = AutonomyCredit(score=50.0, decay_per_day=0.5)
        assert ac.score == 50.0
        assert ac.decay_per_day == 0.5


class TestScoreDecay:
    def test_score_remains_at_default(self):
        ac = AutonomyCredit()
        assert ac.score == 100.0

    def test_manual_score_reduction(self):
        ac = AutonomyCredit(score=80.0)
        ac.score -= ac.decay_per_day
        assert ac.score == 79.0

    def test_score_never_negative(self):
        ac = AutonomyCredit(score=0.5, decay_per_day=1.0)
        ac.score = max(0.0, ac.score - ac.decay_per_day)
        assert ac.score == 0.0


class TestBoundaries:
    def test_zero_score(self):
        ac = AutonomyCredit(score=0.0)
        assert ac.score == 0.0

    def test_negative_decay_rate(self):
        ac = AutonomyCredit(decay_per_day=-1.0)
        assert ac.decay_per_day == -1.0
