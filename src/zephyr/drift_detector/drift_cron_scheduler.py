"""Drift Cron Scheduler — 定期扫描调度器 v1.0.1

module_id: MOD-INF-023
实现蓝图 §2.6 定期触发策略：每30min STANDARD + 每6h DEEP。
集成 DaemonRegistry 统一管理。"""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timedelta, timezone

from zephyr.shared.lifecycle.daemon_registry import DaemonRegistry, DaemonState, registry

logger = logging.getLogger(__name__)

STANDARD_INTERVAL_S = 30 * 60
DEEP_INTERVAL_S = 6 * 60 * 60


class DriftCronScheduler:
    """轻量级定时扫描调度器，通过 DaemonRegistry 注册为后台 daemon。"""

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._last_standard: datetime | None = None
        self._last_deep: datetime | None = None
        self._lock = threading.Lock()

    def start(self):
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="drift-cron-scheduler")
        self._thread.start()
        try:
            registry.register(
                name="drift-cron-scheduler",
                state=DaemonState.RUNNING,
                metadata={"interval_standard_s": STANDARD_INTERVAL_S, "interval_deep_s": DEEP_INTERVAL_S},
            )
        except Exception:
            pass
        logger.info("[Drift][Cron] scheduler started: STANDARD=%ss DEEP=%ss", STANDARD_INTERVAL_S, DEEP_INTERVAL_S)

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None
        try:
            registry.deregister("drift-cron-scheduler")
        except Exception:
            pass
        logger.info("[Drift][Cron] scheduler stopped")

    def _run(self):
        while not self._stop_event.is_set():
            try:
                now = datetime.now(timezone.utc)
                should_standard = (
                    self._last_standard is None
                    or (now - self._last_standard).total_seconds() >= STANDARD_INTERVAL_S
                )
                should_deep = (
                    self._last_deep is None
                    or (now - self._last_deep).total_seconds() >= DEEP_INTERVAL_S
                )

                if should_standard:
                    self._run_scan("STANDARD")
                    with self._lock:
                        self._last_standard = now
                elif should_deep:
                    self._run_scan("DEEP")
                    with self._lock:
                        self._last_deep = now

                self._stop_event.wait(timeout=60)
            except Exception:
                logger.exception("[Drift][Cron] scheduler loop error")
                self._stop_event.wait(timeout=60)

    def _run_scan(self, level: str):
        try:
            import asyncio
            from zephyr.drift_detector.drift_engine import scan, ScanLevel
            scan_level = ScanLevel.DEEP if level == "DEEP" else ScanLevel.STANDARD
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop is not None:
                import concurrent.futures
                future = concurrent.futures.Future()
                def _run():
                    new_loop = asyncio.new_event_loop()
                    try:
                        result = new_loop.run_until_complete(scan(level=scan_level))
                        future.set_result(result)
                    except Exception as exc:
                        future.set_exception(exc)
                    finally:
                        new_loop.close()
                t = threading.Thread(target=_run, daemon=True)
                t.start()
                t.join(timeout=120)
                result = future.result()
            else:
                new_loop = asyncio.new_event_loop()
                try:
                    result = new_loop.run_until_complete(scan(level=scan_level))
                finally:
                    new_loop.close()
            logger.info(
                "[Drift][Cron] %s scan complete: %s detectors, %s events",
                level, result.detectors_run, result.total_drift_events,
            )
            try:
                registry.update("drift-cron-scheduler", metadata={
                    "last_scan": datetime.now(timezone.utc).isoformat(),
                    "last_scan_level": level,
                    "last_scan_events": result.total_drift_events,
                })
            except Exception:
                pass
        except Exception:
            logger.exception("[Drift][Cron] %s scan failed", level)


_scheduler: DriftCronScheduler | None = None
_lock = threading.Lock()


def ensure_scheduler_running() -> DriftCronScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    with _lock:
        if _scheduler is not None:
            return _scheduler
        _scheduler = DriftCronScheduler()
        _scheduler.start()
        return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.stop()
        _scheduler = None