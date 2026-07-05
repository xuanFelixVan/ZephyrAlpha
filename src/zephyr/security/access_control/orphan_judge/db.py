# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §5.1
# [MODULE] zephyr.security.access_control.orphan_judge.db
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema; zephyr.security.access_control.orphan_judge.models
# [CONSUMERS] orphan-judge.__main__._cmd_report; report_generator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 使用项目级SQLite连接(get_db_connection); 表judgment_records结构不可变
# [MODIFY-GUARD] 修改表结构必须同步blueprint.md §5.1; 修改DB_PATH必须同步sqlite_schema.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] IntegrityError on duplicate path
# [TESTS] tests/orphan-judge/test_db.py
# [A_module] module_id=MOD-SEC_db | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from datetime import datetime

from zephyr.governance.persistence.sqlite_schema import get_db_connection
from zephyr.security.access_control.orphan_judge.models import JudgmentRecord, ScanSummary

logger = logging.getLogger(__name__)

__all__ = ["JudgmentDB"]

_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS judgment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    verdict TEXT NOT NULL,
    confidence TEXT NOT NULL,
    reason TEXT DEFAULT '',
    layers_json TEXT DEFAULT '{}',
    scanned_at TEXT NOT NULL,
    file_hash TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_jr_verdict ON judgment_records(verdict);
CREATE INDEX IF NOT EXISTS idx_jr_scanned ON judgment_records(scanned_at);
"""


class JudgmentDB:
    def __init__(self) -> None:
        self._conn = get_db_connection()
        self._ensure_table()

    def _ensure_table(self) -> None:
        self._conn.executescript(_TABLE_DDL)

    def insert(self, record: JudgmentRecord) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO judgment_records (path, verdict, confidence, reason, layers_json, scanned_at, file_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                record.path,
                record.verdict,
                record.confidence,
                record.reason,
                record.layers_json,
                record.scanned_at.isoformat(),
                record.file_hash,
            ),
        )
        self._conn.commit()

    def get(self, path: str) -> JudgmentRecord | None:
        row = self._conn.execute(
            "SELECT path, verdict, confidence, reason, layers_json, scanned_at, file_hash "
            "FROM judgment_records WHERE path = ?",
            (path,),
        ).fetchone()
        if row is None:
            return None
        return JudgmentRecord(
            path=row[0],
            verdict=row[1],
            confidence=row[2],
            reason=row[3],
            layers_json=row[4],
            scanned_at=datetime.fromisoformat(row[5]),
            file_hash=row[6],
        )

    def list_by_verdict(self, verdict: str) -> list[JudgmentRecord]:
        rows = self._conn.execute(
            "SELECT path, verdict, confidence, reason, layers_json, scanned_at, file_hash "
            "FROM judgment_records WHERE verdict = ? ORDER BY scanned_at DESC",
            (verdict,),
        ).fetchall()
        return [
            JudgmentRecord(
                path=r[0],
                verdict=r[1],
                confidence=r[2],
                reason=r[3],
                layers_json=r[4],
                scanned_at=datetime.fromisoformat(r[5]),
                file_hash=r[6],
            )
            for r in rows
        ]

    def summary(self) -> ScanSummary:
        rows = self._conn.execute("SELECT verdict, COUNT(*) FROM judgment_records GROUP BY verdict").fetchall()
        s = ScanSummary(total=sum(r[1] for r in rows))
        for verdict, count in rows:
            if verdict == "KEEP":
                s.keep = count
            elif verdict == "DELETE":
                s.delete = count
            elif verdict == "DEPRECATE":
                s.deprecate = count
            elif verdict == "EXTRACT_AND_MERGE":
                s.extract_and_merge = count
            elif verdict == "ESCALATE":
                s.escalate = count
            elif verdict == "ERROR":
                s.error = count
        return s

    def delete(self, path: str) -> bool:
        cur = self._conn.execute("DELETE FROM judgment_records WHERE path = ?", (path,))
        self._conn.commit()
        return cur.rowcount > 0

    def clear(self) -> int:
        cur = self._conn.execute("DELETE FROM judgment_records")
        self._conn.commit()
        return cur.rowcount
