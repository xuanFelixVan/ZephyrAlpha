"""Latency SLO Monitor — v0.14.0 R192

Blindspot: Latency SLOs defined but not actively monitored; violations accumulate silently.
Risk: R192 — p95 latency 10x SLO; no alert because no automated SLO tracking.

Mitigation: p50/p95/p99 latency tracking with SLO compliance dashboard.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass
class LatencyWindow:
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    sample_count: int = 0
    window_start: float = field(default_factory=time.time)


@dataclass
class LatencySLO:
    p50_target_ms: float = 100.0
    p95_target_ms: float = 500.0
    p99_target_ms: float = 1000.0
    windows: list[LatencyWindow] = field(default_factory=list)

    def record(self, p50: float, p95: float, p99: float, count: int) -> None:
        window = LatencyWindow(p50_ms=p50, p95_ms=p95, p99_ms=p99, sample_count=count)
        self.windows.append(window)

    def current_status(self) -> dict[str, bool]:
        if not self.windows:
            return {"p50_ok": True, "p95_ok": True, "p99_ok": True}
        last = self.windows[-1]
        return {
            "p50_ok": last.p50_ms <= self.p50_target_ms,
            "p95_ok": last.p95_ms <= self.p95_target_ms,
            "p99_ok": last.p99_ms <= self.p99_target_ms,
        }
