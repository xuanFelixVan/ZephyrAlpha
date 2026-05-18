# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.self_monitor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
audit_trail.self_monitor — MOD-INF-020 · 自监控
==================================================
蓝图 §6 · 审计系统自身健康检查 + heartbeat

监控维度
--------
  - 写入吞吐量 (events/min)
  - 日志文件大小 (MB)
  - 完整性检查通过率
  - 最后写入时间 (防静默故障)
  - Heartbeat 自动写入
  - 与 External Verifier 交叉验证
  - 定时调度：后台线程自动 heartbeat + health check
"""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

DEFAULT_HEARTBEAT_INTERVAL_SEC: int = 300
DEFAULT_HEALTH_CHECK_INTERVAL_SEC: int = 600
_MAX_EVENTS_TO_SCAN: int = 5000
_MAX_FILE_SIZE_MB_FOR_CHECK: float = 512.0


class SelfMonitor:
    def __init__(
        self,
        data_dir: Path | str = Path("data/audit_trail"),
        heartbeat_interval: int = DEFAULT_HEARTBEAT_INTERVAL_SEC,
        health_check_interval: int = DEFAULT_HEALTH_CHECK_INTERVAL_SEC,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._event_log = self._data_dir / "events.jsonl"
        self._last_check_time = time.perf_counter()
        self._heartbeat_interval = heartbeat_interval
        self._health_check_interval = health_check_interval
        self._scheduler_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._last_health: dict[str, Any] = {}

    def check(self) -> dict[str, Any]:
        health: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_events": 0,
            "chain_status": "unknown",
            "anomalies": 0,
            "anomaly_summary": [],
            "db_status": "unknown",
            "recommendations": [],
            "file_size_mb": 0.0,
            "throughput_per_min": 0.0,
            "last_event_time": "",
            "healthy": True,
        }

        file_size = self._file_size_mb()
        health["file_size_mb"] = file_size
        health["healthy"] = file_size < 1024

        if file_size > _MAX_FILE_SIZE_MB_FOR_CHECK:
            health["chain_status"] = "skipped_file_too_large"
            health["recommendations"].append(
                f"Event log too large ({file_size:.1f}MB > {_MAX_FILE_SIZE_MB_FOR_CHECK}MB), skipping full check"
            )
            self._last_health = health
            return health

        try:
            verifier = IntegrityVerifier()
            integrity_report = verifier.verify_chain()
            health["total_events"] = integrity_report.get("events_checked", 0)
            health["chain_status"] = integrity_report.get("status", "unknown")

            if integrity_report.get("issues"):
                health["recommendations"].append(
                    f"Integrity issues: {len(integrity_report['issues'])} found"
                )
        except Exception as exc:
            health["chain_status"] = f"verifier_error: {exc}"

        try:
            query = AuditQuery()
            events = query._load_events()

            if events:
                from zephyr.audit_trail.anomaly import AnomalyDetector
                detector = AnomalyDetector()
                scan_events = events[-_MAX_EVENTS_TO_SCAN:] if len(events) > _MAX_EVENTS_TO_SCAN else events
                anomalies = detector.scan(scan_events)
                health["anomalies"] = len(anomalies)
                health["anomaly_summary"] = [
                    {"signature": a.signature_id, "severity": a.severity, "agent": a.agent_id}
                    for a in anomalies[:5]
                ]
                if anomalies:
                    health["recommendations"].append(
                        f"Anomalies detected: {len(anomalies)}"
                    )
        except Exception as exc:
            health["anomalies"] = -1

        try:
            from zephyr.audit_trail.indexer import AuditIndexer
            indexer = AuditIndexer()
            stats = indexer.query_stats()
            health["db_status"] = f"indexed={stats.get('total', 0)}"
        except Exception:
            health["db_status"] = "indexer_unavailable"

        if events := self._load_events_raw(limit=1):
            health["last_event_time"] = events[-1].get("timestamp", "")

        self._last_health = health
        return health

    def heartbeat(self) -> dict[str, Any]:
        now_ts = datetime.now(UTC).isoformat()
        return {
            "timestamp": now_ts,
            "total_events": self._event_count(),
            "file_size_mb": self._file_size_mb(),
            "healthy": self._file_size_mb() < 1024,
        }

    def write_heartbeat(self) -> dict[str, Any]:
        from zephyr.audit_trail.writer import AuditWriter

        writer = AuditWriter(self._data_dir)
        event = {
            "event_type": "heartbeat",
            "agent_id": "self_monitor",
            "session_id": "self_monitor",
            "operation": "heartbeat",
            "status": "ok",
        }
        chain_hash = writer.write(event)
        _logger.info("SelfMonitor: heartbeat written, chain_hash=%s", chain_hash[:16])
        return {"chain_hash": chain_hash, "event_count": writer.event_count}

    def start_scheduler(self, daemon: bool = True) -> None:
        """启动后台定时调度线程——自动 heartbeat + health check."""
        if self._scheduler_thread is not None and self._scheduler_thread.is_alive():
            _logger.warning("SelfMonitor: scheduler already running")
            return

        self._stop_event.clear()

        def _scheduler_loop() -> None:
            _logger.info(
                "SelfMonitor: scheduler started (heartbeat=%ds, health_check=%ds)",
                self._heartbeat_interval, self._health_check_interval,
            )
            last_heartbeat = time.monotonic()
            last_health_check = time.monotonic()

            while not self._stop_event.is_set():
                now = time.monotonic()

                if now - last_heartbeat >= self._heartbeat_interval:
                    try:
                        self.write_heartbeat()
                    except Exception as exc:
                        _logger.error("SelfMonitor: heartbeat failed: %s", exc)
                    last_heartbeat = now

                if now - last_health_check >= self._health_check_interval:
                    try:
                        health = self.check()
                        if not health.get("healthy", True):
                            _logger.warning(
                                "SelfMonitor: health check FAILED: %s",
                                health.get("recommendations", []),
                            )
                    except Exception as exc:
                        _logger.error("SelfMonitor: health check failed: %s", exc)
                    last_health_check = now

                self._stop_event.wait(timeout=min(self._heartbeat_interval, 30))

            _logger.info("SelfMonitor: scheduler stopped")

        self._scheduler_thread = threading.Thread(
            target=_scheduler_loop,
            name="audit-self-monitor",
            daemon=daemon,
        )
        self._scheduler_thread.start()
        from zephyr.shared.lifecycle.resource_optimization_engine import ResourceOptimizationEngine
        try:
            ResourceOptimizationEngine().register_daemon(
                "audit-self-monitor", self.start_scheduler, self.stop_scheduler, priority=5,
            )
        except Exception:
            pass

    def stop_scheduler(self) -> None:
        """停止后台定时调度线程."""
        self._stop_event.set()
        if self._scheduler_thread is not None:
            self._scheduler_thread.join(timeout=10)
            self._scheduler_thread = None

    @property
    def is_running(self) -> bool:
        return self._scheduler_thread is not None and self._scheduler_thread.is_alive()

    @property
    def last_health(self) -> dict[str, Any]:
        return dict(self._last_health)

    def _event_count(self) -> int:
        if not self._event_log.exists():
            return 0
        with open(self._event_log, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    def _file_size_mb(self) -> float:
        if not self._event_log.exists():
            return 0.0
        return round(self._event_log.stat().st_size / (1024 * 1024), 2)

    def _load_events_raw(self, limit: int | None = None) -> list[dict[str, Any]]:
        import json

        if not self._event_log.exists():
            return []
        if limit is not None:
            events: list[dict[str, Any]] = []
            with open(self._event_log, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except (json.JSONDecodeError, ValueError):
                            pass
                    if len(events) > limit * 2:
                        events = events[-limit:]
            return events[-limit:]
        events_full: list[dict[str, Any]] = []
        with open(self._event_log, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events_full.append(json.loads(line))
                    except (json.JSONDecodeError, ValueError):
                        pass
        return events_full
