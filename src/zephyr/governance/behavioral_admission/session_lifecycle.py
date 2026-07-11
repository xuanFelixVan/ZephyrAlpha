# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §17
# [MODULE] zephyr.governance.behavioral_admission.session_lifecycle
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.behavioral_admission.verdict_engine;MOD-INF-027(audit-orchestrator)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] SESSION_TRANSITIONS定义的状态转换是唯一合法路径；max_active_sessions硬限制不可绕过
# [MODIFY-GUARD] docs/docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md;src/zephyr/behavioral-admission/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] transition: InvalidTransition->SessionError; session_not_found->SessionError; register_session: CapacityExceeded->RuntimeError
# [TESTS] tests/test_behavioral_audit/test_session_lifecycle.py
# [A_module] module_id=MOD-GOV_session_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import json
import logging
import os
import sqlite3
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from zephyr.shared.io.paths import REPO_ROOT  # 5.141.2 修复: 使用SSoT路径, 避免相对路径漂移
from zephyr.shared.io.sqlite_factory import get_db_connection  # 5.133.7 工厂化: 使用SSoT连接工厂
from zephyr.shared.foundation.errors import SessionError  # 5.99.8/9 修复: 统一会话异常类型

logger = logging.getLogger(__name__)

IDLE_TIMEOUT_S: Final[int] = 1800
CLOSED_EXPIRY_S: Final[int] = 7776000
GC_INTERVAL_S: Final[int] = 300

# 5.141.2 修复: 使用 REPO_ROOT SSoT 构建绝对路径, 避免相对路径漂移
_DEFAULT_DB_DIR = REPO_ROOT / "data" / "behavioral-admission"
_DEFAULT_DB_NAME = "behavioral_audit_session.db"


class SessionState(str, Enum):
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"
    RESPONDING = "RESPONDING"
    DEGRADED = "DEGRADED"


class SessionTransition(str, Enum):
    ACTIVATE = "ACTIVATE"
    IDLE = "IDLE"
    RESUME = "RESUME"
    CLOSE = "CLOSE"
    EXPIRE = "EXPIRE"
    DEGRADE = "DEGRADE"
    RECOVER = "RECOVER"
    RESPOND = "RESPOND"
    COMPLETE = "COMPLETE"


SESSION_TRANSITIONS: Final[dict[SessionState, dict[SessionTransition, SessionState]]] = {
    SessionState.ACTIVE: {
        SessionTransition.IDLE: SessionState.IDLE,
        SessionTransition.CLOSE: SessionState.CLOSED,
        SessionTransition.DEGRADE: SessionState.DEGRADED,
        SessionTransition.RESPOND: SessionState.RESPONDING,
    },
    SessionState.IDLE: {
        SessionTransition.RESUME: SessionState.ACTIVE,
        SessionTransition.EXPIRE: SessionState.EXPIRED,
        SessionTransition.CLOSE: SessionState.CLOSED,
    },
    SessionState.RESPONDING: {
        SessionTransition.COMPLETE: SessionState.ACTIVE,
        SessionTransition.CLOSE: SessionState.CLOSED,
        SessionTransition.DEGRADE: SessionState.DEGRADED,
    },
    SessionState.DEGRADED: {
        SessionTransition.RECOVER: SessionState.ACTIVE,
        SessionTransition.CLOSE: SessionState.CLOSED,
        SessionTransition.EXPIRE: SessionState.EXPIRED,
    },
    SessionState.CLOSED: {
        SessionTransition.EXPIRE: SessionState.EXPIRED,
    },
    SessionState.EXPIRED: {},
}


class SessionTrustTier(str, Enum):
    PLATINUM = "PLATINUM"
    GOLD = "GOLD"
    SILVER = "SILVER"
    BRONZE = "BRONZE"
    REVOKED = "REVOKED"


class SessionStateRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = ""
    state: SessionState = SessionState.ACTIVE
    trust_score: float = 50.0
    violation_count: int = 0
    trust_tier: SessionTrustTier = SessionTrustTier.SILVER
    created_at: float = Field(default_factory=time.time)
    last_activity_at: float = Field(default_factory=time.time)
    last_transition_at: float = Field(default_factory=time.time)
    transition_history: list[dict[str, Any]] = Field(default_factory=list)


class GCStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_gc_runs: int = 0
    expired_sessions: int = 0
    idle_to_expired: int = 0
    closed_to_expired: int = 0
    last_gc_time: float = 0.0
    last_gc_duration_ms: float = 0.0


_TRUST_TIER_THRESHOLDS: list[tuple[float, SessionTrustTier]] = [
    (90.0, SessionTrustTier.PLATINUM),
    (70.0, SessionTrustTier.GOLD),
    (40.0, SessionTrustTier.SILVER),
    (10.0, SessionTrustTier.BRONZE),
    (0.0, SessionTrustTier.REVOKED),
]


def _compute_trust_tier(score: float) -> SessionTrustTier:
    for threshold, tier in _TRUST_TIER_THRESHOLDS:
        if score >= threshold:
            return tier
    return SessionTrustTier.REVOKED


_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS session_state (
    session_id TEXT PRIMARY KEY,
    state TEXT NOT NULL,
    trust_score REAL NOT NULL,
    violation_count INTEGER NOT NULL,
    trust_tier TEXT NOT NULL,
    created_at REAL NOT NULL,
    last_activity_at REAL NOT NULL,
    last_transition_at REAL NOT NULL,
    transition_history TEXT NOT NULL DEFAULT '[]'
)
"""

_UPSERT_SQL = """
INSERT INTO session_state (session_id, state, trust_score, violation_count, trust_tier,
    created_at, last_activity_at, last_transition_at, transition_history)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(session_id) DO UPDATE SET
    state=excluded.state,
    trust_score=excluded.trust_score,
    violation_count=excluded.violation_count,
    trust_tier=excluded.trust_tier,
    last_activity_at=excluded.last_activity_at,
    last_transition_at=excluded.last_transition_at,
    transition_history=excluded.transition_history
"""

_SELECT_SQL = """
SELECT session_id, state, trust_score, violation_count, trust_tier,
    created_at, last_activity_at, last_transition_at, transition_history
FROM session_state WHERE session_id = ?
"""

_SELECT_ACTIVE_SQL = """
SELECT session_id, state, trust_score, violation_count, trust_tier,
    created_at, last_activity_at, last_transition_at, transition_history
