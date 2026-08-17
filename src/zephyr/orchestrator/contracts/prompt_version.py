# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.contracts.prompt_version
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AI Prompt 版本控制（CT-PROMPT-VERSION）——prompt template版本化+部署前diff。"""


class PromptVersionManager:
    def __init__(self):
        self._versions: dict[str, str] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def versions(self) -> dict[str, str]:
        """只读：versions（Stage 4 公共化）。"""
        return self._versions

    @versions.setter
    def versions(self, value):
        """写入：versions（Stage 4 公共化）。"""
        self._versions = value

    def register(self, prompt_id: str, version: str, template: str) -> None:
        self._versions[prompt_id] = version

    def get_version(self, prompt_id: str) -> str:
        return self._versions.get(prompt_id, "v0.0.0")

    def diff(self, prompt_id: str, old_template: str, new_template: str) -> bool:
        return old_template != new_template
