# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.state.session_manager
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_session_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
SessionManager — AI 代理会话生命周期管理器

消费 config/session_state_machine.yaml 定义的状态机，提供运行时会话状态追踪。
此前 session_state_machine.yaml line 7 声明 "no runtime consumer yet"——本模块补全该缺口。

SSoT: config/session_state_machine.yaml
ADR: ADR-0032（Agent 路由 / Orchestration）
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

import yaml
from zephyr.shared.io.paths import REPO_ROOT

__all__ = ["Session", "SessionError", "SessionManager", "SessionState"]

_logger = logging.getLogger(__name__)

_UTC = UTC

_STATE_MACHINE_YAML = REPO_ROOT / "config" / "session_state_machine.yaml"

_TRANSITION_MAP: dict[str, set[str]] = {
    "idle": {"active", "completed"},
    "active": {"paused", "completed"},
    "paused": {"active", "completed"},
    "completed": {"archived"},
    "archived": set(),
}

_TIMEOUT_RULES: dict[str, tuple[int, str]] = {
    "active": (4, "transition_to_paused"),
    "paused": (72, "transition_to_completed"),
}

_INVARIANT_CHECKS: ClassVar[list[str]] = [
    "Session must have exactly one state at any time",
    "Transition from completed to active is forbidden (start new session instead)",
    "Transition from archived to any other state is forbidden",
    "Each session must have a unique session_id",
    "Session log must be written within 5 minutes of state change",
]


class SessionState(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Session:
    session_id: str = field(default_factory=lambda: f"session-{uuid.uuid4().hex[:12]}")
    state: SessionState = SessionState.IDLE
    task_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(_UTC).isoformat())
    state_changed_at: str = field(default_factory=lambda: datetime.now(_UTC).isoformat())
    paused_at: str | None = None
    completed_at: str | None = None
    archived_at: str | None = None
    state_log: list[dict[str, Any]] = field(default_factory=list)
    token_budget_remaining: int = 8000
    error_info: dict[str, Any] | None = None


class SessionError(RuntimeError):
    pass


class SessionManager:
    """会话状态管理器——运行时消费 session_state_machine.yaml。"""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if not _STATE_MACHINE_YAML.exists():
            _logger.warning("session_state_machine.yaml not found at %s", _STATE_MACHINE_YAML)
            return {}
        with open(_STATE_MACHINE_YAML, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    def create_session(self, task_id: str | None = None) -> Session:
        session = Session(task_id=task_id)
        session.state_log.append(
            {
                "from_state": None,
                "to_state": SessionState.IDLE.value,
                "timestamp": session.state_changed_at,
                "reason": "session_created",
            }
        )
        self._sessions[session.session_id] = session
        _logger.info("Session %s created (task=%s)", session.session_id, task_id)
        return session

    def get_session(self, session_id: str) -> Session:
        s = self._sessions.get(session_id)
        if s is None:
            raise SessionError(f"Session {session_id} not found")
        return s

    def enforce_timeout(self, session_id: str) -> None:
        session = self.get_session(session_id)
        if session.state.value not in _TIMEOUT_RULES:
            return

        max_hours, _ = _TIMEOUT_RULES[session.state.value]

        try:
            changed = datetime.fromisoformat(session.state_changed_at)
            if changed.tzinfo is None:
                changed = changed.replace(tzinfo=_UTC)
        except ValueError:
            return

        elapsed = (datetime.now(_UTC) - changed).total_seconds() / 3600
        if elapsed > max_hours:
            if session.state is SessionState.ACTIVE:
                self.transition(session_id, SessionState.PAUSED, reason="timeout_4h_active")
            elif session.state is SessionState.PAUSED:
                self.transition(session_id, SessionState.COMPLETED, reason="timeout_72h_paused")

    def transition(
        self,
        session_id: str,
        target: SessionState,
        *,
        reason: str = "manual",
        force: bool = False,
    ) -> session:  # type: ignore
        session = self.get_session(session_id)
        current = session.state

        self._validate_transition(current, target, force)

        session.state = target
        now = datetime.now(_UTC).isoformat()
        session.state_changed_at = now

        session.state_log.append(
            {
                "from_state": current.value,
                "to_state": target.value,
                "timestamp": now,
                "reason": reason,
            }
        )

        if target is SessionState.PAUSED:
            session.paused_at = now
        elif target is SessionState.COMPLETED:
            session.completed_at = now
        elif target is SessionState.ARCHIVED:
            session.archived_at = now

        _logger.info("Session %s: %s → %s (reason=%s)", session_id, current.value, target.value, reason)
        return session

    def handle_exception(self, session_id: str, exception_type: str) -> Session:
        session = self.get_session(session_id)
        session.error_info = {
            "type": exception_type,
            "timestamp": datetime.now(_UTC).isoformat(),
        }

        if exception_type == "unrecoverable_error":
            if session.state in {SessionState.IDLE, SessionState.ACTIVE, SessionState.PAUSED}:
                self.transition(session_id, SessionState.COMPLETED, reason="unrecoverable_error")
            session.error_info["resolution"] = "manual_intervention_required"
        elif exception_type in {"encoding_error", "dependency_not_found", "token_budget_exceeded"}:
            if session.state is SessionState.ACTIVE:
                self.transition(session_id, SessionState.PAUSED, reason=exception_type)
            session.error_info["recovery"] = "user_intervention_required"
        else:
            _logger.warning("Unknown exception type: %s", exception_type)

        return session

    def _validate_transition(
        self,
        current: SessionState,
        target: SessionState,
        force: bool,
    ) -> None:
        if force:
            return

        allowed = _TRANSITION_MAP.get(current.value, set())
        if target.value not in allowed:
            raise SessionError(
                f"Invalid transition: {current.value} → {target.value}. Allowed from {current.value}: {sorted(allowed)}"
            )

        if target is SessionState.ACTIVE and current is SessionState.COMPLETED:
            raise SessionError("Transition from completed to active is forbidden. Start a new session instead.")

    def validate_invariants(self, session_id: str) -> list[str]:
        violations: list[str] = []
        session = self.get_session(session_id)

        duplicate_ids = sum(1 for s in self._sessions.values() if s.session_id == session.session_id)
        if duplicate_ids > 1:
            violations.append("Each session must have a unique session_id")

        if session.state is SessionState.ARCHIVED:
            violations.append("Transition from archived to any other state is forbidden")

        if session.state_log:
            last_log = session.state_log[-1]
            try:
                log_time = datetime.fromisoformat(last_log["timestamp"])
                if log_time.tzinfo is None:
                    log_time = log_time.replace(tzinfo=_UTC)
                delta = datetime.now(_UTC) - log_time
                if delta > timedelta(minutes=5):
                    violations.append(
                        f"Session log was written {delta.total_seconds() / 60:.1f}m ago "
                        f"(> 5 min since last state change)"
                    )
            except (ValueError, KeyError):
                pass

        return violations

    def list_sessions(self, state: SessionState | None = None) -> list[Session]:
        sessions = list(self._sessions.values())
        if state:
            sessions = [s for s in sessions if s.state == state]
        return sessions

    def close_session(self, session_id: str) -> Session:
        session = self.get_session(session_id)
        if session.state not in {SessionState.COMPLETED, SessionState.ARCHIVED}:
            self.transition(session_id, SessionState.COMPLETED, reason="session_closed")
        return session

    def remove_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]
            _logger.info("Session %s removed from manager", session_id)