FROM session_state WHERE state IN ('ACTIVE', 'IDLE', 'RESPONDING', 'DEGRADED')
"""

_DELETE_SQL = "DELETE FROM session_state WHERE session_id = ?"


class SessionLifecycle:
    def __init__(
        self,
        db_path: str | None = None,
        idle_timeout_s: int = IDLE_TIMEOUT_S,
        closed_expiry_s: int = CLOSED_EXPIRY_S,
        gc_interval_s: int = GC_INTERVAL_S,
        max_active_sessions: int = 100,
    ) -> None:
        self._idle_timeout_s = idle_timeout_s
        self._closed_expiry_s = closed_expiry_s
        self._gc_interval_s = gc_interval_s
        self._max_active_sessions = max_active_sessions
        self._lock = threading.Lock()
        self._sessions: dict[str, SessionStateRecord] = {}

        if db_path is None:
            db_dir = _DEFAULT_DB_DIR
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / _DEFAULT_DB_NAME)
        self._db_path = db_path
        self._init_db()

        self._gc_stats = GCStats()
        self._total_gc_runs: int = 0
        self._expired_sessions: int = 0
        self._idle_to_expired: int = 0
        self._closed_to_expired: int = 0
        self._last_gc_time: float = 0.0
        self._last_gc_duration_ms: float = 0.0

    def register_session(self, session_id: str) -> SessionStateRecord:
        with self._lock:
            if session_id in self._sessions:
                return self._sessions[session_id]

            active_count = sum(
                1
                for s in self._sessions.values()
                if s.state in (SessionState.ACTIVE, SessionState.RESPONDING, SessionState.DEGRADED)
            )
            if active_count >= self._max_active_sessions:
                raise RuntimeError(f"max_active_sessions({self._max_active_sessions}) reached")

            now = time.time()
            record = SessionStateRecord(
                session_id=session_id,
                state=SessionState.ACTIVE,
                trust_score=50.0,
                violation_count=0,
                trust_tier=SessionTrustTier.SILVER,
                created_at=now,
                last_activity_at=now,
                last_transition_at=now,
                transition_history=[
                    {
                        "from": "NONE",
                        "to": SessionState.ACTIVE.value,
                        "trigger": SessionTransition.ACTIVATE.value,
                        "timestamp": now,
                    }
                ],
            )
            self._sessions[session_id] = record
            self._persist_record(record)
            return record

    def transition(self, session_id: str, trigger: SessionTransition) -> SessionState:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                raise SessionError("session not found", details={"session_id": session_id})

            current = record.state
            allowed = SESSION_TRANSITIONS.get(current, {})
            if trigger not in allowed:
                raise SessionError(f"invalid transition: {current.value} -> {trigger.value} not allowed")

            new_state = allowed[trigger]
            now = time.time()
            history_entry = {
                "from": current.value,
                "to": new_state.value,
                "trigger": trigger.value,
                "timestamp": now,
            }

            updated = SessionStateRecord(
                session_id=record.session_id,
                state=new_state,
                trust_score=record.trust_score,
                violation_count=record.violation_count,
                trust_tier=record.trust_tier,
                created_at=record.created_at,
                last_activity_at=now,
                last_transition_at=now,
                transition_history=record.transition_history + [history_entry],
            )
            self._sessions[session_id] = updated
            self._persist_record(updated)
            return new_state

    def get_state(self, session_id: str) -> SessionStateRecord | None:
        with self._lock:
            return self._sessions.get(session_id)

    def get_trust_tier(self, session_id: str) -> SessionTrustTier:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                return SessionTrustTier.REVOKED
            return record.trust_tier

    def update_trust_score(self, session_id: str, delta: float, reason: str = "") -> float:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                raise SessionError("session not found", details={"session_id": session_id})

            new_score = max(0.0, min(100.0, record.trust_score + delta))
            new_tier = _compute_trust_tier(new_score)

            updated = SessionStateRecord(
                session_id=record.session_id,
                state=record.state,
                trust_score=new_score,
                violation_count=record.violation_count,
                trust_tier=new_tier,
                created_at=record.created_at,
                last_activity_at=time.time(),
                last_transition_at=record.last_transition_at,
                transition_history=record.transition_history,
            )
            self._sessions[session_id] = updated
            self._persist_record(updated)
            return new_score

    def increment_violation(self, session_id: str) -> int:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                raise SessionError("session not found", details={"session_id": session_id})

            new_count = record.violation_count + 1
            penalty = min(5.0, new_count * 1.0)
            new_score = max(0.0, record.trust_score - penalty)
            new_tier = _compute_trust_tier(new_score)

            updated = SessionStateRecord(
                session_id=record.session_id,
                state=record.state,
                trust_score=new_score,
                violation_count=new_count,
                trust_tier=new_tier,
                created_at=record.created_at,
                last_activity_at=time.time(),
                last_transition_at=record.last_transition_at,
                transition_history=record.transition_history,
            )
            self._sessions[session_id] = updated
            self._persist_record(updated)
            return new_count

    def close_session(self, session_id: str) -> bool:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is None:
                return False
            if record.state is SessionState.CLOSED:
                return True

            try:
                now = time.time()
                new_state = SessionState.CLOSED
                history_entry = {
                    "from": record.state.value,
                    "to": new_state.value,
                    "trigger": SessionTransition.CLOSE.value,
                    "timestamp": now,
                }
                updated = SessionStateRecord(
                    session_id=record.session_id,
                    state=new_state,
                    trust_score=record.trust_score,
                    violation_count=record.violation_count,
                    trust_tier=record.trust_tier,
                    created_at=record.created_at,
                    last_activity_at=now,
                    last_transition_at=now,
                    transition_history=record.transition_history + [history_entry],
                )
                self._sessions[session_id] = updated
                self._persist_record(updated)
                return True
            except ValueError as e:
                logger.warning("close_session: failed to close session %s (%s: %s)", session_id, type(e).__name__, e)
                return False

    def run_gc(self) -> int:
        start = time.monotonic()
        expired_count = 0
        now = time.time()

        with self._lock:
            to_expire: list[str] = []
            for sid, record in self._sessions.items():
                if record.state is SessionState.IDLE:
                    idle_duration = now - record.last_activity_at
                    if idle_duration >= self._idle_timeout_s:
                        to_expire.append(sid)
                elif record.state is SessionState.CLOSED:
                    closed_duration = now - record.last_transition_at
                    if closed_duration >= self._closed_expiry_s:
                        to_expire.append(sid)

            for sid in to_expire:
                record = self._sessions[sid]
                old_state = record.state
                history_entry = {
                    "from": old_state.value,
                    "to": SessionState.EXPIRED.value,
                    "trigger": SessionTransition.EXPIRE.value,
                    "timestamp": now,
                }
                updated = SessionStateRecord(
                    session_id=record.session_id,
                    state=SessionState.EXPIRED,
                    trust_score=record.trust_score,
                    violation_count=record.violation_count,
                    trust_tier=record.trust_tier,
                    created_at=record.created_at,
                    last_activity_at=now,
                    last_transition_at=now,
                    transition_history=record.transition_history + [history_entry],
                )
                self._sessions[sid] = updated
                self._persist_record(updated)
                expired_count += 1
                if old_state is SessionState.IDLE:
                    self._idle_to_expired += 1
                elif old_state is SessionState.CLOSED:
                    self._closed_to_expired += 1

            self._expired_sessions += expired_count
            self._total_gc_runs += 1
            self._last_gc_time = now
            self._last_gc_duration_ms = (time.monotonic() - start) * 1000.0

        return expired_count

    def get_active_sessions(self) -> list[SessionStateRecord]:
        with self._lock:
            return [
                r
                for r in self._sessions.values()
                if r.state in (SessionState.ACTIVE, SessionState.IDLE, SessionState.RESPONDING, SessionState.DEGRADED)
            ]

    def get_gc_stats(self) -> GCStats:
        with self._lock:
            return self._build_gc_stats()

    def _build_gc_stats(self) -> GCStats:
        return GCStats(
            total_gc_runs=self._total_gc_runs,
            expired_sessions=self._expired_sessions,
            idle_to_expired=self._idle_to_expired,
            closed_to_expired=self._closed_to_expired,
            last_gc_time=self._last_gc_time,
            last_gc_duration_ms=round(self._last_gc_duration_ms, 2),
        )

    def restore_from_db(self, session_id: str) -> SessionStateRecord | None:
        with self._lock:
            if session_id in self._sessions:
                return self._sessions[session_id]

            record = self._load_from_db(session_id)
            if record is not None:
                self._sessions[session_id] = record
            return record

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            active = sum(
                1 for s in self._sessions.values() if s.state in (SessionState.ACTIVE, SessionState.RESPONDING)
            )
            idle = sum(1 for s in self._sessions.values() if s.state is SessionState.IDLE)
            total = len(self._sessions)
            return {
                "status": "healthy" if active < self._max_active_sessions else "at_capacity",
                "total_sessions": total,
                "active_sessions": active,
                "idle_sessions": idle,
                "max_active_sessions": self._max_active_sessions,
                "gc_stats": self._build_gc_stats().model_dump(),
                "db_path": self._db_path,
            }

    def _init_db(self) -> None:
        db_dir = os.path.dirname(self._db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self._db_conn = get_db_connection(self._db_path, check_same_thread=False, timeout=10.0)
        self._db_conn.execute("PRAGMA journal_mode=WAL")
        self._db_conn.execute("PRAGMA busy_timeout=5000")
        self._db_conn.execute(_CREATE_TABLE_SQL)
        self._db_conn.commit()

    def _persist_record(self, record: SessionStateRecord) -> None:
        try:
            self._db_conn.execute(
                _UPSERT_SQL,
                (
                    record.session_id,
                    record.state.value,
                    record.trust_score,
                    record.violation_count,
                    record.trust_tier.value,
                    record.created_at,
                    record.last_activity_at,
                    record.last_transition_at,
                    json.dumps(record.transition_history),
                ),
            )
            self._db_conn.commit()
        except Exception as exc:
            logger.error("Failed to persist session %s: %s", record.session_id, exc, exc_info=True)

    def _load_from_db(self, session_id: str) -> SessionStateRecord | None:
        try:
            cursor = self._db_conn.execute(_SELECT_SQL, (session_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return SessionStateRecord(
                session_id=row[0],
                state=SessionState(row[1]),
                trust_score=row[2],
                violation_count=row[3],
                trust_tier=SessionTrustTier(row[4]),
                created_at=row[5],
                last_activity_at=row[6],
                last_transition_at=row[7],
                transition_history=json.loads(row[8]),
            )
        except Exception as exc:
            logger.error("Failed to load session %s: %s", session_id, exc, exc_info=True)
            return None