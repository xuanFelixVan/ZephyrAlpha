"""Session 冲突预防契约（CT-SESSION-CONFLICT）——文件锁+并发session检测+冲突resolution。"""

from __future__ import annotations

class SessionConflictGuard:
    def __init__(self):
        self._active_sessions: dict[str, set[str]] = {}

    def register_session(self, session_id: str, files: list[str]) -> bool:
        for f in files:
            for sid, locked in self._active_sessions.items():
                if sid != session_id and f in locked:
                    return False
        self._active_sessions[session_id] = set(files)
        return True

    def release_session(self, session_id: str) -> None:
        self._active_sessions.pop(session_id, None)
