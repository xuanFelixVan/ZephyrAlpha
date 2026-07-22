# [A_test] module_id: MOD-GOV_interrupt_handler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_interrupt_handler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_interrupt_handler.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.interrupt_handler import InterruptHandler, InterruptSignal


class TestInterruptSignalEnum:
    def test_owner_override_value(self):
        assert InterruptSignal.OWNER_OVERRIDE.value == "owner_override"

    def test_safety_breach_value(self):
        assert InterruptSignal.SAFETY_BREACH.value == "safety_breach"

    def test_hard_timeout_value(self):
        assert InterruptSignal.HARD_TIMEOUT.value == "hard_timeout"

    def test_enum_members_count(self):
        assert len(InterruptSignal) == 3


class TestInterruptHandlerInstantiation:
    def test_creates_instance_not_interrupted(self):
        handler = InterruptHandler()
        assert handler.interrupted is False

    def test_initial_signal_is_none(self):
        handler = InterruptHandler()
        state = handler.save_state()
        assert state["signal"] is None


class TestInterrupt:
    def test_interrupt_sets_interrupted_true(self):
        handler = InterruptHandler()
        handler.interrupt(InterruptSignal.OWNER_OVERRIDE)
        assert handler.interrupted is True

    def test_interrupt_stores_signal(self):
        handler = InterruptHandler()
        handler.interrupt(InterruptSignal.SAFETY_BREACH)
        state = handler.save_state()
        assert state["signal"] == "safety_breach"

    def test_interrupt_with_hard_timeout(self):
        handler = InterruptHandler()
        handler.interrupt(InterruptSignal.HARD_TIMEOUT)
        state = handler.save_state()
        assert state["signal"] == "hard_timeout"

    def test_interrupt_overwrites_previous_signal(self):
        handler = InterruptHandler()
        handler.interrupt(InterruptSignal.OWNER_OVERRIDE)
        handler.interrupt(InterruptSignal.SAFETY_BREACH)
        state = handler.save_state()
        assert state["signal"] == "safety_breach"


class TestSaveState:
    def test_save_state_returns_dict(self):
        handler = InterruptHandler()
        state = handler.save_state()
        assert isinstance(state, dict)

    def test_save_state_initial(self):
        handler = InterruptHandler()
        state = handler.save_state()
        assert state == {"interrupted": False, "signal": None}

    def test_save_state_after_interrupt(self):
        handler = InterruptHandler()
        handler.interrupt(InterruptSignal.HARD_TIMEOUT)
        state = handler.save_state()
        assert state == {"interrupted": True, "signal": "hard_timeout"}


class TestResume:
    def test_resume_resets_interrupted(self):
        handler = InterruptHandler()
        handler.interrupt(InterruptSignal.OWNER_OVERRIDE)
        handler.resume()
        assert handler.interrupted is False

    def test_resume_clears_signal(self):
        handler = InterruptHandler()
        handler.interrupt(InterruptSignal.SAFETY_BREACH)
        handler.resume()
        state = handler.save_state()
        assert state["signal"] is None

    def test_resume_returns_true(self):
        handler = InterruptHandler()
        handler.interrupt(InterruptSignal.HARD_TIMEOUT)
        result = handler.resume()
        assert result is True

    def test_resume_when_not_interrupted(self):
        handler = InterruptHandler()
        result = handler.resume()
        assert result is True
        assert handler.interrupted is False


class TestInterruptHandlerBoundary:
    def test_multiple_interrupt_resume_cycles(self):
        handler = InterruptHandler()
        for signal in InterruptSignal:
            handler.interrupt(signal)
            assert handler.interrupted is True
            handler.resume()
            assert handler.interrupted is False

    def test_interrupt_then_save_state_preserves_signal(self):
        handler = InterruptHandler()
        handler.interrupt(InterruptSignal.OWNER_OVERRIDE)
        state1 = handler.save_state()
        state2 = handler.save_state()
        assert state1 == state2
