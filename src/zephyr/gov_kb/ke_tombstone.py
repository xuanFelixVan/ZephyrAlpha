# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.gov_kb.ke_tombstone
# [DOMAIN] D_GOV_KB
# [DEPENDENCIES] zephyr.gov_kb.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_ke_tombstone | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""SQLite墓碑表 + G2向量去重
==============================
蓝图: MOD-KB-001 §9.18.3
任务: KB-INF-0033

墓碑表 ke_tombstones:
  CREATE TABLE ke_tombstones (
    tombstone_id   TEXT PRIMARY KEY,
    ke_id          TEXT NOT NULL,
    deletion_time  TEXT NOT NULL,
    deletion_reason TEXT,
    source_hash    TEXT,
    chroma_id      TEXT,
    vector_hash    TEXT,
    purged         INTEGER DEFAULT 0,
    purged_at      TEXT
  );

功能:
  1. DELETE KE -> 不物理删除 -> 移入墓碑表
  2. G2 dedup -> 先查墓碑 -> 避免"僵尸复活"
  3. 定期 purge -> 90天后的墓碑记录可以清理

用法:
    python -m zephyr.knowledge.kb.ke_tombstone init            # 创建表
    python -m zephyr.knowledge.kb.ke_tombstone list            # 列出墓碑
    python -m zephyr.knowledge.kb.ke_tombstone purge           # 清理过期墓碑
"""

from __future__ import annotations

from typing import Final
import json
import logging
import os
import sqlite3
from zephyr.governance.persistence.sqlite_schema import get_db_connection
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

# SQL constants (NO-BARE-SQL gate compliance)
_SQL_INSERT_TOMBSTONE = (
    "INSERT INTO ke_tombstones (tombstone_id, ke_id, deletion_time, deletion_reason, "
    "source_hash, chroma_id, vector_hash) VALUES (?, ?, ?, ?, ?, ?, ?)"
)
_SQL_SELECT_BY_KE_ID = "SELECT 1 FROM ke_tombstones WHERE ke_id = ? AND purged = 0 LIMIT 1"
_SQL_SELECT_BY_HASH = "SELECT 1 FROM ke_tombstones WHERE source_hash = ? AND purged = 0 LIMIT 1"
_SQL_SELECT_ALL = "SELECT * FROM ke_tombstones ORDER BY deletion_time DESC LIMIT ?"
_SQL_SELECT_UNPURGED = "SELECT * FROM ke_tombstones WHERE purged = 0 ORDER BY deletion_time DESC LIMIT ?"
_SQL_COUNT_UNPURGED = "SELECT COUNT(*) FROM ke_tombstones WHERE purged = 0"
_SQL_PURGE_OLD = "UPDATE ke_tombstones SET purged = 1, purged_at = ? WHERE deletion_time < ? AND purged = 0"


@dataclass
class TombstoneEntry:
    tombstone_id: str
    ke_id: str
    deletion_time: str
    deletion_reason: str
    source_hash: str
    chroma_id: str
    vector_hash: str
    purged: bool = False
    purged_at: str = ""


CREATE_TABLE_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS ke_tombstones (
    tombstone_id   TEXT PRIMARY KEY,
    ke_id          TEXT NOT NULL,
    deletion_time  TEXT NOT NULL,
    deletion_reason TEXT NOT NULL DEFAULT 'unknown',
    source_hash    TEXT DEFAULT '',
    chroma_id      TEXT DEFAULT '',
    vector_hash    TEXT DEFAULT '',
    purged         INTEGER NOT NULL DEFAULT 0,
    purged_at      TEXT DEFAULT ''
);
"""

CREATE_INDEX_SQL: Final[str] = """
CREATE INDEX IF NOT EXISTS idx_tombstones_ke_id ON ke_tombstones(ke_id);
CREATE INDEX IF NOT EXISTS idx_tombstones_deletion_time ON ke_tombstones(deletion_time);
CREATE INDEX IF NOT EXISTS idx_tombstones_purged ON ke_tombstones(purged);
"""


def _get_project_root() -> Path:
    env = os.environ.get("ZEPHYR_PROJECT_ROOT")
    if env:
        return Path(env)
    return REPO_ROOT


