# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.model_version_semantic_drift
# [DOMAIN] D_OPS
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
# [A_module] module_id=MOD-UNK_model_version_semantic_drift | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""Model Version Semantic Drift Monitor — v0.39.0 R493

Blindspot: LLM model versions change (gpt-4→gpt-4-turbo→gpt-4o, claude-3→3.5→4)
with different semantic behaviors. Same prompt produces different quality/format/tone.
FLE diagnosis quality silently degrades because underlying model changed.

Risk: R493 — Model upgrade silently changes diagnosis accuracy. FLE thinks it's
using the same quality model but actually running on a degraded one. Provider-side
model deprecations catch FLE off guard.

Mitigation: Track model version fingerprints. Compare output distributions
across model versions on a held-out benchmark set. Detect semantic drift
when output characteristics change beyond threshold. Alert before model
deprecation dates.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum


class DriftSeverity(str, Enum):
    NONE = "NONE"
    MINOR = "MINOR"
    SIGNIFICANT = "SIGNIFICANT"
    BREAKING = "BREAKING"


@dataclass
class ModelVersionSemanticDrift:
    drift_threshold_mean_shift: float = 0.15
    drift_threshold_variance_shift: float = 0.30
    max_minor_drift: int = 3

    model_fingerprints: dict[str, dict] = field(default_factory=dict)
    benchmark_baselines: dict[str, dict] = field(default_factory=dict)
    drift_events: list[dict] = field(default_factory=list)

    def register_model(self, model_id: str, version: str, provider: str, deprecation_date: float | None = None) -> None:
        self.model_fingerprints[model_id] = {
            "version": version,
            "provider": provider,
            "deprecation_date": deprecation_date,
            "registered_at": time.time(),
            "fingerprint": self._compute_fingerprint(model_id, version),
        }

    def record_benchmark(self, model_id: str, benchmark_name: str, scores: list[float]) -> dict:
        if model_id not in self.model_fingerprints:
            return {"error": "unknown_model"}

        mean_score = sum(scores) / len(scores) if scores else 0.0
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores) if scores else 0.0

        if model_id not in self.benchmark_baselines:
            self.benchmark_baselines[model_id] = {}

        self.benchmark_baselines[model_id][benchmark_name] = {
            "mean": mean_score,
            "variance": variance,
            "sample_count": len(scores),
            "recorded_at": time.time(),
        }

        return {
            "model_id": model_id,
            "benchmark": benchmark_name,
            "mean_score": round(mean_score, 4),
            "sample_count": len(scores),
        }

    def check_semantic_drift(self, model_id: str, benchmark_name: str, new_scores: list[float]) -> dict:
        if model_id not in self.benchmark_baselines:
            return {"severity": DriftSeverity.NONE.value, "reason": "no_baseline"}

        baseline = self.benchmark_baselines[model_id].get(benchmark_name)
        if not baseline:
            return {"severity": DriftSeverity.NONE.value, "reason": f"no_baseline_for_{benchmark_name}"}

        new_mean = sum(new_scores) / len(new_scores) if new_scores else 0.0
        new_variance = sum((s - new_mean) ** 2 for s in new_scores) / len(new_scores) if new_scores else 0.0

        mean_shift = abs(new_mean - baseline["mean"]) / max(abs(baseline["mean"]), 0.001)
        variance_shift = abs(new_variance - baseline["variance"]) / max(baseline["variance"], 0.001)

        if mean_shift > self.drift_threshold_mean_shift * 2 or variance_shift > self.drift_threshold_variance_shift * 2:
            severity = DriftSeverity.BREAKING
        elif mean_shift > self.drift_threshold_mean_shift or variance_shift > self.drift_threshold_variance_shift:
            severity = DriftSeverity.SIGNIFICANT
        elif mean_shift > self.drift_threshold_mean_shift / 2:
            severity = DriftSeverity.MINOR
        else:
            severity = DriftSeverity.NONE

        if severity is not DriftSeverity.NONE:
            self.drift_events.append(
                {
                    "ts": time.time(),
                    "model_id": model_id,
                    "benchmark": benchmark_name,
                    "severity": severity.value,
                    "mean_shift": round(mean_shift, 4),
                    "variance_shift": round(variance_shift, 4),
                }
            )

        return {
            "model_id": model_id,
            "benchmark": benchmark_name,
            "severity": severity.value,
            "mean_shift": round(mean_shift, 4),
            "variance_shift": round(variance_shift, 4),
            "baseline_mean": round(baseline["mean"], 4),
            "current_mean": round(new_mean, 4),
            "recommendation": (
                "rollback_model_version"
                if severity is DriftSeverity.BREAKING
                else "increase_benchmark_frequency"
                if severity is DriftSeverity.SIGNIFICANT
                else "continue_monitoring"
            ),
        }

    def check_deprecation_proximity(self) -> list[dict]:
        now = time.time()
        alerts = []
        for model_id, info in self.model_fingerprints.items():
            dep_date = info.get("deprecation_date")
            if dep_date is None:
                continue
            days_left = (dep_date - now) / 86400.0
            if days_left < 7:
                alerts.append(
                    {
                        "model_id": model_id,
                        "provider": info["provider"],
                        "version": info["version"],
                        "days_until_deprecation": round(days_left, 1),
                        "severity": "CRITICAL" if days_left < 1 else "HIGH" if days_left < 7 else "MEDIUM",
                        "recommendation": "migrate_to_successor_model",
                    }
                )
            elif days_left < 30:
                alerts.append(
                    {
                        "model_id": model_id,
                        "days_until_deprecation": round(days_left, 1),
                        "severity": "MEDIUM",
                        "recommendation": "plan_migration",
                    }
                )
        return alerts

    def _compute_fingerprint(self, model_id: str, version: str) -> str:
        key = f"{model_id}:{version}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def get_drift_summary(self) -> dict:
        breaking = sum(1 for e in self.drift_events if e["severity"] == DriftSeverity.BREAKING.value)
        significant = sum(1 for e in self.drift_events if e["severity"] == DriftSeverity.SIGNIFICANT.value)
        minor = sum(1 for e in self.drift_events if e["severity"] == DriftSeverity.MINOR.value)

        return {
            "models_tracked": len(self.model_fingerprints),
            "breaking_drifts": breaking,
            "significant_drifts": significant,
            "minor_drifts": minor,
            "deprecation_alerts": len(self.check_deprecation_proximity()),
            "healthy": breaking == 0 and significant <= self.max_minor_drift,
            "recommendation": "freeze_all_model_upgrades" if breaking > 0 else "continue",
        }

    def overall_model_health(self) -> float:
        if not self.model_fingerprints:
            return 1.0
        breaking = sum(1 for e in self.drift_events if e["severity"] == DriftSeverity.BREAKING.value)
        return round(max(0.0, 1.0 - breaking * 0.2), 3)
