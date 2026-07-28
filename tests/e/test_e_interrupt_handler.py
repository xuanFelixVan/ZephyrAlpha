# [A_test] module_id: MOD-GOV_e_interrupt_handler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_interrupt_handler
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.interrupt_handler import InterruptHandler, InterruptSignal


class TestInterruptSignal:
    def test_three_signals(self):
        assert len(InterruptSignal) == 3

    def test_values(self):
        assert InterruptSignal.OWNER_OVERRIDE.value == "owner_override"
        assert InterruptSignal.SAFETY_BREACH.value == "safety_breach"
        assert InterruptSignal.HARD_TIMEOUT.value == "hard_timeout"


class TestInterruptHandlerInit:
    def test_default_not_interrupted(self):
        ih = InterruptHandler()
        assert ih.interrupted is False
        assert ih.signal is None


class TestInterruptHandlerInterrupt:
    def test_owner_override(self):
        ih = InterruptHandler()
        ih.interrupt(InterruptSignal.OWNER_OVERRIDE)
        assert ih.interrupted is True
        assert ih.signal == InterruptSignal.OWNER_OVERRIDE

    def test_safety_breach(self):
        ih = InterruptHandler()
        ih.interrupt(InterruptSignal.SAFETY_BREACH)
        assert ih.interrupted is True
        assert ih.signal == InterruptSignal.SAFETY_BREACH

    def test_hard_timeout(self):
        ih = InterruptHandler()
        ih.interrupt(InterruptSignal.HARD_TIMEOUT)
        assert ih.interrupted is True


class TestInterruptHandlerSaveState:
    def test_no_interrupt(self):
        ih = InterruptHandler()
        state = ih.save_state()
        assert state["interrupted"] is False
        assert state["signal"] is None

    def test_after_interrupt(self):
        ih = InterruptHandler()
        ih.interrupt(InterruptSignal.OWNER_OVERRIDE)
        state = ih.save_state()
        assert state["interrupted"] is True
        assert state["signal"] == "owner_override"


class TestInterruptHandlerResume:
    def test_resets_state(self):
        ih = InterruptHandler()
        ih.interrupt(InterruptSignal.SAFETY_BREACH)
        assert ih.resume() is True
        assert ih.interrupted is False
        assert ih.signal is None

    def test_resume_when_not_interrupted(self):
        ih = InterruptHandler()
        assert ih.resume() is True
        assert ih.interrupted is False
