# [A_test] module_id: SRC-TST-0389 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_autonomy_maturity
# [INVARIANTS] Level must be non-negative integer
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.autonomy_maturity import AutonomyMaturity


class TestAutonomyMaturityInstantiation:
    def test_default_level_zero(self):
        am = AutonomyMaturity()
        assert am.level == 0

    def test_custom_level(self):
        am = AutonomyMaturity(level=3)
        assert am.level == 3

    def test_level_is_int(self):
        am = AutonomyMaturity()
        assert isinstance(am.level, int)
