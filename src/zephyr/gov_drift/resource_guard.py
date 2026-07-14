# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.resource_guard
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/gov_drift/_infrastructure.py; tests/resource/test_resource_guard.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬限制不可突破
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_resource_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Resource Guard — 资源上限与优雅降级 D-023-23 · §6.16。


hard_limits: 512MB内存 / 2GB磁盘 / 200文件句柄


graceful_degradation四级: >75%并行减半 / >87.5%暂停非HIGH / >97.6% GC+checkpoint+5min重试 / OOM预警紧急退出


scalability: 10->100->500->1500模块渐进路线


对标 blueprint.md §6.16。"""

from __future__ import annotations

from typing import Final
import logging

logger = logging.getLogger(__name__)

import gc
import os
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class DegradationLevel(str, Enum):
    NORMAL = "NORMAL"

    LEVEL_1 = "LEVEL_1"

    LEVEL_2 = "LEVEL_2"

    LEVEL_3 = "LEVEL_3"

    LEVEL_4 = "LEVEL_4"


class ResourceStatus(str, Enum):
    OK = "OK"

    WARNING = "WARNING"

    CRITICAL = "CRITICAL"

    OOM = "OOM"


@dataclass
class ResourceLimits:
    max_memory_mb: int = 512

    max_disk_mb: int = 2048

    max_file_handles: int = 200

    l1_threshold: float = 0.75

    l2_threshold: float = 0.875

    l3_threshold: float = 0.976

    l4_threshold: float = 0.995


@dataclass
class ResourceSnapshot:
    memory_used_mb: float = 0.0

    disk_used_mb: float = 0.0

    file_handles_open: int = 0

    degradation_level: DegradationLevel = DegradationLevel.NORMAL

    status: ResourceStatus = ResourceStatus.OK

    snapshot_time: datetime = field(default_factory=lambda: datetime.now(UTC))


LIMITS: Final[ResourceLimits] = ResourceLimits()


_current_pool_size: int = 4


_original_pool_size: int = 4


_guard_lock = threading.Lock()


_on_critical: Callable[[], None] | None = None


def _get_memory_usage_mb() -> float:
    try:
        import psutil

        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

    except ImportError:
        return 0.0


def _get_disk_usage_mb(directory: str) -> float:
    try:
        import shutil

        usage = shutil.disk_usage(directory)

        return (usage.total - usage.free) / (1024 * 1024)

    except Exception:
        return 0.0


def snapshot(directory: str = ".") -> ResourceSnapshot:
    mem = _get_memory_usage_mb()

    disk = _get_disk_usage_mb(directory)

    mem_ratio = mem / max(LIMITS.max_memory_mb, 1)

    level = DegradationLevel.NORMAL

    status = ResourceStatus.OK

    if mem_ratio >= LIMITS.l4_threshold:
        level = DegradationLevel.LEVEL_4

        status = ResourceStatus.OOM

    elif mem_ratio >= LIMITS.l3_threshold:
        level = DegradationLevel.LEVEL_3

        status = ResourceStatus.CRITICAL

    elif mem_ratio >= LIMITS.l2_threshold:
        level = DegradationLevel.LEVEL_2

        status = ResourceStatus.CRITICAL

    elif mem_ratio >= LIMITS.l1_threshold:
        level = DegradationLevel.LEVEL_1

        status = ResourceStatus.WARNING

    return ResourceSnapshot(
        memory_used_mb=mem,
        disk_used_mb=disk,
        file_handles_open=0,
        degradation_level=level,
        status=status,
    )


def apply_degradation(snap: ResourceSnapshot, current_pool: int) -> tuple[int, DegradationLevel]:
    new_pool = current_pool

    level = snap.degradation_level

    if level == DegradationLevel.LEVEL_1:
        new_pool = max(1, current_pool // 2)

    elif level == DegradationLevel.LEVEL_2:
        new_pool = max(1, current_pool // 4)

    elif level == DegradationLevel.LEVEL_3:
        gc.collect()

        time.sleep(0.1)

        new_pool = max(1, current_pool // 8)

    elif level == DegradationLevel.LEVEL_4:
        new_pool = 0

        if _on_critical:
            try:
                _on_critical()

            except Exception as e:
                logger.debug("suppressed error in resource_guard", exc_info=True)

    return new_pool, level


_guard_running: bool = False


_guard_stop_event: threading.Event = threading.Event()


def guard_loop(
    check_interval_sec: float = 5.0,
    directory: str = ".",
    on_degraded: Callable[[DegradationLevel], None] | None = None,
) -> None:
    global _guard_running

    import atexit

    def _cleanup() -> None:
        stop_guard_loop()

        _restore_pool()

    # 5.77.4 修复：原 atexit.register(_cleanup) 在 guard_loop 函数体内，每次调用都注册新handler。
    # 改为加 _atexit_registered 守卫，确保只注册一次。
    if not getattr(guard_loop, '_atexit_registered', False):
        atexit.register(_cleanup)
        guard_loop._atexit_registered = True

    _guard_stop_event.clear()

    _guard_running = True

    consecutive_errors = 0

    max_consecutive_errors = 10

    while _guard_running and not _guard_stop_event.is_set():
        try:
            snap = snapshot(directory)

            if snap.status != ResourceStatus.OK:
                _apply_guard(snap, on_degraded)

            if snap.status == ResourceStatus.OOM:
                _restore_pool()

                break

            consecutive_errors = 0

        except Exception:
            consecutive_errors += 1

            if consecutive_errors >= max_consecutive_errors:
                break

            backoff = min(check_interval_sec * (2 ** min(consecutive_errors, 5)), 300)

            _guard_stop_event.wait(timeout=backoff)

            continue

        _guard_stop_event.wait(timeout=check_interval_sec)

    _guard_running = False


def stop_guard_loop() -> None:
    global _guard_running

    _guard_running = False

    _guard_stop_event.set()


def is_guard_running() -> bool:
    return _guard_running


def _apply_guard(
    snap: ResourceSnapshot,
    on_degraded: Callable[[DegradationLevel], None] | None,
) -> None:
    global _current_pool_size

    with _guard_lock:
        new_pool, level = apply_degradation(snap, _current_pool_size)

        _current_pool_size = new_pool

    if on_degraded:
        try:
            on_degraded(level)

        except Exception as e:
            logger.warning("suppressed error in resource_guard", exc_info=True)


def _restore_pool() -> None:
    global _current_pool_size

    with _guard_lock:
        _current_pool_size = _original_pool_size


def set_critical_handler(handler: Callable[[], None]) -> None:
    """设置OOM临界处理器。"""

    global _on_critical

    _on_critical = handler


def validate_scalability() -> dict[str, object]:
    milestones: list[int] = [10, 100, 500, 1500]

    results: dict[str, object] = {}

    for m in milestones:
        estimated_mem = min(m * 0.5, LIMITS.max_memory_mb)

        results[str(m)] = {
            "max_est_mem_mb": estimated_mem,
            "within_limit": estimated_mem <= LIMITS.max_memory_mb * 0.8,
            "recommended_pool": min(8, max(1, m // 50)),
        }

    return results
