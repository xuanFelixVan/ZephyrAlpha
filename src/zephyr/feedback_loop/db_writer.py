# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | CT-FLE-DB-001
# [MODULE] zephyr.feedback_loop.db_writer
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema; zephyr.feedback_loop.__init__; zephyr.infrastructure.__init__
# [CONSUMERS] zephyr.feedback_loop.metrics_collector ; zephyr.feedback_loop.alert_dispatcher
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fle_metrics/fle_alerts/fle_dispatch_log三张表幂等写入; 每次批量返回写入行数; 异常只抛日志不抛异常
# [MODIFY-GUARD] CT-FLE-DB-001 DDL变更必须同步更新sqlite_schema.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DBConnectionError写入失败抛日志; 空输入返回0不报错
# [TESTS] scripts/connect/fle_db.py --verify
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



FLE 持久化写入器 — 写 metrics/alerts/dispatch_log 到 SQLite

CT-FLE-DB-001: Feedback Loop 采集的指标和告警 -> Database 持久化落地。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: batch 参数
#   fields: 参数 batch，类型注解 list[MetricPoint]
#   code: db_writer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: event 参数
#   fields: 参数 event，类型注解 AlertEvent
#   code: db_writer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: event_id 参数
#   fields: 参数 event_id，类型注解 str
#   code: db_writer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: target_system 参数
#   fields: 参数 target_system，类型注解 str
#   code: db_writer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FLEWriter
#   name_en: FLEWriter
#   intro: FLE 数据库写入器。
#   desc: FLE 数据库写入器。；公共方法（定义序）: write_metrics, write_alert, write_dispatch_log, update_alert_status；源码 L115-L251
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② write_metrics_batch
#   name_en: write_metrics_batch
#   intro: 便捷函数：批量写入指标。
#   desc: 便捷函数：批量写入指标。；源码 L254-L256
#   inputs: batch
#   outputs: int
# - id: A3
#   name_zh: ③ write_alert
#   name_en: write_alert
#   intro: 便捷函数：写入告警。
#   desc: 便捷函数：写入告警。；源码 L259-L261
#   inputs: event
#   outputs: str | None
# - id: A4
#   name_zh: ④ write_dispatch_log
#   name_en: write_dispatch_log
#   intro: 便捷函数：写入分派日志。
#   desc: 便捷函数：写入分派日志。；源码 L264-L272
#   inputs: event_id target_system result task_id error_message
#   outputs: int | None
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.feedback_loop.metrics_collector ; zephyr.feedback_loop.alert_dispatcher
# - id: O2
#   name_zh: str | None
#   name_en: str | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.feedback_loop.metrics_collector ; zephyr.feedback_loop.alert_dispatcher
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from zephyr.feedback_loop.alert_dispatcher import AlertEvent
from zephyr.governance.persistence.sqlite_schema import get_db_connection
from zephyr.infrastructure.system_telemetry.metrics_bridge import MetricPoint

logger = logging.getLogger(__name__)

__all__ = [
    "FLEWriter",
    "write_alert",
    "write_dispatch_log",
    "write_metrics_batch",
]


