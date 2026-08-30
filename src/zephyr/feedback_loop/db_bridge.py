# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | CT-FLE-DB-001
# [MODULE] zephyr.feedback_loop.db_bridge
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] zephyr.feedback_loop.metrics_collector
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fle_metrics表DDL与sqlite_schema.py规范DDL一致; INSERT列名匹配规范schema
# [MODIFY-GUARD] CT-FLE-DB-001 DDL变更必须同步更新sqlite_schema.py; 已知schema漂移bug: db_bridge.py曾有独立冲突DDL(metric_type/metric_value/recorded_at)导致db_writer.py INSERT失败
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DBConnectionError写入失败抛日志; 空输入返回0不报错
# [TESTS] python -m pytest tests/test_db_bridge.py tests/test_fl_db_bridge.py -q
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



FLE DB契约适配器 — 通过规范zephyr.governance.sqlite_schema连接写入fle_metrics

CT-FLE-DB-001: FLE采集的指标 -> Database持久化落地。
DDL与sqlite_schema.py的_DDL_FLE_METRICS保持一致（SSoT）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: metric_type 参数
#   fields: 参数 metric_type，类型注解 str
#   code: db_bridge.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: metric_name 参数
#   fields: 参数 metric_name，类型注解 str
#   code: db_bridge.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: metric_value 参数
#   fields: 参数 metric_value，类型注解 float
#   code: db_bridge.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: tags 参数
#   fields: 参数 tags，类型注解 list[str] | None
#   code: db_bridge.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① record_via_db_contract
#   name_en: record_via_db_contract
#   intro: record_via_db_contract(metric_type, metric_name, metric_val…
#   desc: 源码 L132-L163
#   inputs: metric_type metric_name metric_value tags session_id task_id cost_usd…
#   outputs: int
# - id: A2
#   name_zh: ② bulk_record_via_db_contract
#   name_en: bulk_record_via_db_contract
#   intro: bulk_record_via_db_contract(records, db_path) 源码 L166-L211
#   desc: 源码 L166-L211
#   inputs: records db_path
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.feedback_loop.metrics_collector
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from zephyr.governance.persistence.sqlite_schema import get_db_connection
from zephyr.shared.io.paths import DB_PATH

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


def _ensure_table(conn: object) -> None:
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
    db_path: str | Path | None = None,
) -> int:
    # 5.34.7 治本：默认 None -> SSoT DB_PATH（原字面量相对路径
    # "data/databases/governance.db" 依赖 cwd，语义脆弱）
    conn = get_db_connection(DB_PATH if db_path is None else Path(db_path))
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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _logger.warning("record_via_db_contract failed: %s", exc, exc_info=True)
        return -1
    finally:
        conn.close()


def bulk_record_via_db_contract(
    records: list[dict[str, Any]],
    db_path: str | Path | None = None,
) -> int:
    if not records:
        return 0
    # 5.34.7 治本：默认 None -> SSoT DB_PATH（同 record_via_db_contract）
    conn = get_db_connection(DB_PATH if db_path is None else Path(db_path))
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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _logger.warning("bulk_record_via_db_contract failed: %s", exc, exc_info=True)
        conn.rollback()
        return 0
    finally:
        conn.close()
