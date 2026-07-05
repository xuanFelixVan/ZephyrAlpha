# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.contracts.prompt_version
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_prompt_version | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AI Prompt 版本控制（CT-PROMPT-VERSION）——prompt template版本化+部署前diff。"""


class PromptVersionManager:
    def __init__(self):
        self._versions: dict[str, str] = {}

    def register(self, prompt_id: str, version: str, template: str) -> None:
        self._versions[prompt_id] = version

    def get_version(self, prompt_id: str) -> str:
        return self._versions.get(prompt_id, "v0.0.0")

    def diff(self, prompt_id: str, old_template: str, new_template: str) -> bool:
        return old_template != new_template
