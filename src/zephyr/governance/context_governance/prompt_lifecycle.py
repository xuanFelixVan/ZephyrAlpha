# [BLUEPRINT] SRC-029 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.context_governance.prompt_lifecycle
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.context_governance.__init__
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
# [A_module] module_id=MOD-GOV_prompt_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromptVersion:
    prompt_id: str
    semantic_version: str
    prompt_text: str


PROMPT_REGRESSION_THRESHOLD: float = 0.05
PROMPT_STORE: dict[str, PromptVersion] = {}
