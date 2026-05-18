# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.evolution.failure_replay

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Failure Replay — v0.7.0 R77

Blindspot: Past failures not replayed for training.
Risk: R77 — FLE forgets failure patterns; repeats same mistakes.
"""
from dataclasses import dataclass, field

@dataclass
class FailureReplay:
    failures: list[dict] = field(default_factory=list)

    def record(self, failure: dict) -> None:
        self.failures.append(failure)
