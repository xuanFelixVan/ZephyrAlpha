# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md
# [MODULE] zephyr.trading.health_monitor
# [DOMAIN] D-TRADING
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
from typing import Any

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.contracts.core.telemetry_emitter import TelemetryEmitter


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
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ReconciliationReport(BaseModel):
    model_config = BASE_CONFIG
    total_probed: int = 0
    active: int = 0
    degraded: int = 0
    inactive: int = 0
    actions_taken: list[str] = Field(default_factory=list)
    orphan_rate: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


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
        try:
            from zephyr.shared.longevity_monitor import LongevityMonitor

            _longevity = LongevityMonitor()

            def _longevity_probe() -> ProbeResult:
                try:
                    return ProbeResult(
                        capability_id="shared.longevity_monitor",
                        alive=True,
                        ready=True,
                    )
                except Exception as e:
                    return ProbeResult(
                        capability_id="shared.longevity_monitor",
                        alive=False,
                        error=str(e),
                    )

            self.register_probe("shared.longevity_monitor", _longevity_probe)
        except Exception:
            pass

        # 2. HealthcheckService
        try:
            from zephyr.shared.healthcheck_service import HealthcheckService

            project_root = Path(__file__).resolve().parents[3]
            _healthcheck = HealthcheckService(project_root=project_root)

            def _healthcheck_probe() -> ProbeResult:
                try:
                    return ProbeResult(
                        capability_id="shared.healthcheck_service",
                        alive=True,
                        ready=True,
                    )
                except Exception as e:
                    return ProbeResult(
                        capability_id="shared.healthcheck_service",
                        alive=False,
                        error=str(e),
                    )

            self.register_probe("shared.healthcheck_service", _healthcheck_probe)
        except Exception:
            pass

    def _monitor_loop(self) -> None:
        """分钟级监控循环 — DM-201247.

        - 每 _metrics_interval 秒：采集指标到 MetricsRegistry
        - 每 _health_check_interval 秒：运行健康检查 reconcile
        """
        while self._running:
            try:
                now = time.monotonic()
                # Metrics collection every interval
                self._collect_metrics()
                # Health check every health_check_interval
                if now - self._last_health_check >= self._health_check_interval:
                    self.reconcile()
                    self._last_health_check = now
            except Exception:
                pass
            time.sleep(self._metrics_interval)

    def _collect_metrics(self) -> None:
        """采集 probe 指标到 MetricsRegistry — DM-201247."""
        try:
            from zephyr.shared.observability_02.metrics import MetricsRegistry

            registry = MetricsRegistry()
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
        except Exception:
            pass

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
            return ProbeResult(capability_id=capability_id, error=str(e))

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
        except Exception:
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
        except Exception:
            pass
        try:
            import psutil

            mem = psutil.virtual_memory().percent
        except ImportError:
            return PressureLevel.NORMAL
        if mem > 90:
            return PressureLevel.CRITICAL
        if mem > 80:
            return PressureLevel.HIGH
        if mem > 70:
            return PressureLevel.ELEVATED
        return PressureLevel.NORMAL

    def pressure_response(self) -> str:
        level = self.pressure_level()
        if level == PressureLevel.CRITICAL:
            return "SHUTDOWN_L3_PRESERVE_L2"
        if level == PressureLevel.HIGH:
            return "THROTTLE_L3"
        return "NORMAL"

    def dump_last_snapshot(self) -> dict[str, Any]:
        results = self.probe_all()
        snapshot = {cid: r.model_dump() for cid, r in results.items()}
        if self._snapshot_dir:
            self._snapshot_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            path = self._snapshot_dir / f"health_{ts}.json"
            path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
        return snapshot

    def build_telemetry(self, capability_id: str, metric_name: str, metric_value: float) -> TelemetryEmitter:
        return self._telemetry_emitter_type(
            correlation_id=f"hm-{capability_id}",
            emitter_id="health-monitor",
            emitter_type="probe",
            idempotency_key=f"hm-{capability_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            metric_name=metric_name,
            metric_type="gauge",
            metric_value=metric_value,
            source_module="zephyr.trading.health_monitor",
            timestamp=datetime.now(),
        )

    def start(self) -> None:
        """启动健康监控 — DM-201247: 启动分钟级后台调度线程."""
        self._running = True
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._last_health_check = time.monotonic()
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True, name="health-monitor")
            self._monitor_thread.start()

    def stop(self) -> None:
        """停止健康监控 — DM-201247: 停止后台调度线程."""
        self._running = False
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        self._monitor_thread = None
