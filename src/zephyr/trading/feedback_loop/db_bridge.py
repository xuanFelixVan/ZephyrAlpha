# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | CT-FLE-DB-001
# [MODULE] zephyr.trading.feedback_loop.db_bridge
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] zephyr.trading.feedback_loop.metrics_collector; tests.test_db_bridge; tests.test_fl_db_bridge
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] fle_metrics表DDL与sqlite_schema.py规范DDL一致; INSERT列名匹配规范schema
# [MODIFY-GUARD] CT-FLE-DB-001 DDL变更必须同步更新sqlite_schema.py; 已知schema漂移bug: db_bridge.py曾有独立冲突DDL(metric_type/metric_value/recorded_at)导致db_writer.py INSERT失败
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DBConnectionError写入失败抛日志; 空输入返回0不报错
# [TESTS] python -m pytest tests/test_db_bridge.py tests/test_fl_db_bridge.py -q
# [A_module] module_id=MOD-UNK_db_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FLE DB契约适配器 — 通过规范zephyr.governance.sqlite_schema连接写入fle_metrics

CT-FLE-DB-001: FLE采集的指标 -> Database持久化落地。
DDL与sqlite_schema.py的_DDL_FLE_METRICS保持一致（SSoT）。
"""

from __future__ import annotations

from typing import Final
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.governance.persistence.sqlite_schema import get_db_connection

__all__ = ["FLE_METRICS_TABLE_DDL", "bulk_record_via_db_contract", "record_via_db_contract"]

_logger = logging.getLogger(__name__)

# 规范DDL — 与 sqlite_schema.py _DDL_FLE_METRICS 完全一致（SSoT）
FLE_METRICS_TABLE_DDL: Final[str] = """
CREATE TABLE IF NOT EXISTS fle_metrics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL,
    source_system   TEXT    NOT NULL,
    metric_name     TEXT    NOT NULL,
    value           REAL    NOT NULL,
    unit            TEXT    DEFAULT 'count',
    tags_json       TEXT    DEFAULT '{}',
    window_avg      REAL,
    window_p99      REAL,
    window_count    INTEGER,
    collected_at    TEXT    DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_fle_metrics_ts ON fle_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_fle_metrics_collected ON fle_metrics(collected_at);
"""


def _ensure_table(conn: Any) -> None:
    conn.executescript(FLE_METRICS_TABLE_DDL)


def _build_tags_json(
    tags: list[str] | None,
    session_id: str,
    task_id: str,
    cost_usd: float,
    token_count: int,
) -> str:
    """将tags列表和额外字段打包为tags_json（规范schema的JSON text字段）。"""
    payload = {
        "tags": tags or [],
        "session_id": session_id,
        "task_id": task_id,
        "cost_usd": cost_usd,
        "token_count": token_count,
    }
    return json.dumps(payload, ensure_ascii=False)


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
    db_path: str | Path = "data/databases/governance.db",
) -> int:
    conn = get_db_connection(Path(db_path))
    try:
        _ensure_table(conn)
        timestamp = datetime.now(UTC).isoformat()
        tags_json = _build_tags_json(tags, session_id, task_id, cost_usd, token_count)
        cursor = conn.execute(
            "INSERT INTO fle_metrics (timestamp, source_system, metric_name, "
            "value, unit, tags_json) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, metric_type, metric_name, metric_value, "count", tags_json),
        )
        conn.commit()
        return cursor.lastrowid or 0
    except Exception as exc:
        _logger.warning("record_via_db_contract failed: %s", exc, exc_info=True)
        return -1
    finally:
        conn.close()


def bulk_record_via_db_contract(
    records: list[dict[str, Any]],
    db_path: str | Path = "data/databases/governance.db",
) -> int:
    if not records:
        return 0
    conn = get_db_connection(Path(db_path))
    try:
        _ensure_table(conn)
        # 5.44.3 修复：原 for rec in records: conn.execute(...) 为 N+1 往返，
        # 改为 executemany 批量插入，单次往返提交全部记录。
        timestamp = datetime.now(UTC).isoformat()
        batch: list[tuple] = []
        for rec in records:
            tags_json = _build_tags_json(
                rec.get("tags"),
                rec.get("session_id", ""),
                rec.get("task_id", ""),
                rec.get("cost_usd", 0.0),
                rec.get("token_count", 0),
            )
            batch.append(
                (
                    timestamp,
                    rec.get("metric_type", "unknown"),
                    rec.get("metric_name", ""),
                    rec.get("metric_value", 0.0),
                    "count",
                    tags_json,
                )
            )
        conn.executemany(
            "INSERT INTO fle_metrics (timestamp, source_system, metric_name, "
            "value, unit, tags_json) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            batch,
        )
        conn.commit()
        return len(batch)
    except Exception as exc:
        _logger.warning("bulk_record_via_db_contract failed: %s", exc, exc_info=True)
        conn.rollback()
        return 0
    finally:
        conn.close()
