# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation.ensemble_detector
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
# [A_module] module_id=MOD-UNK_ensemble_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Ensemble Detector — v0.4.0 R21

Blindspot: Single anomaly detection method misses multi-modal anomalies.
Risk: R21 — False negatives on anomalies detectable only by ensemble voting.
"""

from dataclasses import dataclass, field


@dataclass
class EnsembleDetector:
    detectors: list[str] = field(default_factory=list)

    def vote(self, scores: dict[str, float]) -> bool:
        return sum(1 for v in scores.values() if v > 2.5) > len(scores) // 2
