# [A_test] module_id: SRC-TST-1266 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_meta_performance_gate
# [INVARIANTS] Gate thresholds must be deterministic
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.meta_performance_gate import MetaPerformanceGate


class TestMetaPerformanceGateInstantiation:
    def test_default_values(self):
        mpg = MetaPerformanceGate()
        assert mpg.mttd_seconds == 300.0
        assert mpg.mttr_seconds == 600.0

    def test_custom_values(self):
        mpg = MetaPerformanceGate(mttd_seconds=120.0, mttr_seconds=240.0)
        assert mpg.mttd_seconds == 120.0
        assert mpg.mttr_seconds == 240.0
