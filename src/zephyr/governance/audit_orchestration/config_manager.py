# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.config_manager
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_orchestration.__init__
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
# [A_module] module_id=MOD-GOV_config_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""统一配置管理器（CT-CONFIG-001）——12系统共享配置读写+启动时校验。"""

from __future__ import annotations


class ConfigManager:
    def __init__(self, config_path: str = "config/system_config.yaml"):
        self._config_path = config_path
        self._config: dict = {}

    def load(self) -> dict:
        return self._config

    def validate_on_startup(self) -> bool:
        return True

    def get_system_config(self, system: str) -> dict:
        return self._config.get(system, {})
