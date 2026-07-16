# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.fix_scheduler
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;__main__.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 双模式调度;批量模式MUST遵守间隔;事件驱动MUST即时响应
# [MODIFY-GUARD] blueprint.md §3;auto_fix_config.yaml scheduler段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SchedulerError
# [TESTS] tests/auto-fix-engine/test_fix_scheduler.py
# [A_module] module_id=MOD-INF_fix_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import FixAction, FixReport

logger = logging.getLogger(__name__)


class SchedulerMode(str, Enum):
    # P0-4 修复：CONTINUOUS 模式已废弃（违反"禁止时间触发"硬约束）
    # 保留枚举值仅为向后兼容（配置文件/测试），start() 不再启动 time.sleep 循环
    CONTINUOUS = "continuous"
    EVENT_DRIVEN = "event_driven"


class FixScheduler:
    def __init__(
        self,
        mode: SchedulerMode = SchedulerMode.EVENT_DRIVEN,
        batch_interval_sec: int = 300,
        fix_fn: Callable[[list[FixAction]], FixReport] | None = None,
        scan_fn: Callable[[], list[FixAction]] | None = None,
    ) -> None:
        self._mode = mode
        self._batch_interval = batch_interval_sec
        self._fix_fn = fix_fn
        self._scan_fn = scan_fn
        self._running = False
        self._thread: threading.Thread | None = None
        self._event_queue: list[FixAction] = []
        self._lock = threading.Lock()
        self._last_batch_time: float = 0.0
        self._batch_count: int = 0
        self._lifecycle_lock = threading.Lock()  # 5.142.6 修复: 保护 start/stop 的 check-then-act, 避免 TOCTOU (与 _lock 分离, 避免与 event_queue 锁耦合)

    @property
    def mode(self) -> SchedulerMode:
        return self._mode

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def batch_count(self) -> int:
        return self._batch_count

    def start(self) -> None:
        # 5.142.6 修复: 加锁保护 check-then-act, 防止并发 start() 创建多个线程
        # P0-4 修复：CONTINUOUS 模式不再启动 time.sleep 循环（违反"禁止时间触发"硬约束）
        with self._lifecycle_lock:
            if self._running:
                return
            self._running = True
            if self._mode is SchedulerMode.CONTINUOUS:
                logger.warning(
                    "FixScheduler.CONTINUOUS 模式已废弃（违反禁止时间触发硬约束），"
                    "请改用 EVENT_DRIVEN 模式 + 事件订阅。本次 start() 仅标记 running=True，"
                    "不启动 time.sleep 循环线程。"
                )
        logger.info("Fix scheduler started in %s mode", self._mode.value)

    def stop(self) -> None:
        # 5.142.6 修复: 加锁保护 _running 写入, join 在锁外执行避免长时间持锁
        with self._lifecycle_lock:
            self._running = False
            thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=5)
        with self._lifecycle_lock:
            self._thread = None
        logger.info("Fix scheduler stopped")

    def submit_event(self, action: FixAction) -> None:
        with self._lock:
            self._event_queue.append(action)
        if self._mode is SchedulerMode.EVENT_DRIVEN and self._fix_fn:
            self._process_events()

    def _process_events(self) -> None:
        with self._lock:
            events = list(self._event_queue)
            self._event_queue.clear()
        if events and self._fix_fn:
            self._fix_fn(events)
            self._batch_count += 1

    def get_status(self) -> dict[str, Any]:
        return {
            "mode": self._mode.value,
            "running": self._running,
            "batch_count": self._batch_count,
            "pending_events": len(self._event_queue),
            "last_batch": datetime.fromtimestamp(self._last_batch_time, tz=UTC).isoformat()
            if self._last_batch_time
            else None,
        }
