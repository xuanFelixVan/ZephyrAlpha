# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.evolution.semantic_intent_preservation_guard
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_semantic_intent_preservation_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R505: SemanticIntentPreservationGuard
自修改语义意图保真校验 — cosine similarity 检测意图漂移
"""

import math
from dataclasses import dataclass, field


@dataclass
class SemanticIntentPreservationGuard:
    pre_modification_embedding: list[float] | None = None
    pre_modification_hash: str = ""
    drift_threshold: float = 0.15
    modifications_log: list[dict] = field(default_factory=list)
    max_log_size: int = 100

    def snapshot_pre_state(self, behavior_vector: list[float], intent_hash: str) -> None:
        self.pre_modification_embedding = list(behavior_vector)
        self.pre_modification_hash = intent_hash

    def verify_post_state(self, post_vector: list[float], post_hash: str) -> dict:
        if not self.pre_modification_embedding:
            return {"status": "no_baseline", "drift_detected": False}

        cosine_sim = self._cosine_similarity(self.pre_modification_embedding, post_vector)
        drift = 1.0 - cosine_sim
        hash_changed = self.pre_modification_hash != post_hash

        severity = "safe"
        if drift > 0.3:
            severity = "critical_drift"
        elif drift > self.drift_threshold:
            severity = "semantic_drift"

        entry = {
            "pre_hash": self.pre_modification_hash,
            "post_hash": post_hash,
            "cosine_similarity": round(cosine_sim, 4),
            "drift": round(drift, 4),
            "severity": severity,
            "hash_changed": hash_changed,
        }
        self.modifications_log.append(entry)
        if len(self.modifications_log) > self.max_log_size:
            self.modifications_log = self.modifications_log[-self.max_log_size :]

        self.pre_modification_embedding = None
        self.pre_modification_hash = ""

        return {
            **entry,
            "drift_detected": drift > self.drift_threshold,
            "recommendation": "BLOCK"
            if severity == "critical_drift"
            else "REVIEW"
            if severity == "semantic_drift"
            else "ALLOW",
        }

    def get_drift_history(self) -> list[dict]:
        return [e for e in self.modifications_log if e["drift"] > self.drift_threshold]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b) or len(a) == 0:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a < 1e-10 or norm_b < 1e-10:
            return 0.0
        return dot / (norm_a * norm_b)
