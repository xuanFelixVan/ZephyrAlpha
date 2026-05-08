"""CT-FLE-DB-001: FLE -> zephyr.db formal contract path adapter.

Routes MetricsCollector writes through the canonical zephyr.db connection
instead of opening a separate raw sqlite3 connection.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from zephyr.db.sqlite_schema import get_db_connection

__all__ = ["record_via_db_contract", "bulk_record_via_db_contract"]

_logger = logging.getLogger(__name__)

FLE_METRICS_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS fle_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    tags TEXT DEFAULT '[]',
    recorded_at TEXT NOT NULL DEFAULT (datetime('now')),
    session_id TEXT DEFAULT '',
    task_id TEXT DEFAULT '',
    cost_usd REAL DEFAULT 0.0,
    token_count INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_fle_metrics_type ON fle_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_fle_metrics_at ON fle_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_fle_metrics_session ON fle_metrics(session_id);
"""


def _ensure_table(conn: Any) -> None:
    conn.executescript(FLE_METRICS_TABLE_DDL)


def record_via_db_contract(
    metric_type: str,
    metric_name: str,
    metric_value: float,
    tags: list[str] | None = None,
    *,
    session_id: str = "",
    task_id: str = "",
    cost_usd: float = 0.0,
    token_count: int = 0,
    db_path: str | Path = "data/zalpha_metadata.db",
) -> int:
    conn = get_db_connection(Path(db_path))
    try:
        _ensure_table(conn)
        import json
        tags_json = json.dumps(tags or [], ensure_ascii=False)
        cursor = conn.execute(
            "INSERT INTO fle_metrics (metric_type, metric_name, metric_value, "
            "tags, session_id, task_id, cost_usd, token_count) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (metric_type, metric_name, metric_value, tags_json,
             session_id, task_id, cost_usd, token_count),
        )
        conn.commit()
        return cursor.lastrowid or 0
    except Exception as exc:
        _logger.warning("record_via_db_contract failed: %s", exc)
        return -1
    finally:
        conn.close()


def bulk_record_via_db_contract(
    records: list[dict[str, Any]],
    db_path: str | Path = "data/zalpha_metadata.db",
) -> int:
    if not records:
        return 0
    conn = get_db_connection(Path(db_path))
    try:
        _ensure_table(conn)
        import json
        count = 0
        for rec in records:
            tags_json = json.dumps(rec.get("tags", []), ensure_ascii=False)
            conn.execute(
                "INSERT INTO fle_metrics (metric_type, metric_name, metric_value, "
                "tags, session_id, task_id, cost_usd, token_count) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    rec.get("metric_type", "unknown"),
                    rec.get("metric_name", ""),
                    rec.get("metric_value", 0.0),
                    tags_json,
                    rec.get("session_id", ""),
                    rec.get("task_id", ""),
                    rec.get("cost_usd", 0.0),
                    rec.get("token_count", 0),
                ),
            )
            count += 1
        conn.commit()
        return count
    except Exception as exc:
        _logger.warning("bulk_record_via_db_contract failed: %s", exc)
        conn.rollback()
        return 0
    finally:
        conn.close()
