# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.finalizer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Finalizer — 优雅清理器
========================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
借鉴: K8s Finalizer + OwnerReference
"""

import logging
import threading
from collections.abc import Callable

_logger = logging.getLogger(__name__)


class Finalizer:
    """优雅清理器——关闭前完成所有必要持久化。"""

    def __init__(self) -> None:
        self._cleanup_fns: list[tuple[str, Callable[[], None]]] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def cleanup_fns(self) -> list[tuple[str, Callable[[], None]]]:
        """只读：cleanup_fns（Stage 4 公共化）。"""
        return self._cleanup_fns

    @cleanup_fns.setter
    def cleanup_fns(self, value):
        """写入：cleanup_fns（Stage 4 公共化）。"""
        self._cleanup_fns = value

    def register(self, resource_type: str, cleanup_fn: Callable[[], None]) -> None:
        self._cleanup_fns.append((resource_type, cleanup_fn))

    def run(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for resource_type, fn in self._cleanup_fns:
            try:
                fn()
                results[resource_type] = True
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                results[resource_type] = False
        return results


# ── DM-201249: 监控模块自动关闭清理链 ────────────────────────────────────

_monitoring_finalizers_registered = False


def register_monitoring_finalizers(finalizer: Finalizer) -> None:
    """注册监控模块的 Finalizer 清理函数 — DM-201249.

    在系统关闭时自动：
    1. monitor-flush — flush MetricsRegistry 指标数据
    2. monitor-health-snapshot — 保存健康快照

    幂等：重复调用不会重复注册。
    安全：cleanup 函数永不抛异常。
    """
    global _monitoring_finalizers_registered
    if _monitoring_finalizers_registered:
        return
    _monitoring_finalizers_registered = True

    def _monitor_flush() -> None:
        """flush MetricsRegistry — DM-201249."""
        try:
            from zephyr.shared.observability.metrics import get_registry

            registry = get_registry()
            snapshots = registry.snapshot()
            _logger.info("Monitor flush: %d metrics snapshots flushed", len(snapshots))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.debug("Monitor flush failed: %s", e, exc_info=True)

    def _monitor_health_snapshot() -> None:
        """保存健康快照 — DM-201249."""
        try:
            from zephyr.shared.lifecycle.health import get_event_health_log

            log = get_event_health_log()
            _logger.info("Monitor health snapshot: %d event log entries saved", len(log))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.debug("Monitor health snapshot failed: %s", e, exc_info=True)

    finalizer.register("monitor-flush", _monitor_flush)
    finalizer.register("monitor-health-snapshot", _monitor_health_snapshot)


_global_finalizer: Finalizer | None = None
_global_finalizer_lock = threading.Lock()


def get_finalizer() -> Finalizer:
    """获取全局 Finalizer 单例 — DM-201249."""
    global _global_finalizer
    if _global_finalizer is None:
        with _global_finalizer_lock:
            if _global_finalizer is None:
                _global_finalizer = Finalizer()
    return _global_finalizer


def register_monitoring_finalizers_auto() -> None:
    """自动注册监控清理函数到全局 Finalizer — DM-201249.

    无需传入 Finalizer 实例，使用全局单例。
    """
    register_monitoring_finalizers(get_finalizer())
