# [A_test] module_id: MOD-GOV_timeout_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_timeout_guard
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.governance.ops_governance.timeout_guard import (
    DEFAULT_TIMEOUTS,
    TimeoutEvent,
    TimeoutGuard,
    TimeoutLevel,
)


class TestTimeoutLevel:
    def test_enum_values(self):
        assert TimeoutLevel.REQUEST.value == "request"
        assert TimeoutLevel.TURN.value == "turn"
        assert TimeoutLevel.TASK.value == "task"
        assert TimeoutLevel.SESSION.value == "session"

    def test_enum_members(self):
        members = list(TimeoutLevel)
        assert len(members) == 4


class TestTimeoutEvent:
    def test_creation_defaults(self):
        evt = TimeoutEvent(level=TimeoutLevel.REQUEST, scope_id="s1", elapsed=1.0, limit=10.0)
        assert evt.aborted is False
        assert evt.timestamp > 0

    def test_creation_aborted(self):
        evt = TimeoutEvent(level=TimeoutLevel.TURN, scope_id="s2", elapsed=20.0, limit=10.0, aborted=True)
        assert evt.aborted is True


class TestTimeoutGuardInit:
    def test_default_timeouts(self):
        guard = TimeoutGuard()
        assert guard.timeouts == DEFAULT_TIMEOUTS

    def test_custom_timeouts(self):
        custom = {TimeoutLevel.REQUEST: 5.0}
        guard = TimeoutGuard(custom_timeouts=custom)
        assert guard.timeouts[TimeoutLevel.REQUEST] == 5.0
        assert guard.timeouts[TimeoutLevel.TURN] == DEFAULT_TIMEOUTS[TimeoutLevel.TURN]

    def test_empty_custom_timeouts(self):
        guard = TimeoutGuard(custom_timeouts={})
        assert guard.timeouts == DEFAULT_TIMEOUTS

    def test_none_custom_timeouts(self):
        guard = TimeoutGuard(custom_timeouts=None)
        assert guard.timeouts == DEFAULT_TIMEOUTS


class TestTimeoutGuardWatch:
    def test_watch_creates_scope(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 600.0})
        guard.watch(TimeoutLevel.REQUEST, "scope_a")
        assert guard.active_count() == 1
        guard.clear()

    def test_watch_with_handler(self):
        results = []
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 0.05})
        guard.watch(TimeoutLevel.REQUEST, "scope_b", on_timeout=lambda e: results.append(e))
        time.sleep(0.15)
        assert len(results) >= 1
        assert results[0].aborted is True
        guard.clear()

    def test_unwatch_returns_event(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 600.0})
        guard.watch(TimeoutLevel.REQUEST, "scope_c")
        evt = guard.unwatch(TimeoutLevel.REQUEST, "scope_c")
        assert evt is not None
        assert isinstance(evt, TimeoutEvent)
        assert evt.scope_id == "scope_c"
        assert evt.aborted is False
        assert guard.active_count() == 0

    def test_unwatch_nonexistent_returns_event(self):
        guard = TimeoutGuard()
        evt = guard.unwatch(TimeoutLevel.REQUEST, "nonexistent")
        assert evt is not None
        assert evt.elapsed == 0.0


class TestTimeoutGuardCheck:
    def test_check_active_scope(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 600.0})
        guard.watch(TimeoutLevel.REQUEST, "scope_d")
        ratio = guard.check(TimeoutLevel.REQUEST, "scope_d")
        assert ratio >= 0.0
        guard.clear()

    def test_check_inactive_scope(self):
        guard = TimeoutGuard()
        ratio = guard.check(TimeoutLevel.REQUEST, "no_scope")
        assert ratio == 0.0

    def test_is_timeout_false(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 600.0})
        guard.watch(TimeoutLevel.REQUEST, "scope_e")
        assert guard.is_timeout(TimeoutLevel.REQUEST, "scope_e") is False
        guard.clear()

    def test_is_timeout_true_after_expiry(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 0.05})
        guard.watch(TimeoutLevel.REQUEST, "scope_f")
        time.sleep(0.15)
        assert guard.is_timeout(TimeoutLevel.REQUEST, "scope_f") is True
        guard.clear()


class TestTimeoutGuardRemaining:
    def test_remaining_active_scope(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 600.0})
        guard.watch(TimeoutLevel.REQUEST, "scope_g")
        rem = guard.remaining(TimeoutLevel.REQUEST, "scope_g")
        assert rem > 0
        assert rem <= 600.0
        guard.clear()

    def test_remaining_inactive_scope(self):
        guard = TimeoutGuard()
        rem = guard.remaining(TimeoutLevel.REQUEST, "no_scope")
        assert rem == DEFAULT_TIMEOUTS[TimeoutLevel.REQUEST]


class TestTimeoutGuardHelpers:
    def test_active_count(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 600.0, TimeoutLevel.TURN: 600.0})
        assert guard.active_count() == 0
        guard.watch(TimeoutLevel.REQUEST, "a")
        guard.watch(TimeoutLevel.TURN, "b")
        assert guard.active_count() == 2
        guard.clear()
        assert guard.active_count() == 0

    def test_recent_events(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 600.0})
        guard.watch(TimeoutLevel.REQUEST, "x")
        guard.unwatch(TimeoutLevel.REQUEST, "x")
        events = guard.recent_events(5)
        assert len(events) >= 1
        guard.clear()

    def test_clear(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 600.0})
        guard.watch(TimeoutLevel.REQUEST, "y")
        guard.clear()
        assert guard.active_count() == 0
        assert len(guard.recent_events()) == 0


class TestSleepOrAbort:
    def test_sleep_completes(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 600.0})
        guard.watch(TimeoutLevel.REQUEST, "sleep1")
        result = TimeoutGuard.sleep_or_abort(0.05, guard, TimeoutLevel.REQUEST, "sleep1")
        assert result is True
        guard.clear()

    def test_sleep_aborts_on_timeout(self):
        guard = TimeoutGuard(custom_timeouts={TimeoutLevel.REQUEST: 0.02})
        guard.watch(TimeoutLevel.REQUEST, "sleep2")
        result = TimeoutGuard.sleep_or_abort(1.0, guard, TimeoutLevel.REQUEST, "sleep2")
        assert result is False
        guard.clear()
