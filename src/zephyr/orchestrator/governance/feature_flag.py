# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.governance.feature_flag
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_feature_flag | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""FeatureFlag 管理器（CT-FEATUREFLAG-001）——CT-*运行时开关+audit_log。"""

from pydantic import BaseModel


class FeatureFlag(BaseModel):
    contract_id: str
    enabled: bool = True
    description: str = ""


class FeatureFlagManager:
    def __init__(self):
        self._flags: dict[str, FeatureFlag] = {}
        self._audit: list[dict] = []

    def set(self, contract_id: str, enabled: bool, description: str = "") -> FeatureFlag:
        flag = FeatureFlag(contract_id=contract_id, enabled=enabled, description=description)
        self._flags[contract_id] = flag
        self._audit.append({"contract_id": contract_id, "enabled": enabled, "description": description})
        return flag

    def is_enabled(self, contract_id: str) -> bool:
        # 5.38.3 修复: 未注册 flag 默认 False (安全默认原则),
        # 原代码 return True 违反灰度发布原则——新功能无需显式启用即生效
        flag = self._flags.get(contract_id)
        return flag.enabled if flag else False

    def get_all(self) -> dict[str, bool]:
        return {k: v.enabled for k, v in self._flags.items()}
