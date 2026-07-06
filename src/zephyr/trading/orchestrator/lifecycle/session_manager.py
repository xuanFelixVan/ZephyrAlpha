# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.lifecycle.session_manager
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_session_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""SessionManager — AI Agent 会话生命周期管理（CT-003 契约兑现）

消费 config/session_state_machine.yaml 定义的 5 状态 + 7 转换 + 超时规则，
提供运行时会话状态机。对标 ITIL Service Transition + NASA-STD-8739.8。

Task: CT-003 | experimental | session-20260506-012
"""

from __future__ import annotations

from typing import Final
import logging
import time
from enum import Enum, unique
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from threading import RLock
from typing import Any

import yaml

__all__ = [
    "SessionManager",
    "SessionState",
    "SessionTransitionError",
    "load_state_machine_config",
]

_logger = logging.getLogger(__name__)

DEFAULT_STATE_MACHINE_PATH: Final[Path] = REPO_ROOT / "config" / "session_state_machine.yaml"


@unique
class SessionState(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class SessionTransitionError(RuntimeError):
    """非法状态转换。"""


def load_state_machine_config(path: Path | None = None) -> dict[str, Any]:
    """从 session_state_machine.yaml 加载状态机定义。"""
    resolved = path or DEFAULT_STATE_MACHINE_PATH
    if not resolved.exists():
        raise FileNotFoundError(f"session_state_machine.yaml not found: {resolved}")
    with resolved.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


class SessionManager:
    """AI Agent 会话生命周期管理器。

    从 config/session_state_machine.yaml 加载状态定义和转换规则，
    在运行时强制执行合法转换和超时规则。

    Usage::

        sm = SessionManager()
        sid = sm.create_session()
        sm.transition(sid, "active")
        sm.transition(sid, "completed")
        sm.archive_session(sid)
    """

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or DEFAULT_STATE_MACHINE_PATH
        self._lock = RLock()
        self._sessions: dict[str, dict[str, Any]] = {}
        self._transitions: list[dict[str, Any]] = []
        self._timeout_rules: list[dict[str, Any]] = []
        self._exception_handling: list[dict[str, Any]] = []
        self._load_config()

    def _load_config(self) -> None:
        try:
            config = load_state_machine_config(self._config_path)
        except FileNotFoundError:
            _logger.warning("session_state_machine.yaml not found, using defaults")
            return
        self._transitions = config.get("transitions", [])
        self._timeout_rules = config.get("timeout_rules", [])
        self._exception_handling = config.get("exception_handling", [])

    def create_session(self, session_id: str | None = None) -> str:
        import uuid

        sid = session_id or str(uuid.uuid4())[:8]
        with self._lock:
            if sid in self._sessions:
                raise ValueError(f"Session {sid} already exists")
            self._sessions[sid] = {
                "state": SessionState.IDLE,
                "created_at": time.time(),
                "last_transition_at": time.time(),
                "history": [{"from": None, "to": "idle", "at": time.time()}],
            }
        return sid

    def transition(self, session_id: str, target_state: str) -> SessionState:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise KeyError(f"Session {session_id} not found")
            current = session["state"]
            target = SessionState(target_state)
            allowed = any(t.get("from") == current.value and t.get("to") == target.value for t in self._transitions)
            if not allowed:
                raise SessionTransitionError(f"Transition {current.value} -> {target.value} not allowed")
            session["state"] = target
            session["last_transition_at"] = time.time()
            session["history"].append(
                {
                    "from": current.value,
                    "to": target.value,
                    "at": time.time(),
                }
            )
        _logger.info("Session %s: %s -> %s", session_id, current.value, target.value)
        return target

    def get_state(self, session_id: str) -> SessionState:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise KeyError(f"Session {session_id} not found")
            return session["state"]

    def check_timeouts(self) -> list[str]:
        now = time.time()
        timed_out = []
        with self._lock:
            for sid, session in self._sessions.items():
                if session["state"] == SessionState.ACTIVE:
                    elapsed_h = (now - session["last_transition_at"]) / 3600
                    for rule in self._timeout_rules:
                        if rule.get("state") == "active" and elapsed_h >= rule.get("max_duration", 4):
                            timed_out.append(sid)
                            break
        return timed_out

    def archive_session(self, session_id: str) -> None:
        self.transition(session_id, "archived")

    @property
    def active_sessions(self) -> list[str]:
        with self._lock:
            return [sid for sid, s in self._sessions.items() if s["state"] == SessionState.ACTIVE]
