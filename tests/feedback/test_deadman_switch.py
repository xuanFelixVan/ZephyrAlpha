# [A_test] module_id: SRC-TST-0712 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_deadman_switch
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.resilience.deadman_switch
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_deadman_switch.py
# [TTL] task_bound


from zephyr.feedback_loop.resilience.deadman_switch import (
    DeadmanState,
    DeadmanSwitch,
)


class TestDeadmanSwitchInstantiation:
    def test_default_instantiation(self):
        ds = DeadmanSwitch()
        assert ds.heartbeat_interval == 60.0
        assert ds.max_missed == 3
        assert ds.state == DeadmanState.ALIVE
        assert ds.missed_count == 0
        assert ds.last_beat > 0

    def test_custom_instantiation(self):
        ds = DeadmanSwitch(heartbeat_interval=30.0, max_missed=5)
        assert ds.heartbeat_interval == 30.0
        assert ds.max_missed == 5


class TestHeartbeat:
    def test_heartbeat_resets_missed_count(self):
        ds = DeadmanSwitch()
        ds.missed_count = 2
        state = ds.heartbeat()
        assert ds.missed_count == 0
        assert state == DeadmanState.ALIVE

    def test_heartbeat_recovers_from_warning(self):
        ds = DeadmanSwitch()
        ds.state = DeadmanState.WARNING
        state = ds.heartbeat()
        assert state == DeadmanState.ALIVE

    def test_heartbeat_does_not_recover_from_locked(self):
        ds = DeadmanSwitch()
        ds.state = DeadmanState.LOCKED
        state = ds.heartbeat()
        assert state == DeadmanState.LOCKED


class TestCheck:
    def test_check_within_interval_stays_alive(self):
        ds = DeadmanSwitch(heartbeat_interval=9999.0)
        state = ds.check()
        assert state == DeadmanState.ALIVE

    def test_check_after_interval_increments_missed(self):
        ds = DeadmanSwitch(heartbeat_interval=-1.0, max_missed=5)
        ds.check()
        assert ds.missed_count >= 1

    def test_check_warning_after_one_miss(self):
        ds = DeadmanSwitch(heartbeat_interval=-1.0, max_missed=3)
        ds.check()
        assert ds.state == DeadmanState.WARNING

    def test_check_locked_after_max_missed(self):
        ds = DeadmanSwitch(heartbeat_interval=-1.0, max_missed=1)
        ds.check()
        assert ds.state == DeadmanState.LOCKED


class TestIsLocked:
    def test_not_locked_initially(self):
        ds = DeadmanSwitch()
        assert ds.is_locked is False

    def test_locked_after_max_missed(self):
        ds = DeadmanSwitch(heartbeat_interval=-1.0, max_missed=1)
        ds.check()
        assert ds.is_locked is True
