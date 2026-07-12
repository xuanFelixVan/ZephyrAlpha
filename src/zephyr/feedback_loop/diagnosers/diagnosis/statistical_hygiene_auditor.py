# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.diagnosis.statistical_hygiene_auditor
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_statistical_hygiene_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Statistical Hygiene Auditor — v0.38.0 R476

Blindspot: Automated analysis is susceptible to statistical fallacies —
p-hacking (trying many thresholds until one triggers), multiple comparisons
(many metrics -> some false-positive by chance), survivorship bias (only
tracking successful actions), look-ahead bias (using future data in
backtesting), data snooping (overfitting to historical patterns).

Risk: R476 — FLE self-deception: thinks it's 95% effective but 30% of
"successes" are statistical noise. Grows overconfident on biased data.

Mitigation: Apply statistical rigor checks. Bonferroni correction for
multi-metric thresholds. Require replication before confirming anomaly.
Track false discovery rate. Flag when threshold tuning approaches p-hacking.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class StatViolation(str, Enum):
    P_HACKING = "P_HACKING"
    MULTIPLE_COMPARISONS = "MULTIPLE_COMPARISONS"
    SURVIVORSHIP_BIAS = "SURVIVORSHIP_BIAS"
    LOOK_AHEAD_BIAS = "LOOK_AHEAD_BIAS"
    DATA_SNOOPING = "DATA_SNOOPING"
    SMALL_SAMPLE = "SMALL_SAMPLE"


@dataclass
class StatisticalHygieneAuditor:
    min_sample_size: int = 30
    max_threshold_attempts: int = 5
    bonferroni_active_metrics: int = 1
    replication_required: bool = True

    threshold_attempts: dict[str, int] = field(default_factory=dict)
    active_metrics_count: int = 0
    violations: list[dict] = field(default_factory=list)
    confirmed_anomalies: dict[str, int] = field(default_factory=dict)
    unconfirmed_anomalies: dict[str, int] = field(default_factory=dict)

    def record_threshold_attempt(self, metric_name: str) -> dict:
        self.threshold_attempts[metric_name] = self.threshold_attempts.get(metric_name, 0) + 1
        attempts = self.threshold_attempts[metric_name]

        if attempts > self.max_threshold_attempts:
            self.violations.append(
                {
                    "ts": time.time(),
                    "type": StatViolation.P_HACKING.value,
                    "metric": metric_name,
                    "attempts": attempts,
                }
            )
            return {"violation": StatViolation.P_HACKING.value, "metric": metric_name, "attempts": attempts}
        return {"ok": True}

    def set_active_metrics(self, count: int) -> dict:
        self.active_metrics_count = count
        if count > 20:
            self.violations.append(
                {
                    "ts": time.time(),
                    "type": StatViolation.MULTIPLE_COMPARISONS.value,
                    "active_metrics": count,
                    "bonferroni_alpha": round(0.05 / max(count, 1), 5),
                }
            )
            return {
                "violation": StatViolation.MULTIPLE_COMPARISONS.value,
                "count": count,
                "corrected_alpha": round(0.05 / count, 5),
                "recommendation": "reduce_metric_cardinality_or_accept_higher_fpr",
            }
        return {"ok": True, "bonferroni_alpha": round(0.05 / max(count, 1), 5)}

    def record_anomaly_confirmation(self, anomaly_id: str, confirmed: bool) -> None:
        if confirmed:
            self.confirmed_anomalies[anomaly_id] = self.confirmed_anomalies.get(anomaly_id, 0) + 1
        else:
            self.unconfirmed_anomalies[anomaly_id] = self.unconfirmed_anomalies.get(anomaly_id, 0) + 1

    def check_survivorship_bias(self) -> dict:
        total_confirmed = sum(self.confirmed_anomalies.values())
        total_unconfirmed = sum(self.unconfirmed_anomalies.values())
        total = total_confirmed + total_unconfirmed

        if total == 0:
            return {"survivorship_bias": False}

        confirmation_rate = total_confirmed / total
        bias_detected = confirmation_rate > 0.90 and total > 20

        if bias_detected:
            self.violations.append(
                {
                    "ts": time.time(),
                    "type": StatViolation.SURVIVORSHIP_BIAS.value,
                    "confirmation_rate": round(confirmation_rate, 3),
                    "total": total,
                }
            )

        return {
            "survivorship_bias": bias_detected,
            "confirmation_rate": round(confirmation_rate, 3),
            "total_anomalies": total,
            "recommendation": "track_failed_actions_equally" if bias_detected else "continue",
        }

    def check_sample_size(self, sample_count: int, metric_name: str) -> dict:
        if sample_count < self.min_sample_size:
            self.violations.append(
                {
                    "ts": time.time(),
                    "type": StatViolation.SMALL_SAMPLE.value,
                    "metric": metric_name,
                    "sample_count": sample_count,
                }
            )
            return {
                "violation": StatViolation.SMALL_SAMPLE.value,
                "sample_count": sample_count,
                "min_required": self.min_sample_size,
                "recommendation": "suppress_anomaly_detection_until_enough_data",
            }
        return {"ok": True}

    def get_false_discovery_rate_estimate(self) -> float:
        active = max(self.active_metrics_count, 1)
        return min(1.0, 0.05 * active / max(len(self.confirmed_anomalies), 1))

    def overall_hygiene_score(self) -> float:
        base = 1.0
        base -= len(self.violations) * 0.1
        if self.active_metrics_count > 20:
            base -= 0.2
        total_anomalies = len(self.confirmed_anomalies) + len(self.unconfirmed_anomalies)
        if total_anomalies < self.min_sample_size:
            base -= 0.2
        return max(0.0, min(1.0, round(base, 3)))
