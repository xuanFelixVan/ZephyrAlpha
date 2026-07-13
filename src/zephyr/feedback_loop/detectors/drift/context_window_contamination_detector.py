# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.drift.context_window_contamination_detector
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
# [A_module] module_id=MOD-UNK_context_window_contamination_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Context Window Contamination Detector — v0.38.0 R471

Blindspot: Vibe coding AI sessions receive contaminated context — stale session
resumes, hallucinated references, cross-session information leakage, or RAG-retrieved
irrelevant chunks — and FLE has no way to detect this pollution.

Risk: R471 — AI makes decisions based on wrong context; FLE diagnoses based on
contaminated metrics; cascade failure of trust in automated decisions.

Mitigation: Token source provenance tracking. Monitor per-source token ratios.
Detect when stale context exceeds freshness threshold. Cross-session fingerprint
comparison to detect unintended information carryover.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class TokenSource(str, Enum):
    CURRENT_SESSION = "CURRENT_SESSION"
    RESUME_FROM_PRIOR = "RESUME_FROM_PRIOR"
    RAG_RETRIEVAL = "RAG_RETRIEVAL"
    SYSTEM_PROMPT = "SYSTEM_PROMPT"
    HALLUCINATED_REFERENCE = "HALLUCINATED_REFERENCE"


@dataclass
class ContextWindowContaminationDetector:
    max_stale_ratio: float = 0.30
    max_cross_session_carryover: float = 0.15
    max_hallucinated_ratio: float = 0.05

    token_sources: dict[str, int] = field(default_factory=lambda: {s.value: 0 for s in TokenSource})
    total_tokens: int = 0
    contamination_events: list[dict] = field(default_factory=list)

    def record_tokens(self, source: TokenSource, token_count: int) -> None:
        self.token_sources[source.value] += token_count
        self.total_tokens += token_count

    def detect_contamination(self) -> dict:
        if self.total_tokens == 0:
            return {"contaminated": False, "confidence": 0.0}

        stale_ratio = self.token_sources[TokenSource.RESUME_FROM_PRIOR.value] / self.total_tokens
        carryover_ratio = max(0, stale_ratio - 0.1)
        hallucinated_ratio = self.token_sources[TokenSource.HALLUCINATED_REFERENCE.value] / max(self.total_tokens, 1)

        flags = []
        if stale_ratio > self.max_stale_ratio:
            flags.append(f"stale_context={stale_ratio:.2f}>{self.max_stale_ratio}")
        if carryover_ratio > self.max_cross_session_carryover:
            flags.append(f"cross_session_carryover={carryover_ratio:.2f}")
        if hallucinated_ratio > self.max_hallucinated_ratio:
            flags.append(f"hallucinated_refs={hallucinated_ratio:.3f}")

        contaminated = len(flags) > 0
        if contaminated:
            self.contamination_events.append(
                {
                    "ts": time.time(),
                    "flags": flags,
                    "stale_ratio": round(stale_ratio, 3),
                    "total_tokens": self.total_tokens,
                }
            )

        return {
            "contaminated": contaminated,
            "flags": flags,
            "stale_ratio": round(stale_ratio, 3),
            "carryover_ratio": round(carryover_ratio, 3),
            "hallucinated_ratio": round(hallucinated_ratio, 4),
            "recommendation": "context_refresh" if contaminated else "continue",
        }

    def get_provenance_summary(self) -> dict:
        return {
            "total_tokens": self.total_tokens,
            "sources": dict(self.token_sources),
            "contamination_count": len(self.contamination_events),
        }

    def reset_window(self) -> None:
        self.token_sources = {s.value: 0 for s in TokenSource}
        self.total_tokens = 0
