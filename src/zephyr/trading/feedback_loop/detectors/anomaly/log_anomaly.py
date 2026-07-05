# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.anomaly.log_anomaly
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_log_anomaly | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Log Anomaly Detector — v0.6.0 R61

Blindspot: Structured log anomalies invisible to metric-only detection.
Risk: R61 — Error log spikes undetected while CPU/memory look normal.
"""

from dataclasses import dataclass


@dataclass
class LogAnomaly:
    error_rate_threshold: float = 0.05

    def check(self, error_rate: float) -> bool:
        return error_rate > self.error_rate_threshold
