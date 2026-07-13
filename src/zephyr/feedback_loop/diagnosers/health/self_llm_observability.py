# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.health.self_llm_observability
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_self_llm_observability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Self LLM Observability — v0.12.0 R160

Blindspot: FLE uses LLM but cannot observe LLM quality degradation.
Risk: R160 — Silent LLM quality drop corrupts all downstream diagnosis.
"""

from dataclasses import dataclass


@dataclass
class SelfLLMObservability:
    error_rate: float = 0.0
    latency_p95: float = 0.0

    def alert(self) -> bool:
        return self.error_rate > 0.05 or self.latency_p95 > 10000.0
