# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.stochastic_diagnosis_verifier
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_stochastic_diagnosis_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Stochastic Diagnosis Verifier — v0.38.0 R483

Blindspot: FLE diagnoses are deterministic but fragile — a single diagnosis
may be an artifact of specific random initialization (model seed, sampling
order, data shuffle). Diagnosis seems confident but is actually path-dependent.

Risk: R483 — FLE pursues wrong fix because initial diagnosis was a fluke of
random seed; re-running with different seeds would produce different conclusion.

Mitigation: Re-run diagnosis pipeline with N different random seeds. Check
diagnosis stability across runs. If top diagnosis varies >20% across seeds
-> flag as unstable. Require consensus before acting on unstable diagnosis.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class StochasticDiagnosisVerifier:
    min_reruns: int = 5
    consensus_threshold: float = 0.60
    max_variance_tolerance: float = 0.20

    diagnosis_runs: dict[str, list[dict]] = field(default_factory=dict)
    stability_scores: dict[str, float] = field(default_factory=dict)
    unstable_diagnoses: list[dict] = field(default_factory=list)
    inversion_results: dict[str, dict] = field(default_factory=dict)

    def deterministic_seed(self, anomaly_id: str, run_index: int) -> int:
        key = f"{anomaly_id}:{run_index}"
        return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)

    def record_diagnosis_run(self, anomaly_id: str, run_index: int, root_cause: str, confidence: float) -> None:
        if anomaly_id not in self.diagnosis_runs:
            self.diagnosis_runs[anomaly_id] = []
        self.diagnosis_runs[anomaly_id].append(
            {
                "run": run_index,
                "root_cause": root_cause,
                "confidence": confidence,
            }
        )

    def verify_stability(self, anomaly_id: str) -> dict:
        runs = self.diagnosis_runs.get(anomaly_id, [])
        if len(runs) < self.min_reruns:
            return {
                "stable": False,
                "reason": f"insufficient_reruns:{len(runs)}<{self.min_reruns}",
                "recommendation": "run_more_seeds",
            }

        root_cause_counts: dict[str, int] = {}
        for run in runs:
            rc = run["root_cause"]
            root_cause_counts[rc] = root_cause_counts.get(rc, 0) + 1

        top_cause = max(root_cause_counts, key=lambda k: root_cause_counts[k])
        consensus_ratio = root_cause_counts[top_cause] / len(runs)

        stable = consensus_ratio >= self.consensus_threshold
        self.stability_scores[anomaly_id] = consensus_ratio

        if not stable:
            self.unstable_diagnoses.append(
                {
                    "ts": time.time(),
                    "anomaly_id": anomaly_id,
                    "top_cause": top_cause,
                    "consensus_ratio": round(consensus_ratio, 3),
                    "all_causes": dict(root_cause_counts),
                }
            )

        return {
            "stable": stable,
            "consensus_cause": top_cause if stable else None,
            "consensus_ratio": round(consensus_ratio, 3),
            "cause_distribution": {k: round(v / len(runs), 3) for k, v in root_cause_counts.items()},
            "total_reruns": len(runs),
            "recommendation": (
                "act_on_consensus" if stable else "request_human_review" if consensus_ratio < 0.4 else "increase_reruns"
            ),
        }

    def get_unstable_count(self) -> int:
        return len(self.unstable_diagnoses)

    def overall_diagnosis_reliability(self) -> float:
        if not self.stability_scores:
            return 1.0
        stable_count = sum(1 for s in self.stability_scores.values() if s >= self.consensus_threshold)
        return round(stable_count / len(self.stability_scores), 3)

    def clear_runs(self, anomaly_id: str) -> None:
        self.diagnosis_runs.pop(anomaly_id, None)
        self.stability_scores.pop(anomaly_id, None)
