# [A_module] module_id=MOD-GOV_prompt_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-029 | docs/03_modules/_domain-governance/blueprint.md | §

# [MODULE] zephyr.governance.prompt_lifecycle

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromptVersion:
    prompt_id: str
    semantic_version: str
    prompt_text: str


PROMPT_REGRESSION_THRESHOLD: float = 0.05
PROMPT_STORE: dict[str, PromptVersion] = {}
