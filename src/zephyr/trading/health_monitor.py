# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.health_monitor
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.shared.contracts.core.telemetry_emitter; zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_health_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
HealthMonitor — 健康监控 + 自愈
================================
蓝图: ARC-0001 §6.1
借鉴: K8s Liveness/Readiness Probe + Level-Triggered Reconciliation
"""

import json
import threading
import time
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from typing import Any

import logging

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.contracts.core.telemetry_emitter import TelemetryEmitter
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

# 5.137.1 修复：内存压力分级阈值魔数提取为命名常量
_MEM_PRESSURE_CRITICAL = 90
_MEM_PRESSURE_HIGH = 80
_MEM_PRESSURE_ELEVATED = 70

# 5.43.5 修复：磁盘压力纳入分级阈值，disk_usage>90% 直接判为 CRITICAL
_DISK_PRESSURE_CRITICAL = 90

# 5.39.1 修复：模块级共享 MetricsRegistry，避免每次 _collect_metrics 创建新实例导致指标被 GC
_shared_metrics_registry = None


class PressureLevel(str, Enum):
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProbeResult(BaseModel):
    model_config = BASE_CONFIG
    capability_id: str
    alive: bool = False
    ready: bool = False
    latency_ms: float = 0.0
    error: str = ""
    timestamp: str = Field(default_factory=lambda: now_utc().isoformat())


class ReconciliationReport(BaseModel):
    model_config = BASE_CONFIG
    total_probed: int = 0
    active: int = 0
    degraded: int = 0
    inactive: int = 0
    actions_taken: list[str] = Field(default_factory=list)
    orphan_rate: float = 0.0
    timestamp: str = Field(default_factory=lambda: now_utc().isoformat())


class HealthMonitor:
    """健康监控 + 自愈——水平触发调和循环。

    借鉴:
      - K8s Liveness Probe: 组件是否存活
      - K8s Readiness Probe: 组件是否可服务
      - K8s Controller Pattern: 水平触发（不是事件驱动）
    """

    def __init__(
        self,
        snapshot_dir: Path | None = None,
        max_restart_attempts: int = 3,
        health_check_interval: int = 300,
        metrics_interval: int = 60,
    ) -> None:
        self._snapshot_dir = snapshot_dir
        self._max_restart_attempts = max_restart_attempts
        self._failure_counts: dict[str, int] = {}
        self._probe_fns: dict[str, Callable[[], ProbeResult]] = {}
        self._restart_fns: dict[str, Callable[[], bool]] = {}
        self._lock = threading.Lock()
        self._running = False
        self._telemetry_emitter_type = TelemetryEmitter
        self._monitor_thread: threading.Thread | None = None
        # 5.142.6 修复: 生命周期锁保护 start/stop 的 check-then-act, 避免两线程同时调用 start() 启动两个线程
        self._lifecycle_lock = threading.Lock()
        self._health_check_interval = health_check_interval
        self._metrics_interval = metrics_interval
        self._last_health_check: float = 0.0

    def register_probe(
        self, capability_id: str, probe_fn: Callable[[], ProbeResult], restart_fn: Callable[[], bool] | None = None
    ) -> None:
        with self._lock:
            self._probe_fns[capability_id] = probe_fn
            if restart_fn:
                self._restart_fns[capability_id] = restart_fn

    def register_shared_monitoring_probes(self) -> None:
        """注册 shared/ 监控模块为 probe — DM-201247.

        将 LongevityMonitor 和 HealthcheckService 注册为 K8s Probe 模式的健康检查。
        """
        # 1. LongevityMonitor
        # 5.55.3 修复：原硬编码 alive=True，现使用 LongevityMonitor.report() + psutil 真实内存退化检查
        try:
            from zephyr.shared.lifecycle.longevity_monitor import LongevityMonitor

            _longevity = LongevityMonitor()
            _longevity_component_id = "health_monitor"

            # 注册时采集基线内存（psutil 不可用时基线为 0，退化分数始终为 0 -> 永远 healthy）
            _baseline_mb = 0.0
            try:
                import psutil

                _baseline_mb = psutil.Process().memory_info().rss / (1024 * 1024)
            except ImportError:
                pass
            _longevity.register(_longevity_component_id, baseline_memory_mb=_baseline_mb)

            def _longevity_probe() -> ProbeResult:
                try:
                    current_mb = _baseline_mb  # psutil 不可用时退化分数为 0
                    try:
                        import psutil

                        current_mb = psutil.Process().memory_info().rss / (1024 * 1024)
                    except ImportError:
                        pass
                    report = _longevity.report(_longevity_component_id, current_mb)
                    # 退化分数阈值：>=0.8 视为不存活；>=0.5 视为存活但未就绪
                    alive = report.degradation_score < 0.8
                    ready = report.degradation_score < 0.5
                    return ProbeResult(
                        capability_id="shared.longevity_monitor",
                        alive=alive,
                        ready=ready,
                        error=f"degradation_score={report.degradation_score:.3f}" if not ready else "",
                    )
                except Exception as e:
                    return ProbeResult(
                        capability_id="shared.longevity_monitor",
                        alive=False,
                        error="internal error",
                    )

            self.register_probe("shared.longevity_monitor", _longevity_probe)
        except Exception:
            logger.debug("longevity probe registration failed", exc_info=True)

        # 2. HealthcheckService
        try:
            from zephyr.shared.lifecycle.healthcheck_service import HealthcheckService

            project_root = REPO_ROOT
            _healthcheck = HealthcheckService(project_root=project_root)

            def _healthcheck_probe() -> ProbeResult:
                # 5.55.3 修复：原硬编码 alive=True，现调用 check_all() 真实检查
                try:
                    report = _healthcheck.check_all()
                    healthy = report.overall_healthy
                    detail = "; ".join(c.message for c in report.components if not c.healthy)
                    return ProbeResult(
                        capability_id="shared.healthcheck_service",
                        alive=healthy,
                        ready=healthy,
                        error=detail if not healthy else "",
                    )
                except Exception as e:
                    return ProbeResult(
                        capability_id="shared.healthcheck_service",
                        alive=False,
                        error="internal error",
                    )

            self.register_probe("shared.healthcheck_service", _healthcheck_probe)
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞注册失败
            logger.debug("healthcheck probe registration failed", exc_info=True)

    def tick(self) -> None:
        """事件驱动入口：采集指标 + 条件性健康检查 reconcile。

        由 EventBus 事件（task.completed/task.failed 等）触发，
        或由 CI 批量兜底调用。替代原 _monitor_loop 的 time.sleep 轮询。
        """
        try:
            now = time.monotonic()
            self._collect_metrics()
            if now - self._last_health_check >= self._health_check_interval:
                self.reconcile()
                self._last_health_check = now
        except Exception:
            logger.exception("health monitor tick failed", exc_info=True)

    def _collect_metrics(self) -> None:
        """采集 probe 指标到 MetricsRegistry — DM-201247."""
        try:
            from zephyr.shared.observability.metrics import MetricsRegistry

            # 5.39.1 修复：原每次调用创建新 MetricsRegistry 实例，采集结束后局部变量被 GC，
            # 历史趋势不可查。改为模块级共享实例，保留历史指标数据。
            global _shared_metrics_registry
            if _shared_metrics_registry is None:
                _shared_metrics_registry = MetricsRegistry()
            registry = _shared_metrics_registry
            results = self.probe_all()
            for cid, result in results.items():
                registry.observe(
                    f"health.{cid}.alive",
                    1.0 if result.alive else 0.0,
                    labels={"capability_id": cid},
                )
                registry.observe(
                    f"health.{cid}.latency_ms",
                    result.latency_ms,
                    labels={"capability_id": cid},
                )
                # 5.39.8 修复：RED 方法论 Error 维度——健康检查失败时 increment error counter
                if not result.alive:
                    registry.inc(
                        f"health.{cid}.errors",
                        labels={"capability_id": cid},
                    )
        except Exception:
            # 5.53.6 修复：原 except: pass 静默吞没所有异常，metrics 采集失效时运维无感知。
            # 改为 warning 级别日志记录。
            logger.warning("health_monitor: _collect_metrics failed", exc_info=True)

    def probe(self, capability_id: str) -> ProbeResult:
        fn = self._probe_fns.get(capability_id)
        if fn is None:
            return ProbeResult(capability_id=capability_id, error="no probe registered")
        try:
            start = time.monotonic()
            result = fn()
            result.latency_ms = (time.monotonic() - start) * 1000
            return result
        except Exception as e:
            return ProbeResult(capability_id=capability_id, error="internal error")

    def probe_all(self) -> dict[str, ProbeResult]:
        results: dict[str, ProbeResult] = {}
        with self._lock:
            ids = list(self._probe_fns.keys())
        for cid in ids:
            results[cid] = self.probe(cid)
        return results

    def reconcile(self, orphan_rate: float = 0.0) -> ReconciliationReport:
        report = ReconciliationReport(orphan_rate=orphan_rate)
        results = self.probe_all()
        report.total_probed = len(results)

        for cid, result in results.items():
            if result.alive and result.ready:
                report.active += 1
                self._failure_counts[cid] = 0
            elif result.alive:
                report.degraded += 1
                report.actions_taken.append(f"{cid}: DEGRADED, attempting auto_restart")
                self._auto_restart(cid)
            else:
                report.inactive += 1
                report.actions_taken.append(f"{cid}: INACTIVE, alert triggered")

        return report

    def auto_restart(self, capability_id: str) -> bool:
        return self._auto_restart(capability_id)

    def _auto_restart(self, capability_id: str) -> bool:
        with self._lock:
            self._failure_counts[capability_id] = self._failure_counts.get(capability_id, 0) + 1
            if self._failure_counts[capability_id] > self._max_restart_attempts:
                return False
        fn = self._restart_fns.get(capability_id)
        if fn is None:
            return False
        try:
            return fn()
        except Exception as e:
            logger.warning("_auto_restart: restart failed for capability %s (%s: %s)", capability_id, type(e).__name__, e, exc_info=True)
            return False

    def pressure_level(self) -> PressureLevel:
        try:
            from zephyr.trading.resource_optimization import PressureLevel as ROELevel
            from zephyr.trading.resource_optimization import ResourceOptimizationEngine

            engine = ResourceOptimizationEngine()
            roe_level = engine.get_pressure_state().current_level
            mapping = {
                ROELevel.NORMAL: PressureLevel.NORMAL,
                ROELevel.WARNING: PressureLevel.ELEVATED,
                ROELevel.CRITICAL: PressureLevel.HIGH,
                ROELevel.EMERGENCY: PressureLevel.CRITICAL,
            }
            return mapping.get(roe_level, PressureLevel.NORMAL)
        except Exception as e:
            logger.warning("suppressed error in health_monitor", exc_info=True)
        try:
            import psutil

            mem = psutil.virtual_memory().percent
        except ImportError:
            return PressureLevel.NORMAL
        # 5.43.5 修复：disk_usage>90% 纳入压力分类阈值
        try:
            disk = psutil.disk_usage("/").percent
        except Exception:
            disk = 0.0
        if mem > _MEM_PRESSURE_CRITICAL or disk > _DISK_PRESSURE_CRITICAL:
            return PressureLevel.CRITICAL
        if mem > _MEM_PRESSURE_HIGH:
            return PressureLevel.HIGH
        if mem > _MEM_PRESSURE_ELEVATED:
            return PressureLevel.ELEVATED
        return PressureLevel.NORMAL

    def pressure_response(self) -> str:
        level = self.pressure_level()
        if level is PressureLevel.CRITICAL:
            return "SHUTDOWN_L3_PRESERVE_L2"
        if level is PressureLevel.HIGH:
            return "THROTTLE_L3"
        return "NORMAL"

    def dump_last_snapshot(self) -> dict[str, Any]:
        results = self.probe_all()
        snapshot = {cid: r.model_dump() for cid, r in results.items()}
        if self._snapshot_dir:
            self._snapshot_dir.mkdir(parents=True, exist_ok=True)
            ts = now_utc().strftime("%Y%m%d%H%M%S")
            path = self._snapshot_dir / f"health_{ts}.json"
            path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
        return snapshot

    def build_telemetry(self, capability_id: str, metric_name: str, metric_value: float) -> TelemetryEmitter:
        return self._telemetry_emitter_type(
            correlation_id=f"hm-{capability_id}",
            emitter_id="health-monitor",
            emitter_type="probe",
            idempotency_key=f"hm-{capability_id}-{now_utc().strftime('%Y%m%d%H%M%S')}",
            metric_name=metric_name,
            metric_type="gauge",
            metric_value=metric_value,
            source_module="zephyr.trading.health_monitor",
            timestamp=now_utc(),
        )

    def start(self) -> None:
        """启动健康监控 — P1 修复（2026-07-05）：事件驱动替代 time.sleep daemon。

        订阅 EventBus 事件（task.completed/task.failed）触发 tick()，
        不再启动后台轮询线程。CI 批量兜底由外部调用 tick()。
        """
        with self._lifecycle_lock:
            if self._running:
                return
            self._running = True
            self._last_health_check = time.monotonic()
            try:
                from zephyr.shared.events.event_bus import bus

                bus.subscribe("task.completed", lambda _: self.tick())
                bus.subscribe("task.failed", lambda _: self.tick())
                bus.subscribe("health.check.request", lambda _: self.tick())
                logger.info("HealthMonitor started (event-driven, no daemon thread)")
            except Exception as e:
                logger.warning("HealthMonitor EventBus subscribe failed, tick() must be called manually: %s", e, exc_info=True)

    def stop(self) -> None:
        """停止健康监控 — P1 修复：事件驱动模式无线程需 join。"""
        with self._lifecycle_lock:
            self._running = False
        logger.info("HealthMonitor stopped (event-driven mode)")