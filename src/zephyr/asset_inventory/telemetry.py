"""AssetInventoryTelemetry — MOD-INF-026 自监控指标

蓝图 §27：OpenTelemetry 三支柱（Metrics/Traces/Logs）风格的盘点器自监控。
"""

from __future__ import annotations

import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_sys_telemetry = None


def _get_sys_telemetry():
    global _sys_telemetry
    if _sys_telemetry is None:
        try:
            from zephyr.l12_system_telemetry.facade import Telemetry
            _sys_telemetry = Telemetry("asset_inventory", test_mode=os.environ.get("ZALPHA_TEST_MODE", "") == "1")
        except Exception:
            _sys_telemetry = False
    return _sys_telemetry if _sys_telemetry is not False else None


class MetricPoint(BaseModel):
    name: str = Field(description="指标名")
    value: float = Field(description="指标值")
    labels: dict[str, str] = Field(default_factory=dict, description="标签")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InventorySelfMetrics:
    """盘点系统自监控——内存中累计，可导出到 JSON / stdout / OTEL。"""

    def __init__(self) -> None:
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histories: dict[str, list[float]] = defaultdict(list)
        self._start_times: dict[str, float] = {}
        self._errors: list[str] = []

    def start_operation(self, name: str) -> None:
        self._start_times[name] = time.monotonic()

    def end_operation(self, name: str) -> float:
        t0 = self._start_times.pop(name, time.monotonic())
        elapsed = time.monotonic() - t0
        self._histories[f"{name}_duration_sec"].append(elapsed)
        return elapsed

    def inc(self, name: str, delta: float = 1.0, **labels: str) -> None:
        self._counters[name] += delta

    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def record_error(self, msg: str) -> None:
        self._errors.append(msg)
        self.inc("errors_total")

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histories": {k: {"count": len(v), "avg": sum(v) / len(v) if v else 0.0, "max": max(v) if v else 0.0} for k, v in self._histories.items()},
            "errors_count": len(self._errors),
            "errors_recent": self._errors[-10:],
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
        }

    def print(self) -> None:
        snap = self.snapshot()
        print("=== InventorySelfMetrics ===")
        print(f"  Counters: {snap['counters']}")
        print(f"  Gauges:   {snap['gauges']}")
        if snap["errors_recent"]:
            print(f"  Errors:   {snap['errors_count']} total, recent:")
            for e in snap["errors_recent"]:
                print(f"    - {e}")
        print("==============================")

    def push_to_facade(self) -> None:
        telemetry = _get_sys_telemetry()
        if telemetry is None:
            return
        try:
            for name, value in self._gauges.items():
                telemetry.metrics.gauge(name, value)
            for name, value in self._counters.items():
                telemetry.metrics.counter(f"{name}_total", value)
            telemetry.health.register()
        except Exception as exc:
            logger.warning("telemetry push_to_facade failed: %s", exc)


TELEMETRY = InventorySelfMetrics()


def get_telemetry() -> InventorySelfMetrics:
    return TELEMETRY