class FLEWriter:
    """FLE 数据库写入器。"""

    def __init__(self) -> None:
        pass

    def write_metrics(self, batch: list[MetricPoint]) -> int:
        """批量写入 fle_metrics。返回写入行数。"""
        if not batch:
            return 0

        rows = []
        for m in batch:
            tags_json = json.dumps(m.tags or {}, ensure_ascii=False)
            source = m.source_system.value if hasattr(m.source_system, "value") else str(m.source_system)
            rows.append(
                (
                    m.timestamp,
                    source,
                    m.metric_name,
                    m.value,
                    getattr(m, "unit", "count"),
                    tags_json,
                    getattr(m, "window_avg", None),
                    getattr(m, "window_p99", None),
                    getattr(m, "window_count", None),
                )
            )

        conn = get_db_connection()
        try:
            count = conn.executemany(
                """INSERT INTO fle_metrics
                   (timestamp, source_system, metric_name, value, unit, tags_json, window_avg, window_p99, window_count)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows,
            )
            conn.commit()
            written = len(rows)
            logger.debug("[FLE-DB] wrote %d metrics", written)
            return written
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("[FLE-DB] write_metrics failed: %s", exc, exc_info=True)
            conn.rollback()
            return 0
        finally:
            conn.close()

    def write_alert(self, event: AlertEvent) -> str | None:
        """写入告警事件。返回 event_id 成功，None 失败。"""
        severity = event.severity.value if hasattr(event.severity, "value") else str(event.severity)
        category = event.category.value if hasattr(event.category, "value") else str(event.category)

        conn = get_db_connection()
        try:
            conn.execute(
                """INSERT INTO fle_alerts
                   (event_id, severity, category, title, detail, detected_at, metric_name, current_value, threshold_value)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.event_id,
                    severity,
                    category,
                    event.title,
                    event.detail[:2000] if event.detail else None,
                    event.detected_at,
                    event.metric_ref.get("name") if event.metric_ref else None,
                    event.metric_ref.get("current_value") if event.metric_ref else None,
                    event.metric_ref.get("threshold_value") if event.metric_ref else None,
                ),
            )
            conn.commit()
            logger.debug("[FLE-DB] wrote alert %s %s", event.event_id, severity)
            return event.event_id
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("[FLE-DB] write_alert failed: %s", exc, exc_info=True)
            conn.rollback()
            return None
        finally:
            conn.close()

    def write_dispatch_log(
        self,
        event_id: str,
        target_system: str,
        result: str,
        task_id: str | None = None,
        error_message: str | None = None,
    ) -> int | None:
        """写入分派日志。返回 row id 成功，None 失败。"""
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                """INSERT INTO fle_dispatch_log
                   (event_id, target_system, result, task_id, error_message)
                   VALUES (?, ?, ?, ?, ?)""",
                (event_id, target_system, result, task_id, error_message),
            )
            conn.commit()
            last_id = cursor.lastrowid
            logger.debug("[FLE-DB] wrote dispatch_log %d for %s", last_id, event_id)
            return last_id
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("[FLE-DB] write_dispatch_log failed: %s", exc, exc_info=True)
            conn.rollback()
            return None
        finally:
            conn.close()

    def update_alert_status(self, event_id: str, status: str) -> bool:
        """更新告警状态 (DISPATCHED/RESOLVED/DISMISSED)。"""
        now = datetime.now(UTC).isoformat()
        conn = get_db_connection()
        try:
            if status == "DISPATCHED":
                conn.execute(
                    "UPDATE fle_alerts SET status = ?, dispatched_at = ? WHERE event_id = ?",
                    (status, now, event_id),
                )
            elif status == "RESOLVED":
                conn.execute(
                    "UPDATE fle_alerts SET status = ?, resolved_at = ? WHERE event_id = ?",
                    (status, now, event_id),
                )
            else:
                conn.execute(
                    "UPDATE fle_alerts SET status = ? WHERE event_id = ?",
                    (status, event_id),
                )
            conn.commit()
            return True
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("[FLE-DB] update_alert_status failed: %s", exc, exc_info=True)
            conn.rollback()
            return False
        finally:
            conn.close()


def write_metrics_batch(batch: list[MetricPoint]) -> int:
    """便捷函数：批量写入指标。"""
    return FLEWriter().write_metrics(batch)


def write_alert(event: AlertEvent) -> str | None:
    """便捷函数：写入告警。"""
    return FLEWriter().write_alert(event)


def write_dispatch_log(
    event_id: str,
    target_system: str,
    result: str,
    task_id: str | None = None,
    error_message: str | None = None,
) -> int | None:
    """便捷函数：写入分派日志。"""
    return FLEWriter().write_dispatch_log(event_id, target_system, result, task_id, error_message)
