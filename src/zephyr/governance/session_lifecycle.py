from __future__ import annotations

import time
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Optional

from pydantic import BaseModel, Field

logger = __import__("logging").getLogger(__name__)


class SessionState(str, Enum):
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    INTERRUPTED = "INTERRUPTED"
    TIMED_OUT = "TIMED_OUT"
    CLOSED = "CLOSED"


class StateDef(BaseModel):
    state: SessionState
    label: str
    valid_transitions: list[SessionState] = Field(default_factory=list)
    ttl_seconds: int = 3600
    checkpoint_on_enter: bool = False


STATE_DEFS: dict[SessionState, StateDef] = {
    SessionState.RUNNING: StateDef(
        state=SessionState.RUNNING,
        label="运行中",
        valid_transitions=[SessionState.IDLE, SessionState.INTERRUPTED, SessionState.TIMED_OUT, SessionState.CLOSED],
        ttl_seconds=7200,
        checkpoint_on_enter=False,
    ),
    SessionState.IDLE: StateDef(
        state=SessionState.IDLE,
        label="空闲",
        valid_transitions=[SessionState.RUNNING, SessionState.TIMED_OUT, SessionState.CLOSED],
        ttl_seconds=1800,
        checkpoint_on_enter=True,
    ),
    SessionState.INTERRUPTED: StateDef(
        state=SessionState.INTERRUPTED,
        label="中断",
        valid_transitions=[SessionState.RUNNING, SessionState.CLOSED],
        ttl_seconds=600,
        checkpoint_on_enter=True,
    ),
    SessionState.TIMED_OUT: StateDef(
        state=SessionState.TIMED_OUT,
        label="超时",
        valid_transitions=[SessionState.CLOSED],
        ttl_seconds=0,
        checkpoint_on_enter=True,
    ),
    SessionState.CLOSED: StateDef(
        state=SessionState.CLOSED,
        label="已关闭",
        valid_transitions=[],
        ttl_seconds=0,
        checkpoint_on_enter=True,
    ),
}


class SessionManager(BaseModel):
    session_id: str
    state: SessionState = SessionState.RUNNING
    started_at: str = ""
    last_checkpoint: Optional[str] = None

    def transition(self, new_state: SessionState, checkpoint_fn: Optional[Callable[[], None]] = None) -> bool:
        sdef = STATE_DEFS.get(self.state)
        if sdef is None or new_state not in sdef.valid_transitions:
            logger.warning("Invalid transition: %s → %s", self.state.value, new_state.value)
            return False
        self.state = new_state
        new_sdef = STATE_DEFS.get(new_state)
        if new_sdef and new_sdef.checkpoint_on_enter and checkpoint_fn:
            checkpoint_fn()
            self.last_checkpoint = datetime.now(timezone.utc).isoformat()
        return True

    @property
    def is_active(self) -> bool:
        return self.state in (SessionState.RUNNING, SessionState.IDLE)


def get_state_def(state: SessionState) -> Optional[StateDef]:
    return STATE_DEFS.get(state)