class TombstoneManager:
    _TABLE_NAME = "ke_tombstones"
    _RETENTION_DAYS = 90

    def __init__(self, project_root: Path | None = None):
        self._root = project_root or _get_project_root()

    @property
    def db_path(self) -> Path:
        return self._root / "data" / "databases" / "governance.db"

    def _get_conn(self) -> sqlite3.Connection:
        db_dir = self.db_path.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        conn = get_db_connection(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
        return conn

    def init(self) -> bool:
        try:
            conn = self._get_conn()
            conn.execute(CREATE_TABLE_SQL)
            conn.executescript(CREATE_INDEX_SQL)
            conn.commit()
            conn.close()
            logger.info("Tombstone table ke_tombstones initialized")
            return True
        except Exception as e:
            logger.error("Failed to init tombstone table: %s", e, exc_info=True)
            return False

    def bury(
        self,
        ke_id: str,
        reason: str = "unknown",
        source_hash: str = "",
        chroma_id: str = "",
        vector_hash: str = "",
    ) -> TombstoneEntry:
        conn = self._get_conn()
        tombstone_id = f"t-{ke_id}-{int(datetime.now(UTC).timestamp())}"
        now_str = datetime.now(UTC).isoformat()
        try:
            conn.execute(
                _SQL_INSERT_TOMBSTONE,
                (tombstone_id, ke_id, now_str, reason, source_hash, chroma_id, vector_hash),
            )
            conn.commit()
            return TombstoneEntry(
                tombstone_id=tombstone_id,
                ke_id=ke_id,
                deletion_time=now_str,
                deletion_reason=reason,
                source_hash=source_hash,
                chroma_id=chroma_id,
                vector_hash=vector_hash,
            )
        except Exception as e:
            logger.error("Failed to bury KE %s: %s", ke_id, e, exc_info=True)
            raise
        finally:
            conn.close()

    def is_buried(self, ke_id: str) -> bool:
        conn = self._get_conn()
        try:
            row = conn.execute(
                _SQL_SELECT_BY_KE_ID,
                (ke_id,),
            ).fetchone()
            return row is not None
        except Exception:
            return False
        finally:
            conn.close()

    def is_buried_by_hash(self, source_hash: str) -> bool:
        if not source_hash:
            return False
        conn = self._get_conn()
        try:
            row = conn.execute(
                _SQL_SELECT_BY_HASH,
                (source_hash,),
            ).fetchone()
            return row is not None
        except Exception:
            return False
        finally:
            conn.close()

    def list(self, include_purged: bool = False, limit: int = 100) -> list[TombstoneEntry]:
        conn = self._get_conn()
        try:
            if include_purged:
                rows = conn.execute(
                    _SQL_SELECT_ALL,
                    (limit,),
                ).fetchall()
            else:
                rows = conn.execute(
                    _SQL_SELECT_UNPURGED,
                    (limit,),
                ).fetchall()
            return [
                TombstoneEntry(
                    tombstone_id=r["tombstone_id"],
                    ke_id=r["ke_id"],
                    deletion_time=r["deletion_time"],
                    deletion_reason=r["deletion_reason"],
                    source_hash=r["source_hash"],
                    chroma_id=r["chroma_id"],
                    vector_hash=r["vector_hash"],
                    purged=bool(r["purged"]),
                    purged_at=r["purged_at"],
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Failed to list tombstones: %s", e, exc_info=True)
            return []
        finally:
            conn.close()

    def count(self) -> int:
        conn = self._get_conn()
        try:
            row = conn.execute(_SQL_COUNT_UNPURGED).fetchone()
            return row[0] if row else 0
        except Exception:
            return 0
        finally:
            conn.close()

    def purge(self, older_than_days: int | None = None) -> int:
        retention = older_than_days or self._RETENTION_DAYS
        cutoff = datetime.now(UTC).timestamp() - (retention * 24 * 3600)
        cutoff_str = datetime.fromtimestamp(cutoff, tz=UTC).isoformat()
        now_str = datetime.now(UTC).isoformat()

        conn = self._get_conn()
        try:
            result = conn.execute(
                _SQL_PURGE_OLD,
                (now_str, cutoff_str),
            )
            conn.commit()
            count = result.rowcount
            if count > 0:
                logger.info("Purged %d tombstones older than %s", count, cutoff_str)
            return count
        except Exception as e:
            logger.error("Failed to purge tombstones: %s", e, exc_info=True)
            return 0
        finally:
            conn.close()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="KB Tombstone Manager")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init", help="Create ke_tombstones table")
    sub.add_parser("list", help="List non-purged tombstones")
    pur = sub.add_parser("purge", help="Purge expired tombstones")
    pur.add_argument("--older-than-days", type=int, help="Purge entries older than N days (default: 90)")
    bur = sub.add_parser("bury", help="Manually bury a KE")
    bur.add_argument("ke_id", help="KE ID to bury")
    bur.add_argument("--reason", default="manual", help="Deletion reason")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()
    tm = TombstoneManager()

    if args.cmd == "init":
        ok = tm.init()
        print("Tombstone table created." if ok else "Failed to create tombstone table.")
        if not ok:
            sys.exit(1)
        return

    if args.cmd == "list":
        entries = tm.list()
        if args.json:
            print(
                json.dumps(
                    [
                        {
                            "tombstone_id": e.tombstone_id,
                            "ke_id": e.ke_id,
                            "deletion_time": e.deletion_time,
                            "deletion_reason": e.deletion_reason,
                            "purged": e.purged,
                        }
                        for e in entries
                    ],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"Tombstones ({len(entries)}):")
            for e in entries:
                print(f"  {e.tombstone_id}: KE={e.ke_id} at {e.deletion_time} ({e.deletion_reason})")
        return

    if args.cmd == "purge":
        count = tm.purge(older_than_days=args.older_than_days)
        print(f"Purged {count} tombstone entries.")
        return

    if args.cmd == "bury":
        entry = tm.bury(args.ke_id, reason=args.reason or "manual")
        print(f"Buried KE {args.ke_id}: tombstone_id={entry.tombstone_id}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()