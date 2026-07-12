# [A_test] module_id: SRC-TST-1568 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_self_upgrade_canary
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.self_upgrade_canary
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_self_upgrade_canary.py
# [TTL] task_bound


from zephyr.feedback_loop.evolution.self_upgrade_canary import (
    CanaryPhase,
    SelfUpgradeCanary,
)


class TestSelfUpgradeCanaryInstantiation:
    def test_default_instantiation(self):
        obj = SelfUpgradeCanary()
        assert obj is not None
        assert obj.current_phase == CanaryPhase.INIT
        assert obj.steps == []

    def test_is_dataclass(self):
        obj = SelfUpgradeCanary()
        assert hasattr(obj, "__dataclass_fields__")


class TestSelfUpgradeCanaryAdvance:
    def test_advance_from_init(self):
        suc = SelfUpgradeCanary()
        phase = suc.advance(health_ok=True)
        assert phase == CanaryPhase.CANARY_5

    def test_advance_through_phases(self):
        suc = SelfUpgradeCanary()
        suc.advance(health_ok=True)
        phase = suc.advance(health_ok=True)
        assert phase == CanaryPhase.CANARY_25

    def test_advance_to_full(self):
        suc = SelfUpgradeCanary()
        suc.advance(health_ok=True)
        suc.advance(health_ok=True)
        suc.advance(health_ok=True)
        phase = suc.advance(health_ok=True)
        assert phase == CanaryPhase.FULL_100

    def test_advance_beyond_full_stays(self):
        suc = SelfUpgradeCanary()
        suc.advance(health_ok=True)
        suc.advance(health_ok=True)
        suc.advance(health_ok=True)
        suc.advance(health_ok=True)
        phase = suc.advance(health_ok=True)
        assert phase == CanaryPhase.FULL_100

    def test_advance_with_bad_health_rollback(self):
        suc = SelfUpgradeCanary()
        suc.advance(health_ok=True)
        phase = suc.advance(health_ok=False)
        assert phase == CanaryPhase.ROLLED_BACK


class TestSelfUpgradeCanaryRollback:
    def test_rollback_sets_phase(self):
        suc = SelfUpgradeCanary()
        suc.advance(health_ok=True)
        suc.rollback()
        assert suc.current_phase == CanaryPhase.ROLLED_BACK

    def test_rollback_from_init(self):
        suc = SelfUpgradeCanary()
        suc.rollback()
        assert suc.current_phase == CanaryPhase.ROLLED_BACK


class TestSelfUpgradeCanaryBoundaries:
    def test_advance_records_steps(self):
        suc = SelfUpgradeCanary()
        suc.advance(health_ok=True)
        assert len(suc.steps) == 1
        assert suc.steps[0].health_check_pass is True

    def test_rollback_from_full(self):
        suc = SelfUpgradeCanary()
        for _ in range(4):
            suc.advance(health_ok=True)
        suc.rollback()
        assert suc.current_phase == CanaryPhase.ROLLED_BACK

    def test_multiple_rollbacks(self):
        suc = SelfUpgradeCanary()
        suc.rollback()
        suc.rollback()
        assert suc.current_phase == CanaryPhase.ROLLED_BACK
