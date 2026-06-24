# [A_test] module_id: SRC-TST-1588 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §test
# [MODULE] tests.test_session_lifecycle
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.access_control.session_lifecycle
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_session_lifecycle.py
from zephyr.security.access_control.session_lifecycle import (
    STATE_DEFS,
    SessionManager,
    SessionState,
    StateDef,
    get_state_def,
)


class TestSessionState:
    def test_enum_values(self):
        assert SessionState.RUNNING.value == "RUNNING"
        assert SessionState.IDLE.value == "IDLE"
        assert SessionState.INTERRUPTED.value == "INTERRUPTED"
        assert SessionState.TIMED_OUT.value == "TIMED_OUT"
        assert SessionState.CLOSED.value == "CLOSED"

    def test_enum_count(self):
        assert len(SessionState) == 5


class TestStateDef:
    def test_defaults(self):
        sd = StateDef(state=SessionState.RUNNING, label="run")
        assert sd.valid_transitions == []
        assert sd.ttl_seconds == 3600
        assert sd.checkpoint_on_enter is False


class TestStateDefs:
    def test_all_states_covered(self):
        for ss in SessionState:
            assert ss in STATE_DEFS

    def test_running_transitions(self):
        assert SessionState.IDLE in STATE_DEFS[SessionState.RUNNING].valid_transitions
        assert SessionState.CLOSED in STATE_DEFS[SessionState.RUNNING].valid_transitions

    def test_closed_no_transitions(self):
        assert STATE_DEFS[SessionState.CLOSED].valid_transitions == []

    def test_timed_out_only_closed(self):
        assert STATE_DEFS[SessionState.TIMED_OUT].valid_transitions == [SessionState.CLOSED]


class TestGetStateDef:
    def test_existing(self):
        sd = get_state_def(SessionState.RUNNING)
        assert sd is not None
        assert sd.label == "运行中"

    def test_nonexistent(self):
        assert get_state_def("NONEXISTENT") is None


class TestSessionManager:
    def test_instantiation(self):
        sm = SessionManager(session_id="s1")
        assert sm.state == SessionState.RUNNING
        assert sm.is_active is True

    def test_valid_transition(self):
        sm = SessionManager(session_id="s1")
        result = sm.transition(SessionState.IDLE)
        assert result is True
        assert sm.state == SessionState.IDLE
        assert sm.is_active is True

    def test_invalid_transition(self):
        sm = SessionManager(session_id="s1")
        sm.transition(SessionState.CLOSED)
        assert sm.state == SessionState.CLOSED
        result = sm.transition(SessionState.RUNNING)
        assert result is False
        assert sm.state == SessionState.CLOSED

    def test_closed_not_active(self):
        sm = SessionManager(session_id="s1")
        sm.transition(SessionState.IDLE)
        sm.transition(SessionState.TIMED_OUT)
        sm.transition(SessionState.CLOSED)
        assert sm.is_active is False

    def test_checkpoint_on_enter(self):
        sm = SessionManager(session_id="s1")
        checkpoint_called = []
        sm.transition(SessionState.IDLE, checkpoint_fn=lambda: checkpoint_called.append(1))
        assert len(checkpoint_called) == 1
        assert sm.last_checkpoint is not None

    def test_no_checkpoint_without_fn(self):
        sm = SessionManager(session_id="s1")
        sm.transition(SessionState.IDLE)
        assert sm.last_checkpoint is None

    def test_running_no_checkpoint(self):
        sm = SessionManager(session_id="s1")
        checkpoint_called = []
        sm.transition(SessionState.IDLE)
        sm.transition(SessionState.RUNNING, checkpoint_fn=lambda: checkpoint_called.append(1))
        assert len(checkpoint_called) == 0

    def test_full_lifecycle(self):
        sm = SessionManager(session_id="s1")
        sm.transition(SessionState.IDLE)
        sm.transition(SessionState.RUNNING)
        sm.transition(SessionState.INTERRUPTED)
        sm.transition(SessionState.RUNNING)
        sm.transition(SessionState.TIMED_OUT)
        sm.transition(SessionState.CLOSED)
        assert sm.state == SessionState.CLOSED
