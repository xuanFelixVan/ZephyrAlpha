# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.agent_cooldown
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_agent_cooldown | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AgentCooldown — Agent 冷却隔离器。

依据: 蓝图 MOD-INF-021 §7 Phase 2.2 + §6.2 B8 + AP6

回滚后 5min 禁止修改被回滚文件。
cooldown 记录: (agent_session, file_path, until_iso) → rollback_quarantine.db
cooldown 状态绑定到 Agent Identity session token。
"""

from __future__ import annotations

import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path


@dataclass
class CooldownEntry:
    agent_session: str
    file_path: str
    cooldown_until: str
    reason: str


@dataclass
class CooldownCheck:
    allowed: bool
    blocked_files: list[str]
    cooldown_remaining_seconds: dict[str, int]


class AgentCooldown:
    COOLDOWN_MINUTES: int = 5
    DB_NAME: str = ".zephyr/rollback_quarantine.db"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._db_path = self._project_root / self.DB_NAME
        self._init_db()

    def _init_db(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        # 5.144.6 修复: conn.close() 移入 finally, 防止 execute/commit 抛异常跳过 close
        conn = get_db_connection(str(self._db_path))
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cooldown (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_session TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    cooldown_until TEXT NOT NULL,
                    reason TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cooldown_session ON cooldown(agent_session)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cooldown_file ON cooldown(file_path)")
            conn.commit()
        finally:
            conn.close()

    def quarantine(
        self,
        agent_session: str,
        file_paths: list[str],
        reason: str = "post_rollback_cooldown",
    ) -> list[CooldownEntry]:
        now = datetime.now(UTC)
        cooldown_until = now + timedelta(minutes=self.COOLDOWN_MINUTES)

        entries: list[CooldownEntry] = []
        # 5.144.6 修复: conn.close() 移入 finally
        conn = get_db_connection(str(self._db_path))
        try:
            self._cleanup_expired(conn)

            for fp in file_paths:
                entry = CooldownEntry(
                    agent_session=agent_session,
                    file_path=fp,
                    cooldown_until=cooldown_until.isoformat(),
                    reason=reason,
                )
                conn.execute(
                    "INSERT INTO cooldown (agent_session, file_path, cooldown_until, reason, created_at) VALUES (?, ?, ?, ?, ?)",
                    (agent_session, fp, cooldown_until.isoformat(), reason, now.isoformat()),
                )
                entries.append(entry)

            conn.commit()
        finally:
            conn.close()
        return entries

    def check(self, agent_session: str, file_paths: list[str]) -> CooldownCheck:
        # 5.144.6 修复: conn.close() 移入 finally
        conn = get_db_connection(str(self._db_path))
        try:
            self._cleanup_expired(conn)

            now = datetime.now(UTC)

            blocked_files: list[str] = []
            remaining: dict[str, int] = {}

            for fp in file_paths:
                rows = conn.execute(
                    "SELECT cooldown_until FROM cooldown WHERE agent_session=? AND file_path=? AND cooldown_until > ?",
                    (agent_session, fp, now.isoformat()),
                ).fetchall()

                for row in rows:
                    try:
                        until = datetime.fromisoformat(row[0])
                        secs = int((until - now).total_seconds())
                        if secs > 0:
                            blocked_files.append(fp)
                            remaining[fp] = max(remaining.get(fp, 0), secs)
                    except (ValueError, TypeError):
                        pass
        finally:
            conn.close()
        return CooldownCheck(
            allowed=len(blocked_files) == 0,
            blocked_files=list(set(blocked_files)),
            cooldown_remaining_seconds=remaining,
        )

    def is_quarantined(self, agent_session: str, file_path: str) -> bool:
        result = self.check(agent_session, [file_path])
        return file_path in result.blocked_files

    def lift_quarantine(self, agent_session: str, file_paths: list[str] | None = None) -> int:
        # 5.144.6 修复: conn.close() 移入 finally
        conn = get_db_connection(str(self._db_path))
        try:
            if file_paths:
                placeholders = ",".join(["?"] * len(file_paths))
                cursor = conn.execute(
                    f"DELETE FROM cooldown WHERE agent_session=? AND file_path IN ({placeholders})",
                    [agent_session] + file_paths,
                )
            else:
                cursor = conn.execute(
                    "DELETE FROM cooldown WHERE agent_session=?",
                    (agent_session,),
                )

            count = cursor.rowcount
            conn.commit()
        finally:
            conn.close()
        return count

    def get_active_quarantines(self, agent_session: str) -> list[CooldownEntry]:
        # 5.144.6 修复: conn.close() 移入 finally
        conn = get_db_connection(str(self._db_path))
        try:
            self._cleanup_expired(conn)

            now = datetime.now(UTC).isoformat()
            rows = conn.execute(
                "SELECT agent_session, file_path, cooldown_until, reason FROM cooldown WHERE agent_session=? AND cooldown_until > ?",
                (agent_session, now),
            ).fetchall()

            entries = [
                CooldownEntry(
                    agent_session=r[0],
                    file_path=r[1],
                    cooldown_until=r[2],
                    reason=r[3],
                )
                for r in rows
            ]
        finally:
            conn.close()
        return entries

    def _cleanup_expired(self, conn: sqlite3.Connection) -> None:
        now = datetime.now(UTC).isoformat()
        conn.execute("DELETE FROM cooldown WHERE cooldown_until <= ?", (now,))
        conn.commit()
