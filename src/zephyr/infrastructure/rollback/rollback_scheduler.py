# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §7 Phase 5.3
# [MODULE] zephyr.infrastructure.rollback.rollback_scheduler
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.rollback.startup_shutdown; zephyr.trading.boot_hooks
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] start/stop are idempotent; daemon thread; never blocks boot/shutdown
# [MODIFY-GUARD] WAL_GC_INTERVAL_SECONDS / DRILL_CHECK_INTERVAL_SECONDS / WAL_RETENTION_DAYS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns SchedulerResult; logs error on failure; never raises in daemon thread
# [TESTS] tests/adversarial/test_rollback_scheduler.py
# [A_module] module_id=MOD-INF_rollback_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
RollbackScheduler — 回滚系统自动运行调度器 (MOD-INF-021 §7 Phase 5.3).

蓝图要求: "回滚演练必须定期自动执行；WAL 必须自动 GC，防止无限增长"

实现:
    - 后台守护线程，定期执行两个任务:
        1. WAL GC: 清理超过保留期的 COMPLETE 条目（默认 7 天）
        2. Drill 调度: 检查是否到演练时间（每周六 03:00 UTC），触发 RollbackDrill
    - start()/stop() 幂等，可安全集成到启动/停机序列
    - schedule_wal_gc()/schedule_drill() 可独立调用（用于测试和手动触发）

