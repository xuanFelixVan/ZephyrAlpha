# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.anomaly.intermittent_failure_pattern
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
# [A_module] module_id=MOD-UNK_intermittent_failure_pattern | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Intermittent Failure Pattern Detector — v0.40.0 R501

Blindspot: Failures that occur only under specific conditions — certain time
of day, specific load levels, particular sequence of preceding events — are
the hardest to diagnose. FLE sees each failure as an isolated incident and
misses the pattern connecting them.

Risk: R501 — Intermittent failures accumulate undiagnosed; FLE repeatedly
applies generic fixes that don't address the conditional root cause; system
degrades slowly with no one understanding why.

Mitigation: Correlate failure occurrences with environmental context (time
of day, day of week, load level, preceding actions, active features). When
same failure type occurs only under specific conditions -> flag as
intermittent pattern -> surface the triggering conditions for diagnosis.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class PatternConfidence(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class IntermittentFailurePattern:
    min_occurrences: int = 5
    condition_correlation_threshold: float = 0.70
    context_window_days: int = 7

    failure_contexts: dict[str, list[dict]] = field(default_factory=dict)
    discovered_patterns: list[dict] = field(default_factory=list)

    def record_failure(
        self,
        failure_type: str,
        context: dict,
    ) -> None:
        if failure_type not in self.failure_contexts:
            self.failure_contexts[failure_type] = []

        entry = {"ts": time.time(), **context}
        self.failure_contexts[failure_type].append(entry)

        cutoff = time.time() - self.context_window_days * 86400
        self.failure_contexts[failure_type] = [e for e in self.failure_contexts[failure_type] if e["ts"] > cutoff]

    def analyze_pattern(self, failure_type: str) -> dict:
        contexts = self.failure_contexts.get(failure_type, [])
        if len(contexts) < self.min_occurrences:
            return {
                "pattern_found": False,
                "confidence": PatternConfidence.NONE.value,
                "reason": "insufficient_occurrences",
            }

        condition_frequencies: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        total = len(contexts)

        condition_keys = [k for k in contexts[0].keys() if k not in ("ts", "failure_id")]
        for ctx in contexts:
            for key in condition_keys:
                val = str(ctx.get(key, "UNKNOWN"))
                condition_frequencies[key][val] += 1

        strong_conditions = []
        for key, freq_map in condition_frequencies.items():
            for val, count in freq_map.items():
                ratio = count / total
                if ratio >= self.condition_correlation_threshold and ratio < 1.0:
                    strong_conditions.append(
                        {
                            "condition": key,
                            "value": val,
                            "ratio": round(ratio, 3),
                            "occurrences": count,
                        }
                    )

        if not strong_conditions:
            return {
                "pattern_found": False,
                "confidence": PatternConfidence.NONE.value,
                "reason": "no_strong_correlations",
            }

        max_ratio = max(c["ratio"] for c in strong_conditions)
        if max_ratio >= 0.90:
            confidence = PatternConfidence.HIGH
        elif max_ratio >= 0.80:
            confidence = PatternConfidence.MEDIUM
        else:
            confidence = PatternConfidence.LOW

        pattern = {
            "failure_type": failure_type,
            "total_occurrences": total,
            "confidence": confidence.value,
            "trigger_conditions": strong_conditions,
            "discovered_at": time.time(),
        }
        self.discovered_patterns.append(pattern)

        return {
            "pattern_found": True,
            "failure_type": failure_type,
            "confidence": confidence.value,
            "occurrences": total,
            "triggers": [f"{c['condition']}={c['value']} ({c['ratio']:.0%})" for c in strong_conditions],
            "recommendation": (
                "reproduce_with_exact_conditions"
                if confidence is PatternConfidence.HIGH
                else "increase_context_capture_depth"
                if confidence is PatternConfidence.LOW
                else "investigate_conditional_root_cause"
            ),
        }

    def analyze_all_patterns(self) -> list[dict]:
        results = []
        for failure_type in self.failure_contexts:
            result = self.analyze_pattern(failure_type)
            if result["pattern_found"]:
                results.append(result)
        return results

    def get_temporal_clustering(self, failure_type: str) -> dict:
        contexts = self.failure_contexts.get(failure_type, [])
        if not contexts:
            return {"clustered": False}

        timestamps = sorted([c["ts"] for c in contexts])
        gaps = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
        if not gaps:
            return {"clustered": False}

        mean_gap = sum(gaps) / len(gaps)
        tight_clusters = sum(1 for g in gaps if g < mean_gap * 0.1)

        return {
            "clustered": tight_clusters > len(gaps) * 0.3,
            "total_occurrences": len(timestamps),
            "mean_gap_seconds": round(mean_gap, 1),
            "tight_clusters": tight_clusters,
            "interpretation": "bursty_failures" if tight_clusters > len(gaps) * 0.3 else "uniformly_distributed",
        }

    def get_all_discovered_patterns(self) -> list[dict]:
        return [
            {
                "failure_type": p["failure_type"],
                "confidence": p["confidence"],
                "triggers_count": len(p["trigger_conditions"]),
            }
            for p in self.discovered_patterns
        ]

    def overall_pattern_discovery_rate(self) -> float:
        analyzed = len({p["failure_type"] for p in self.discovered_patterns})
        total = len(self.failure_contexts)
        if total == 0:
            return 1.0
        return round(analyzed / total, 3)
