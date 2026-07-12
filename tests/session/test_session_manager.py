# [A_test] module_id: SRC-TST-1589 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_session_manager
# [INVARIANTS] 5 states; 7 transitions; IDLE initial state; duplicate session_id rejected
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SessionError for unknown session; ValueError for duplicate session; SessionTransitionError for illegal transition
# [TESTS] test_session_manager.py
# [TTL] task_bound

from __future__ import annotations

import time

import pytest
import yaml

from zephyr.orchestrator.lifecycle.session_manager import (
    SessionError,
    SessionManager,
    SessionState,
    SessionTransitionError,
    load_state_machine_config,
)

_MINIMAL_CONFIG = {
    "transitions": [
        {"from": "idle", "to": "active"},
        {"from": "active", "to": "paused"},
        {"from": "paused", "to": "active"},
        {"from": "active", "to": "completed"},
        {"from": "completed", "to": "archived"},
        {"from": "paused", "to": "completed"},
        {"from": "idle", "to": "completed"},
    ],
    "timeout_rules": [
        {"state": "active", "max_duration": 4},
    ],
    "exception_handling": [],
}


@pytest.fixture()
def config_file(tmp_path):
    p = tmp_path / "session_state_machine.yaml"
    p.write_text(yaml.dump(_MINIMAL_CONFIG), encoding="utf-8")
    return p


@pytest.fixture()
def manager(config_file):
    return SessionManager(config_path=config_file)


class TestSessionState:
    def test_all_states(self):
        assert SessionState.IDLE.value == "idle"
        assert SessionState.ACTIVE.value == "active"
        assert SessionState.PAUSED.value == "paused"
        assert SessionState.COMPLETED.value == "completed"
        assert SessionState.ARCHIVED.value == "archived"

    def test_state_count(self):
        assert len(SessionState) == 5


class TestLoadStateMachineConfig:
    def test_load_valid_config(self, config_file):
        config = load_state_machine_config(config_file)
        assert "transitions" in config
        assert len(config["transitions"]) == 7

    def test_load_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_state_machine_config(tmp_path / "nonexistent.yaml")


class TestSessionManager:
    def test_create_session_auto_id(self, manager):
        sid = manager.create_session()
        assert isinstance(sid, str)
        assert len(sid) > 0

    def test_create_session_custom_id(self, manager):
        sid = manager.create_session(session_id="my-session")
        assert sid == "my-session"

    def test_create_session_duplicate_id(self, manager):
        manager.create_session(session_id="dup")
        with pytest.raises(ValueError, match="already exists"):
            manager.create_session(session_id="dup")

    def test_initial_state_is_idle(self, manager):
        sid = manager.create_session()
        assert manager.get_state(sid) == SessionState.IDLE

    def test_get_state_nonexistent_session(self, manager):
        with pytest.raises(SessionError, match="not found"):
            manager.get_state("nonexistent")

    def test_valid_transition_idle_to_active(self, manager):
        sid = manager.create_session()
        result = manager.transition(sid, "active")
        assert result == SessionState.ACTIVE
        assert manager.get_state(sid) == SessionState.ACTIVE

    def test_valid_transition_idle_to_completed(self, manager):
        sid = manager.create_session()
        result = manager.transition(sid, "completed")
        assert result == SessionState.COMPLETED

    def test_valid_transition_active_to_paused(self, manager):
        sid = manager.create_session()
        manager.transition(sid, "active")
        result = manager.transition(sid, "paused")
        assert result == SessionState.PAUSED

    def test_valid_transition_paused_to_active(self, manager):
        sid = manager.create_session()
        manager.transition(sid, "active")
        manager.transition(sid, "paused")
        result = manager.transition(sid, "active")
        assert result == SessionState.ACTIVE

    def test_valid_transition_completed_to_archived(self, manager):
        sid = manager.create_session()
        manager.transition(sid, "completed")
        result = manager.transition(sid, "archived")
        assert result == SessionState.ARCHIVED

    def test_invalid_transition_idle_to_archived(self, manager):
        sid = manager.create_session()
        with pytest.raises(SessionTransitionError, match="not allowed"):
            manager.transition(sid, "archived")

    def test_invalid_transition_active_to_idle(self, manager):
        sid = manager.create_session()
        manager.transition(sid, "active")
        with pytest.raises(SessionTransitionError, match="not allowed"):
            manager.transition(sid, "idle")

    def test_transition_nonexistent_session(self, manager):
        with pytest.raises(SessionError, match="not found"):
            manager.transition("nonexistent", "active")

    def test_archive_session(self, manager):
        sid = manager.create_session()
        manager.transition(sid, "completed")
        manager.archive_session(sid)
        assert manager.get_state(sid) == SessionState.ARCHIVED

    def test_active_sessions_property(self, manager):
        sid1 = manager.create_session()
        sid2 = manager.create_session()
        assert manager.active_sessions == []
        manager.transition(sid1, "active")
        assert sid1 in manager.active_sessions
        assert sid2 not in manager.active_sessions
        manager.transition(sid2, "active")
        assert len(manager.active_sessions) == 2

    def test_check_timeouts_no_timeout(self, manager):
        sid = manager.create_session()
        manager.transition(sid, "active")
        assert manager.check_timeouts() == []

    def test_check_timeouts_with_elapsed(self, manager):
        sid = manager.create_session()
        manager.transition(sid, "active")
        session = manager._sessions[sid]
        session["last_transition_at"] = time.time() - 5 * 3600
        timed_out = manager.check_timeouts()
        assert sid in timed_out

    def test_check_timeouts_idle_not_timed_out(self, manager):
        sid = manager.create_session()
        session = manager._sessions[sid]
        session["last_transition_at"] = time.time() - 10 * 3600
        assert manager.check_timeouts() == []

    def test_missing_config_uses_defaults(self, tmp_path):
        mgr = SessionManager(config_path=tmp_path / "nonexistent.yaml")
        sid = mgr.create_session()
        assert mgr.get_state(sid) == SessionState.IDLE
