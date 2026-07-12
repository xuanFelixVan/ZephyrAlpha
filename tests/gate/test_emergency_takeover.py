# [A_test] module_id: SRC-TST-0829 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_emergency_takeover
# [INVARIANTS] Emergency takeover must be irreversible once triggered
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.emergency_takeover import EmergencyTakeover


class TestEmergencyTakeoverInstantiation:
    def test_default_not_active(self):
        et = EmergencyTakeover()
        assert et.active is False

    def test_custom_active(self):
        et = EmergencyTakeover(active=True)
        assert et.active is True


class TestTrigger:
    def test_trigger_activates(self):
        et = EmergencyTakeover()
        et.trigger()
        assert et.active is True

    def test_trigger_idempotent(self):
        et = EmergencyTakeover()
        et.trigger()
        et.trigger()
        assert et.active is True

    def test_trigger_from_inactive(self):
        et = EmergencyTakeover(active=False)
        assert et.active is False
        et.trigger()
        assert et.active is True
