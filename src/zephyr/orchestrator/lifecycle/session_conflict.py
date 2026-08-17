# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.lifecycle.session_conflict
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Session 冲突预防契约（CT-SESSION-CONFLICT）——文件锁+并发session检测+冲突resolution。"""


class SessionConflictGuard:
    def __init__(self):
        self._active_sessions: dict[str, set[str]] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def active_sessions(self) -> dict[str, set[str]]:
        """只读：active_sessions（Stage 4 公共化）。"""
        return self._active_sessions

    @active_sessions.setter
    def active_sessions(self, value):
        """写入：active_sessions（Stage 4 公共化）。"""
        self._active_sessions = value

    def register_session(self, session_id: str, files: list[str]) -> bool:
        for f in files:
            for sid, locked in self._active_sessions.items():
                if sid != session_id and f in locked:
                    return False
        self._active_sessions[session_id] = set(files)
        return True

    def release_session(self, session_id: str) -> None:
        self._active_sessions.pop(session_id, None)
