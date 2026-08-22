# [A_test] module_id: MOD-GOV_ce_kill_switch | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.infrastructure.capacity_assurance.kill_switch
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.infrastructure.capacity_assurance.kill_switch import FuseState, KillSwitch

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


class TestFuseState:
    def test_dataclass_fields(self):
        state = FuseState(on=True, trigger_reason="too many errors", manual_reset_needed=True)
        assert state.on is True
        assert state.trigger_reason == "too many errors"
        assert state.manual_reset_needed is True

    def test_fuse_off_state(self):
        state = FuseState(on=False, trigger_reason="", manual_reset_needed=False)
        assert state.on is False
        assert state.trigger_reason == ""

    def test_default_not_applicable(self):
        with pytest.raises(TypeError):
            FuseState()


class TestKillSwitch:
    def test_init_default_threshold(self):
        ks = KillSwitch()
        assert ks.threshold == 5

    def test_init_custom_threshold(self):
        ks = KillSwitch(threshold=3)
        assert ks.threshold == 3

    def test_fuse_off_initially(self):
        ks = KillSwitch()
        assert ks.fuse_on is False
        assert ks.error_count == 0

    def test_record_error_below_threshold(self):
        ks = KillSwitch(threshold=5)
        state = ks.record_error("err1")
        assert state.on is False
        assert ks.error_count == 1

    def test_record_error_reaches_threshold(self):
        ks = KillSwitch(threshold=3)
        ks.record_error("e1")
        ks.record_error("e2")
        state = ks.record_error("e3")
        assert state.on is True
        assert state.trigger_reason == "e3"

    def test_record_error_exceeds_threshold(self):
        ks = KillSwitch(threshold=2)
        ks.record_error("e1")
        ks.record_error("e2")
        state = ks.record_error("e3")
        assert state.on is True

    def test_manual_reset_needed_always_true(self):
        ks = KillSwitch(threshold=1)
        state = ks.record_error("e1")
        assert state.manual_reset_needed is True

    def test_reset_clears_state(self):
        ks = KillSwitch(threshold=2)
        ks.record_error("e1")
        ks.record_error("e2")
        ks.reset()
        assert ks.error_count == 0
        assert ks.fuse_on is False

    def test_reset_allows_new_errors(self):
        ks = KillSwitch(threshold=2)
        ks.record_error("e1")
        ks.record_error("e2")
        ks.reset()
        state = ks.record_error("e3")
        assert state.on is False
        assert ks.error_count == 1

    def test_trigger_reason_preserved(self):
        ks = KillSwitch(threshold=1)
        state = ks.record_error("critical failure")
        assert state.trigger_reason == "critical failure"

    def test_empty_reason(self):
        ks = KillSwitch(threshold=1)
        state = ks.record_error()
        assert state.trigger_reason == ""
        assert state.on is True

    def test_threshold_one(self):
        ks = KillSwitch(threshold=1)
        state = ks.record_error("first error")
        assert state.on is True

    def test_incremental_errors(self):
        ks = KillSwitch(threshold=5)
        for i in range(4):
            state = ks.record_error(f"e{i}")
            assert state.on is False
        state = ks.record_error("e4")
        assert state.on is True
