# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.guard.alert_desensitization_curve
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_alert_desensitization_curve | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Alert Desensitization Curve — v0.37.0 R492

Blindspot: Repeated similar alerts cause operator desensitization;
critical signals are ignored after N exposures to similar patterns.

Risk: R492 — Operator stops responding to real incidents due to alert fatigue.

Mitigation: Track per-alert-type exposure count. Model desensitization as
exponential decay of response probability. When curve drops below 50%,
auto-escalate to alternate channel or increase severity.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AlertDesensitizationCurve:
    decay_lambda: float = 0.1
    threshold: float = 0.5

    alert_exposures: dict[str, int] = field(default_factory=dict)
    response_history: dict[str, list[bool]] = field(default_factory=dict)

    def record_exposure(self, alert_type: str, did_respond: bool) -> float:
        self.alert_exposures[alert_type] = self.alert_exposures.get(alert_type, 0) + 1

        if alert_type not in self.response_history:
            self.response_history[alert_type] = []
        self.response_history[alert_type].append(did_respond)
        if len(self.response_history[alert_type]) > 50:
            self.response_history[alert_type] = self.response_history[alert_type][-50:]

        return self.get_desensitization(alert_type)

    def get_desensitization(self, alert_type: str) -> float:
        n = self.alert_exposures.get(alert_type, 0)
        p = 1.0 * (self.decay_lambda**n)
        return max(0.0, min(1.0, p))

    def get_response_rate(self, alert_type: str) -> float:
        history = self.response_history.get(alert_type, [])
        if not history:
            return 1.0
        return sum(history) / len(history)

    def needs_escalation(self, alert_type: str) -> bool:
        return self.get_desensitization(alert_type) < self.threshold

    def is_desensitized(self) -> list[str]:
        return [t for t in self.alert_exposures if self.needs_escalation(t)]
