# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.health.self_bottleneck_detector
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_self_bottleneck_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Self-Bottleneck Detector — v0.38.0 R479

Blindspot: FLE pipeline stages (collect->detect->diagnose->act->verify) have
unknown performance characteristics. One slow stage creates backpressure
that cascades through the entire feedback loop. Anomaly detection delayed
because diagnosis queue is full.

Risk: R479 — FLE becomes the bottleneck it was designed to prevent. System
degrades because the watchdog is too slow to bark.

Mitigation: Per-stage latency tracking with percentile histograms. Detect
queue depth buildup at each pipeline stage. Identify slowest stage and
trigger auto-scaling or degradation. Alert when end-to-end latency exceeds
real-time requirements.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class PipelineStage(str, Enum):
    COLLECT = "COLLECT"
    DETECT = "DETECT"
    DIAGNOSE = "DIAGNOSE"
    ACT = "ACT"
    VERIFY = "VERIFY"


@dataclass
class SelfBottleneckDetector:
    max_stage_latency_ms: float = 5000.0
    max_e2e_latency_ms: float = 30000.0
    max_queue_depth: int = 100
    window_size: int = 100

    stage_latencies: dict[str, list[float]] = field(default_factory=lambda: {s.value: [] for s in PipelineStage})
    stage_queue_depths: dict[str, int] = field(default_factory=lambda: {s.value: 0 for s in PipelineStage})
    e2e_latencies: list[float] = field(default_factory=list)
    bottleneck_events: list[dict] = field(default_factory=list)
    current_bottleneck: str = ""

    def record_stage_latency(self, stage: PipelineStage, latency_ms: float) -> None:
        self.stage_latencies[stage.value].append(latency_ms)
        if len(self.stage_latencies[stage.value]) > self.window_size:
            self.stage_latencies[stage.value] = self.stage_latencies[stage.value][-self.window_size :]

    def record_e2e_latency(self, latency_ms: float) -> None:
        self.e2e_latencies.append(latency_ms)
        if len(self.e2e_latencies) > self.window_size:
            self.e2e_latencies = self.e2e_latencies[-self.window_size :]

    def set_queue_depth(self, stage: PipelineStage, depth: int) -> None:
        self.stage_queue_depths[stage.value] = depth

    def detect_bottleneck(self) -> dict:
        stage_stats = {}
        for stage in PipelineStage:
            lats = self.stage_latencies[stage.value]
            if not lats:
                continue
            lats_sorted = sorted(lats)
            p50 = lats_sorted[len(lats_sorted) // 2]
            p95 = lats_sorted[int(len(lats_sorted) * 0.95)]
            p99 = lats_sorted[int(len(lats_sorted) * 0.99)]
            stage_stats[stage.value] = {
                "p50_ms": round(p50, 1),
                "p95_ms": round(p95, 1),
                "p99_ms": round(p99, 1),
                "queue_depth": self.stage_queue_depths.get(stage.value, 0),
                "sample_count": len(lats),
            }

        slowest_stage = (
            max(
                stage_stats.items(),
                key=lambda x: x[1]["p95_ms"],
            )[0]
            if stage_stats
            else ""
        )

        queue_saturated = any(self.stage_queue_depths.get(s.value, 0) > self.max_queue_depth for s in PipelineStage)

        bottleneck = ""
        if slowest_stage and stage_stats[slowest_stage]["p95_ms"] > self.max_stage_latency_ms:
            bottleneck = slowest_stage
        elif queue_saturated:
            bottleneck = max(
                self.stage_queue_depths.items(),
                key=lambda x: x[1],
            )[0]

        if bottleneck and bottleneck != self.current_bottleneck:
            self.current_bottleneck = bottleneck
            self.bottleneck_events.append(
                {
                    "ts": time.time(),
                    "stage": bottleneck,
                    "p95_ms": stage_stats.get(bottleneck, {}).get("p95_ms", 0),
                    "queue_depth": self.stage_queue_depths.get(bottleneck, 0),
                }
            )

        e2e_p95 = 0.0
        if self.e2e_latencies:
            e2e_sorted = sorted(self.e2e_latencies)
            e2e_p95 = e2e_sorted[int(len(e2e_sorted) * 0.95)]

        return {
            "bottleneck": bottleneck or "none",
            "stage_stats": stage_stats,
            "e2e_p95_ms": round(e2e_p95, 1),
            "e2e_healthy": e2e_p95 < self.max_e2e_latency_ms,
            "queue_saturated": queue_saturated,
            "recommendation": (
                f"scale_{bottleneck}" if bottleneck else "increase_concurrency" if queue_saturated else "continue"
            ),
        }

    def overall_throughput_health(self) -> float:
        if not self.e2e_latencies:
            return 1.0
        p95 = sorted(self.e2e_latencies)[int(len(self.e2e_latencies) * 0.95)]
        return round(max(0.0, 1.0 - p95 / (self.max_e2e_latency_ms * 2)), 3)
