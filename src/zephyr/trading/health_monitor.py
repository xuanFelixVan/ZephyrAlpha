# [A_module] module_id=MOD-ORC_health_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md

# [MODULE] zephyr.trading.health_monitor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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
    ) -> None:
        self._snapshot_dir = snapshot_dir
        self._max_restart_attempts = max_restart_attempts
        self._failure_counts: dict[str, int] = {}
        self._probe_fns: dict[str, Callable[[], ProbeResult]] = {}
        self._restart_fns: dict[str, Callable[[], bool]] = {}
        self._lock = threading.Lock()
        self._running = False
        self._telemetry_emitter_type = TelemetryEmitter

    def register_probe(
        self, capability_id: str, probe_fn: Callable[[], ProbeResult], restart_fn: Callable[[], bool] | None = None
    ) -> None:
        with self._lock:
            self._probe_fns[capability_id] = probe_fn
            if restart_fn:
                self._restart_fns[capability_id] = restart_fn

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
        self._running = True

    def stop(self) -> None:
        self._running = False
