# [A_test] module_id: SRC-TST-0386 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_autonomy_credit
# [INVARIANTS] Score must be non-negative float; decay must reduce score
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.autonomy_credit import AutonomyCredit


class TestAutonomyCreditInstantiation:
    def test_default_values(self):
        ac = AutonomyCredit()
        assert ac.score == 100.0
        assert ac.decay_per_day == 1.0

    def test_custom_values(self):
        ac = AutonomyCredit(score=50.0, decay_per_day=2.0)
        assert ac.score == 50.0
        assert ac.decay_per_day == 2.0
