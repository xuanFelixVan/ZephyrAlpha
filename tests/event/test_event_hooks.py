# [A_test] module_id: MOD-GOV_event_hooks | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_event_hooks
# [INVARIANTS] 测试覆盖register/unregister/emit/emit_for_status/get_event_log;边界:空输入/None/异常
# [MODIFY-GUARD] blueprint.md §3
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.infrastructure.auto_fix_engine.event_hooks import EventHooks, FixEvent
from zephyr.infrastructure.auto_fix_engine.models import FixAction, FixLevel, FixStatus


def _make_action(status: FixStatus = FixStatus.PENDING, escalated: bool = False) -> FixAction:
    return FixAction(
        action_type="drift_fix",
        target="t.py",
        level=FixLevel.L1_RULE,
        status=status,
        escalated=escalated,
    )


class TestEventHooksInstantiation:
    def test_empty_hooks(self):
        eh = EventHooks()
        assert eh._hooks == {}

    def test_empty_event_log(self):
        eh = EventHooks()
        assert eh._event_log == []


class TestRegister:
    def test_register_callback(self):
        eh = EventHooks()
        cb = MagicMock()
        eh.register(FixEvent.FIX_STARTED, cb)
        assert FixEvent.FIX_STARTED in eh._hooks
        assert cb in eh._hooks[FixEvent.FIX_STARTED]

    def test_register_multiple_callbacks(self):
        eh = EventHooks()
        cb1 = MagicMock()
        cb2 = MagicMock()
        eh.register(FixEvent.FIX_STARTED, cb1)
        eh.register(FixEvent.FIX_STARTED, cb2)
        assert len(eh._hooks[FixEvent.FIX_STARTED]) == 2


class TestUnregister:
    def test_unregister_callback(self):
        eh = EventHooks()
        cb = MagicMock()
        eh.register(FixEvent.FIX_STARTED, cb)
        eh.unregister(FixEvent.FIX_STARTED, cb)
        assert cb not in eh._hooks.get(FixEvent.FIX_STARTED, [])

    def test_unregister_nonexistent_callback(self):
        eh = EventHooks()
        cb = MagicMock()
        eh.unregister(FixEvent.FIX_STARTED, cb)

    def test_unregister_nonexistent_event(self):
        eh = EventHooks()
        eh.unregister(FixEvent.FIX_STARTED, MagicMock())


class TestEmit:
    def test_emit_logs_event(self):
        eh = EventHooks()
        action = _make_action()
        eh.emit(FixEvent.FIX_STARTED, action)
        log = eh.get_event_log(limit=10)
        assert len(log) == 1
        assert log[0]["event"] == "fix_started"
        assert log[0]["action_id"] == action.action_id

    def test_emit_without_action(self):
        eh = EventHooks()
        eh.emit(FixEvent.FIX_STARTED)
        log = eh.get_event_log()
        assert len(log) == 1
        assert log[0]["action_id"] is None

    def test_emit_calls_callbacks(self):
        eh = EventHooks()
        cb = MagicMock()
        eh.register(FixEvent.FIX_STARTED, cb)
        action = _make_action()
        eh.emit(FixEvent.FIX_STARTED, action)
        cb.assert_called_once()

    def test_emit_callback_exception_does_not_propagate(self):
        eh = EventHooks()
        cb = MagicMock(side_effect=RuntimeError("callback boom"))
        eh.register(FixEvent.FIX_STARTED, cb)
        eh.emit(FixEvent.FIX_STARTED)
        assert len(eh.get_event_log()) == 1

    def test_emit_kwargs_passed(self):
        eh = EventHooks()
        cb = MagicMock()
        eh.register(FixEvent.FIX_STARTED, cb)
        eh.emit(FixEvent.FIX_STARTED, detail="extra")
        cb.assert_called_once()
        call_kwargs = cb.call_args
        assert call_kwargs.kwargs.get("detail") == "extra"


class TestEmitForStatus:
    def test_completed_status(self):
        eh = EventHooks()
        action = _make_action(status=FixStatus.COMPLETED)
        eh.emit_for_status(action)
        log = eh.get_event_log()
        assert any(r["event"] == "fix_completed" for r in log)

    def test_failed_status(self):
        eh = EventHooks()
        action = _make_action(status=FixStatus.FAILED)
        eh.emit_for_status(action)
        log = eh.get_event_log()
        assert any(r["event"] == "fix_failed" for r in log)

    def test_escalated_action(self):
        eh = EventHooks()
        action = _make_action(status=FixStatus.FAILED, escalated=True)
        eh.emit_for_status(action)
        log = eh.get_event_log()
        events = [r["event"] for r in log]
        assert "fix_escalated" in events

    def test_pending_status_no_event(self):
        eh = EventHooks()
        action = _make_action(status=FixStatus.PENDING)
        eh.emit_for_status(action)
        log = eh.get_event_log()
        assert len(log) == 0


class TestGetEventLog:
    def test_limit(self):
        eh = EventHooks()
        for _ in range(10):
            eh.emit(FixEvent.FIX_STARTED)
        log = eh.get_event_log(limit=3)
        assert len(log) == 3

    def test_filter_by_event_type(self):
        eh = EventHooks()
        eh.emit(FixEvent.FIX_STARTED)
        eh.emit(FixEvent.FIX_COMPLETED)
        log = eh.get_event_log(event_type="fix_completed")
        assert len(log) == 1
        assert log[0]["event"] == "fix_completed"

    def test_empty_log(self):
        eh = EventHooks()
        log = eh.get_event_log()
        assert log == []


class TestClearHooks:
    def test_clear_hooks(self):
        eh = EventHooks()
        eh.register(FixEvent.FIX_STARTED, MagicMock())
        eh.clear_hooks()
        assert eh._hooks == {}


class TestClearLog:
    def test_clear_log(self):
        eh = EventHooks()
        eh.emit(FixEvent.FIX_STARTED)
        eh.clear_log()
        assert eh._event_log == []


class TestFixEventEnum:
    def test_all_events_have_values(self):
        for event in FixEvent:
            assert isinstance(event.value, str)
            assert len(event.value) > 0
