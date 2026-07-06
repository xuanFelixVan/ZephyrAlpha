# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | CT-TELE-FLE-001
# [MODULE] zephyr.infrastructure.system_telemetry.metrics_bridge
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.metrics_collector; zephyr.trading.health_monitor
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] source_system 必须在枚举中; value 必须是 float; tag 值只允许 str/int/float/bool/None
# [MODIFY-GUARD] CT-TELE-FLE-001 协议变更必须同步更新 FLE metrics_collector.collect_from_telemetry
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TelemetryWriteError 磁盘满/DB 锁超时; ValueError 参数非法
# [TESTS] scripts/connect/tele_fle.py --trigger
# [A_module] module_id=MOD-INF_metrics_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""TELE→FLE 指标桥接 — emit_metrics() 生产者

CT-TELE-FLE-001: SystemTelemetry → FeedbackLoop 数据管道。
Telemetry 暴露 metrics 聚合 API，FLE collector 定期拉取并缓存。
"""

from __future__ import annotations

import json
import logging
import queue
import threading
from enum import Enum, unique
from typing import Any

from zephyr.shared.protocols.registry import ServiceRegistry

logger = logging.getLogger(__name__)

__all__ = [
    "MetricPoint",
    "MetricsBridge",
    "SourceSystem",
    "TelemetryWriteError",
    "emit_metrics",
    "get_metrics_queue",
]


@unique
class SourceSystem(str, Enum):
    ORCHESTRATOR = "orchestrator"
    GATE_ENGINE = "gate_engine"
    PIPELINE = "pipeline"
    SCRIPT_SYSTEM = "script_system"
    CONTEXT_ENGINE = "context-engine"
    KNOWLEDGE_BASE = "knowledge_base"
    VECTOR_MEMORY = "vector-memory"
    MCP = "mcp"
    LLM_SECURITY = "llm-security"
    TELEMETRY = "telemetry"
    FEEDBACK_LOOP = "feedback-loop"


class MetricPoint:
    """TELE→FLE 协议数据单元"""

    __slots__ = (
        "metric_name",
        "source_system",
        "tags",
        "timestamp",
        "ttl_seconds",
        "unit",
        "value",
    )

    def __init__(
        self,
        timestamp: str,
        source_system: str | SourceSystem,
        metric_name: str,
        value: float,
        unit: str = "count",
        tags: dict[str, Any] | None = None,
        ttl_seconds: int = 86400,
    ) -> None:
        if isinstance(source_system, SourceSystem):
            source_system = source_system.value
        if source_system not in {s.value for s in SourceSystem}:
            raise ValueError(f"非法的 source_system: {source_system}")

        self.timestamp = timestamp
        self.source_system = source_system
        self.metric_name = metric_name
        self.value = float(value)
        self.unit = unit
        self.tags = tags or {}
        self.ttl_seconds = ttl_seconds

    def to_db_row(self) -> tuple:
        return (
            self.timestamp,
            self.source_system,
            self.metric_name,
            self.value,
            self.unit,
            json.dumps(self.tags),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "source_system": self.source_system,
            "metric_name": self.metric_name,
            "value": self.value,
            "unit": self.unit,
            "tags": self.tags,
            "ttl_seconds": self.ttl_seconds,
        }


class TelemetryWriteError(Exception):
    """指标写入失败"""

    pass


_metrics_queue: queue.Queue[MetricPoint] = queue.Queue(maxsize=10000)


def get_metrics_queue() -> queue.Queue[MetricPoint]:
    return _metrics_queue


DEFAULT_AGGREGATION_DAY_MINUTES = 15
DEFAULT_AGGREGATION_NIGHT_MINUTES = 60


def _create_telemetry_metrics_table() -> None:
    conn = ServiceRegistry.get("db_connection")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS telemetry_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_system TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT DEFAULT 'count',
            tags_json TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_telemetry_ts
            ON telemetry_metrics(timestamp);
        CREATE INDEX IF NOT EXISTS idx_telemetry_source
            ON telemetry_metrics(source_system, metric_name);
        """
    )
    conn.commit()
    conn.close()


class MetricsBridge:
    """指标桥接 — 批量写入 telemetry_metrics + 广播到内存队列"""

    _instance: MetricsBridge | None = None
    _instance_lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        _create_telemetry_metrics_table()

    @classmethod
    def instance(cls) -> MetricsBridge:
        # 5.16.2 修复：double-checked locking 防止并发创建多实例导致指标分叉
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def emit_metrics(self, metrics: list[MetricPoint]) -> int:
        if not metrics:
            return 0

        _validate_batch(metrics)

        conn = ServiceRegistry.get("db_connection")
        try:
            rows = [m.to_db_row() for m in metrics]
            conn.executemany(
                "INSERT INTO telemetry_metrics "
                "(timestamp, source_system, metric_name, value, unit, tags_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                rows,
            )
            conn.commit()

            for m in metrics:
                try:
                    _metrics_queue.put_nowait(m)
                except queue.Full:
                    logger.warning("[TELE-FLE] metrics queue full, dropped broadcast for %s", m.metric_name)

            logger.debug("[TELE-FLE] emit_metrics: %d written", len(metrics))
            return len(metrics)
        except Exception as exc:
            conn.rollback()
            raise TelemetryWriteError("emit_metrics 失败") from exc
        finally:
            conn.close()


def _validate_batch(metrics: list[MetricPoint]) -> None:
    for i, m in enumerate(metrics):
        if not isinstance(m.value, (int, float)):
            raise ValueError(f"metrics[{i}].value 必须是数字, 实际: {type(m.value)}")
        if m.source_system not in {s.value for s in SourceSystem}:
            raise ValueError(f"metrics[{i}].source_system 非法: {m.source_system}")


def emit_metrics(metrics: list[MetricPoint]) -> int:
    """便捷函数 — 等价于 MetricsBridge.instance().emit_metrics(metrics)"""
    return MetricsBridge.instance().emit_metrics(metrics)
