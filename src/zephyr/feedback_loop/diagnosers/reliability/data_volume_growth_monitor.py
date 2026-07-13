# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.data_volume_growth_monitor
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_data_volume_growth_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Data Volume Growth Monitor — v0.39.0 R492

Blindspot: Metric storage, logs, checkpoints, and event timelines grow
monotonically. FLE writes data but never checks if storage is approaching
limits. Disk fills silently until writes fail.

Risk: R492 — FLE stops collecting metrics because disk is full. Anomalies
go undetected because the data pipeline silently dropped. Recovery requires
manual intervention from the 1-person team that's already overwhelmed.

Mitigation: Track data volume growth rates per storage sink. Project time-to-full
using linear/exponential growth models. Alert when TTF (time-to-full) drops
below threshold. Auto-trigger retention policy tightening or compaction.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class GrowthModel(str, Enum):
    LINEAR = "LINEAR"
    EXPONENTIAL = "EXPONENTIAL"
    STABLE = "STABLE"


@dataclass
class DataVolumeGrowthMonitor:
    warning_ttf_days: float = 30.0
    critical_ttf_days: float = 7.0
    min_samples_for_projection: int = 5

    storage_sinks: dict[str, dict] = field(default_factory=dict)
    growth_alerts: list[dict] = field(default_factory=list)

    def register_sink(self, sink_name: str, current_bytes: int, max_bytes: int, retention_days: float) -> None:
        self.storage_sinks[sink_name] = {
            "current_bytes": current_bytes,
            "max_bytes": max_bytes,
            "retention_days": retention_days,
            "history": [{"ts": time.time(), "bytes": current_bytes}],
            "growth_model": GrowthModel.STABLE,
            "ttf_days": float("inf"),
        }

    def record_volume(self, sink_name: str, current_bytes: int) -> dict:
        sink = self.storage_sinks.get(sink_name)
        if not sink:
            return {"error": "unknown_sink"}

        sink["current_bytes"] = current_bytes
        sink["history"].append({"ts": time.time(), "bytes": current_bytes})
        if len(sink["history"]) > 200:
            sink["history"] = sink["history"][-200:]

        projection = self._project_growth(sink_name)
        sink["growth_model"] = GrowthModel(projection["model"])
        sink["ttf_days"] = projection["ttf_days"]

        alert = None
        if projection["ttf_days"] < self.critical_ttf_days:
            alert = {
                "sink": sink_name,
                "severity": "CRITICAL",
                "ttf_days": round(projection["ttf_days"], 1),
                "usage_pct": round(100.0 * current_bytes / max(sink["max_bytes"], 1), 1),
                "recommendation": "trigger_emergency_compaction",
            }
        elif projection["ttf_days"] < self.warning_ttf_days:
            alert = {
                "sink": sink_name,
                "severity": "WARNING",
                "ttf_days": round(projection["ttf_days"], 1),
                "usage_pct": round(100.0 * current_bytes / max(sink["max_bytes"], 1), 1),
                "recommendation": "tighten_retention_policy",
            }

        if alert:
            self.growth_alerts.append({**alert, "ts": time.time()})

        return {
            "sink": sink_name,
            "usage_pct": round(100.0 * current_bytes / max(sink["max_bytes"], 1), 1),
            "ttf_days": round(projection["ttf_days"], 1) if projection["ttf_days"] != float("inf") else None,
            "growth_model": projection["model"],
            "alert": alert,
        }

    def _project_growth(self, sink_name: str) -> dict:
        sink = self.storage_sinks.get(sink_name)
        if not sink:
            return {"model": GrowthModel.STABLE.value, "ttf_days": float("inf")}

        history = sink["history"]
        if len(history) < self.min_samples_for_projection:
            return {"model": GrowthModel.STABLE.value, "ttf_days": float("inf")}

        latest = history[-1]
        oldest = history[0]
        time_span_days = (latest["ts"] - oldest["ts"]) / 86400.0
        if time_span_days < 0.01:
            return {"model": GrowthModel.STABLE.value, "ttf_days": float("inf")}

        bytes_added = latest["bytes"] - oldest["bytes"]
        if bytes_added <= 0:
            return {"model": GrowthModel.STABLE.value, "ttf_days": float("inf")}

        linear_rate = bytes_added / time_span_days

        last_half = history[len(history) // 2 :]
        if len(last_half) >= 2:
            half_span = (last_half[-1]["ts"] - last_half[0]["ts"]) / 86400.0
            half_bytes = last_half[-1]["bytes"] - last_half[0]["bytes"]
            recent_rate = half_bytes / max(half_span, 0.01)

            if recent_rate > linear_rate * 1.5:
                model = GrowthModel.EXPONENTIAL
                rate = recent_rate
            elif abs(recent_rate - linear_rate) / max(linear_rate, 1) < 0.2:
                model = GrowthModel.LINEAR
                rate = linear_rate
            else:
                model = GrowthModel.LINEAR
                rate = max(recent_rate, linear_rate)
        else:
            model = GrowthModel.LINEAR
            rate = linear_rate

        remaining = sink["max_bytes"] - latest["bytes"]
        ttf = remaining / max(rate, 1)

        return {"model": model.value, "ttf_days": round(ttf, 1), "rate_bytes_per_day": round(rate, 0)}

    def get_all_projections(self) -> list[dict]:
        return [
            {
                "sink": name,
                "usage_pct": round(100.0 * s["current_bytes"] / max(s["max_bytes"], 1), 1),
                "ttf_days": round(s["ttf_days"], 1) if s["ttf_days"] != float("inf") else None,
                "model": s["growth_model"].value,
            }
            for name, s in self.storage_sinks.items()
        ]

    def overall_storage_health(self) -> float:
        if not self.storage_sinks:
            return 1.0
        critical = sum(1 for s in self.storage_sinks.values() if s["ttf_days"] < self.critical_ttf_days)
        return round(max(0.0, 1.0 - critical * 0.5), 3)
