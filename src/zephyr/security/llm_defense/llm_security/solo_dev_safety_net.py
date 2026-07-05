# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md
# [MODULE] zephyr.security.llm_defense.llm_security.solo_dev_safety_net
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_solo_dev_safety_net | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""solo_dev_safety_net.py — 单人无审查安全网 (B15, DD89, TASK-017)"""

from dataclasses import dataclass


@dataclass
class SafetyNetCheck:
    task_id: str
    is_p0: bool
    confirmation_needed: bool
    context_summary: str
    timeout_auto_proceed: bool = False


class SoloDevSafetyNet:
    """P0 task injection confirmation gate + 5min timeout auto-proceed (DD89)."""

    def check_injection(self, task_id: str, priority: str, context_preview: str) -> SafetyNetCheck:
        is_p0 = priority.upper() == "P0"
        return SafetyNetCheck(
            task_id=task_id,
            is_p0=is_p0,
            confirmation_needed=is_p0,
            context_summary=context_preview[:200],
        )
