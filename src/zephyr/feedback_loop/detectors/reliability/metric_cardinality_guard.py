# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.reliability.metric_cardinality_guard
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_metric_cardinality_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Metric Cardinality Guard — v0.40.0 R495

Blindspot: High-cardinality metric dimensions (per-symbol, per-user, per-venue,
per-session) cause label combination explosion. Each unique label set creates
a new time series, silently consuming storage/network/memory until saturation.

Risk: R495 — Storage fills with high-cardinality metrics; query performance
degrades; FLE cannot read recent data to detect anomalies; silent data loss.

Mitigation: Track unique label value combinations per metric name. Alert when
cardinality exceeds threshold or growth rate is exponential. Auto-suggest
label pruning. Flag metrics approaching Prometheus-style cardinality limits.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class CardinalityStatus(str, Enum):
    SAFE = "SAFE"
    ELEVATED = "ELEVATED"
    DANGEROUS = "DANGEROUS"
    CRITICAL = "CRITICAL"


@dataclass
class MetricCardinalityGuard:
    max_cardinality: int = 10000
    warning_cardinality: int = 5000
    max_growth_rate_per_hour: float = 100.0
    window_size: int = 100

    metrics: dict[str, dict] = field(default_factory=dict)
    cardinality_alerts: list[dict] = field(default_factory=list)
    max_alerts: int = 200

    def record_labels(self, metric_name: str, label_set: tuple[tuple[str, str], ...]) -> dict:
        if metric_name not in self.metrics:
            self.metrics[metric_name] = {
                "unique_label_sets": set(),
                "history": [],
                "peak_cardinality": 0,
            }

        m = self.metrics[metric_name]
        m["unique_label_sets"].add(label_set)
        current_cardinality = len(m["unique_label_sets"])

        if current_cardinality > self.max_cardinality:
            m["unique_label_sets"] = set(list(m["unique_label_sets"])[-self.warning_cardinality :])
            current_cardinality = len(m["unique_label_sets"])
        m["history"].append({"ts": time.time(), "cardinality": current_cardinality})

        if len(m["history"]) > self.window_size:
            m["history"] = m["history"][-self.window_size :]

        if current_cardinality > m["peak_cardinality"]:
            m["peak_cardinality"] = current_cardinality

        status = self._classify_cardinality(current_cardinality)
        growth_rate = self._compute_growth_rate(metric_name)

        alert = None
        if status == CardinalityStatus.CRITICAL:
            alert = {
                "metric": metric_name,
                "cardinality": current_cardinality,
                "status": status.value,
                "growth_rate_per_hour": round(growth_rate, 1),
                "recommendation": "emergency_label_pruning",
            }
        elif status == CardinalityStatus.DANGEROUS:
            alert = {
                "metric": metric_name,
                "cardinality": current_cardinality,
                "status": status.value,
                "recommendation": "reduce_label_dimensions",
            }

        if alert:
            self.cardinality_alerts.append({**alert, "ts": time.time()})
            if len(self.cardinality_alerts) > self.max_alerts:
                self.cardinality_alerts = self.cardinality_alerts[-self.max_alerts :]

        return {
            "metric": metric_name,
            "cardinality": current_cardinality,
            "status": status.value,
            "growth_rate_per_hour": round(growth_rate, 1),
            "peak_cardinality": m["peak_cardinality"],
            "alert": alert,
        }

    def _classify_cardinality(self, count: int) -> CardinalityStatus:
        if count >= self.max_cardinality:
            return CardinalityStatus.CRITICAL
        if count >= self.warning_cardinality * 2:
            return CardinalityStatus.DANGEROUS
        if count >= self.warning_cardinality:
            return CardinalityStatus.ELEVATED
        return CardinalityStatus.SAFE

    def _compute_growth_rate(self, metric_name: str) -> float:
        m = self.metrics.get(metric_name)
        if not m or len(m["history"]) < 2:
            return 0.0

        latest = m["history"][-1]
        oldest = m["history"][0]
        hours = (latest["ts"] - oldest["ts"]) / 3600
        if hours < 0.01:
            return 0.0

        return (latest["cardinality"] - oldest["cardinality"]) / hours

    def get_top_cardinality_metrics(self, top_n: int = 5) -> list[dict]:
        ranked = sorted(
            [
                {"metric": name, "cardinality": len(m["unique_label_sets"]), "peak": m["peak_cardinality"]}
                for name, m in self.metrics.items()
            ],
            key=lambda x: -x["cardinality"],
        )
        return ranked[:top_n]

    def suggest_label_pruning(self, metric_name: str) -> list[str]:
        m = self.metrics.get(metric_name)
        if not m:
            return []
        suggestions = []
        if len(m["unique_label_sets"]) > self.warning_cardinality:
            suggestions.append(f"{metric_name}: consider removing high-cardinality dimensions")
        if self._compute_growth_rate(metric_name) > self.max_growth_rate_per_hour:
            suggestions.append(f"{metric_name}: exponential growth detected — cap unique label count")
        return suggestions

    def overall_cardinality_health(self) -> float:
        if not self.metrics:
            return 1.0
        critical = sum(1 for name, m in self.metrics.items() if len(m["unique_label_sets"]) >= self.max_cardinality)
        return round(max(0.0, 1.0 - critical * 0.2), 3)