依赖:
    - RollbackWAL (WAL GC)
    - RollbackDrill (演练调度)
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SchedulerResult:
    """调度任务执行结果。"""
    task: str
    success: bool
    timestamp_utc: str
    details: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class RollbackScheduler:
    """回滚系统自动运行调度器。

    后台守护线程定期执行:
        1. WAL GC: 清理超过保留期的 COMPLETE 条目
        2. Drill 调度: 检查演练时间，触发 RollbackDrill
    """

    WAL_GC_INTERVAL_SECONDS: int = 3600  # WAL GC 每小时一次
    DRILL_CHECK_INTERVAL_SECONDS: int = 60  # 演练检查每分钟一次
    WAL_RETENTION_DAYS: int = 7  # WAL COMPLETE 条目保留 7 天

    def __init__(
        self,
        project_root: Path | None = None,
        wal: Any | None = None,
        drill: Any | None = None,
    ) -> None:
        self._project_root = project_root or Path.cwd()
        self._wal = wal
        self._drill = drill
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._running = False
        self._lock = threading.Lock()
        self._last_wal_gc: float = 0.0
        self._last_drill_check: float = 0.0
        self._gc_count: int = 0
        self._drill_count: int = 0

    def _get_wal(self) -> Any:
        if self._wal is not None:
            return self._wal
        try:
            from zephyr.infrastructure.rollback.rollback_wal import RollbackWAL
            self._wal = RollbackWAL(project_root=self._project_root)
        except Exception as e:
            logger.error("Failed to initialize RollbackWAL: %s", e, exc_info=True)
        return self._wal

    def _get_drill(self) -> Any:
        if self._drill is not None:
            return self._drill
        try:
            from zephyr.infrastructure.rollback.rollback_drill import RollbackDrill
            self._drill = RollbackDrill(project_root=self._project_root)
        except Exception as e:
            logger.error("Failed to initialize RollbackDrill: %s", e, exc_info=True)
        return self._drill

    def start(self) -> bool:
        """启动调度器（幂等）。已运行则返回 True。"""
        with self._lock:
            if self._running:
                logger.debug("RollbackScheduler already running")
                return True
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run_loop,
                daemon=True,
                name="rollback-scheduler",
            )
            self._thread.start()
            self._running = True
            logger.info(
                "RollbackScheduler started (wal_gc=%ds, drill_check=%ds, retention=%dd)",
                self.WAL_GC_INTERVAL_SECONDS,
                self.DRILL_CHECK_INTERVAL_SECONDS,
                self.WAL_RETENTION_DAYS,
            )
        return True

    def stop(self, timeout: float = 5.0) -> bool:
        """停止调度器（幂等）。未运行则返回 True。"""
        with self._lock:
            if not self._running:
                return True
            self._stop_event.set()
            thread = self._thread
            self._running = False
        if thread is not None:
            thread.join(timeout=timeout)
            if thread.is_alive():
                logger.warning("RollbackScheduler thread did not stop within %.1fs", timeout)
            else:
                logger.info("RollbackScheduler stopped (gc_count=%d, drill_count=%d)", self._gc_count, self._drill_count)
        return True

    def _run_loop(self) -> None:
        """调度器主循环（守护线程）。"""
        logger.debug("RollbackScheduler loop started")
        while not self._stop_event.is_set():
            now = time.time()
            # WAL GC
            if now - self._last_wal_gc >= self.WAL_GC_INTERVAL_SECONDS:
                try:
                    self.schedule_wal_gc()
                except Exception as e:
                    logger.error("RollbackScheduler WAL GC error: %s", e, exc_info=True)
                self._last_wal_gc = now
            # Drill check
            if now - self._last_drill_check >= self.DRILL_CHECK_INTERVAL_SECONDS:
                try:
                    self.schedule_drill()
                except Exception as e:
                    logger.error("RollbackScheduler drill check error: %s", e, exc_info=True)
                self._last_drill_check = now
            # 等待下一次检查（可被 stop 唤醒）
            self._stop_event.wait(self.DRILL_CHECK_INTERVAL_SECONDS)
        logger.debug("RollbackScheduler loop exited")

    def schedule_wal_gc(self) -> SchedulerResult:
        """执行 WAL 垃圾回收——清理超过保留期的 COMPLETE 条目。

        删除 written_at 早于 WAL_RETENTION_DAYS 天前的 COMPLETE 条目。
        保留所有 PENDING 条目（未完成的回滚不能删）。
        """
        timestamp = datetime.now(UTC).isoformat()
        wal = self._get_wal()
        if wal is None:
            return SchedulerResult(
                task="wal_gc",
                success=False,
                timestamp_utc=timestamp,
                errors=["WAL not available"],
            )

        wal_path = self._project_root / getattr(wal, "WAL_FILE", ".zephyr/rollback_wal.jsonl")
        if not wal_path.exists():
            self._gc_count += 1
            return SchedulerResult(
                task="wal_gc",
                success=True,
                timestamp_utc=timestamp,
                details={"removed": 0, "reason": "wal_file_not_exist"},
            )

        cutoff = datetime.now(UTC) - timedelta(days=self.WAL_RETENTION_DAYS)
        cutoff_str = cutoff.isoformat()

        entries = wal._read_all()
        kept: list[dict[str, Any]] = []
        removed: list[dict[str, Any]] = []

        for entry in entries:
            status = entry.get("status", "")
            written_at = entry.get("written_at", "")
            # PENDING 条目永远保留
            if status != "COMPLETE":
                kept.append(entry)
                continue
            # COMPLETE 且超过保留期 → 删除
            if written_at and written_at < cutoff_str:
                removed.append(entry)
            else:
                kept.append(entry)

        # 原子写入（RULE-ONE）
        tmp_path = f"{wal_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                for e in kept:
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
            os.replace(tmp_path, wal_path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return SchedulerResult(
                task="wal_gc",
                success=False,
                timestamp_utc=timestamp,
                errors=["permission_denied"],
            )

        self._gc_count += 1
        logger.info("WAL GC: removed %d entries (retention=%dd)", len(removed), self.WAL_RETENTION_DAYS)

        return SchedulerResult(
            task="wal_gc",
            success=True,
            timestamp_utc=timestamp,
            details={
                "removed": len(removed),
                "kept": len(kept),
                "retention_days": self.WAL_RETENTION_DAYS,
                "cutoff": cutoff_str,
            },
        )

    def schedule_drill(self) -> SchedulerResult | None:
        """检查并调度回滚演练。

        如果当前时间满足演练条件（每周六 03:00 UTC），触发 RollbackDrill.run_drill()。
        非演练时间返回 None。
        """
        timestamp = datetime.now(UTC).isoformat()
        drill = self._get_drill()
        if drill is None:
            return SchedulerResult(
                task="drill",
                success=False,
                timestamp_utc=timestamp,
                errors=["drill not available"],
            )

        # 检查是否到演练时间
        if not drill.is_drill_time():
            return None

        # 避免同一小时内重复触发
        now = datetime.now(UTC)
        drill_key = f"{now.strftime('%Y%m%d')}-drill-done"
        marker_path = self._project_root / ".zephyr" / drill_key
        if marker_path.exists():
            return None

        logger.info("Drill time reached, triggering RollbackDrill")
        try:
            result = drill.run_drill()
            self._drill_count += 1
            # 标记本次演练已完成（避免重复触发）
            try:
                marker_path.parent.mkdir(parents=True, exist_ok=True)
                marker_path.write_text(
                    json.dumps(
                        {
                            "drill_id": result.drill_id,
                            "timestamp_utc": timestamp,
                            "success": result.success,
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
            except Exception as e:
                logger.warning("Failed to write drill marker: %s", e, exc_info=True)

            return SchedulerResult(
                task="drill",
                success=result.success,
                timestamp_utc=timestamp,
                details={
                    "drill_id": result.drill_id,
                    "commit_sha": result.commit_sha,
                    "duration_ms": result.duration_ms,
                    "chaos_scenario": result.chaos_scenario,
                    "db_integrity_pass": result.db_integrity_pass,
                },
                errors=[] if result.success else [f"drill failed: {result.details}"],
            )
        except Exception as e:
            logger.error("RollbackDrill execution failed: %s", e, exc_info=True)
            return SchedulerResult(
                task="drill",
                success=False,
                timestamp_utc=timestamp,
                errors=[f"drill exception: {e}"],
            )

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def gc_count(self) -> int:
        return self._gc_count

    @property
    def drill_count(self) -> int:
        return self._drill_count

    def get_stats(self) -> dict[str, Any]:
        """获取调度器统计信息。"""
        return {
            "running": self._running,
            "gc_count": self._gc_count,
            "drill_count": self._drill_count,
            "last_wal_gc": self._last_wal_gc,
            "last_drill_check": self._last_drill_check,
            "wal_gc_interval_seconds": self.WAL_GC_INTERVAL_SECONDS,
            "drill_check_interval_seconds": self.DRILL_CHECK_INTERVAL_SECONDS,
            "wal_retention_days": self.WAL_RETENTION_DAYS,
        }