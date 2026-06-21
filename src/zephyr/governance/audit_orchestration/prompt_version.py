# [A_module] module_id=MOD-GOV_prompt_version | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.governance.audit_orchestration.prompt_version

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""AI Prompt 版本控制（CT-PROMPT-VERSION）——prompt template版本化+部署前diff。"""

from __future__ import annotations

class PromptVersionManager:
    def __init__(self):
        self._versions: dict[str, str] = {}

    def register(self, prompt_id: str, version: str, template: str) -> None:
        self._versions[prompt_id] = version

    def get_version(self, prompt_id: str) -> str:
        return self._versions.get(prompt_id, "v0.0.0")

    def diff(self, prompt_id: str, old_template: str, new_template: str) -> bool:
        return old_template != new_template
