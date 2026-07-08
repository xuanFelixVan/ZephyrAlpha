# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.model_version_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 模型版本突变必须检测;KL divergence阈值不可手动覆盖
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_model_version_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Model Version Detector — v0.10.0 模型版本突变检测: model version change->degraded auto_guard。
"""

from __future__ import annotations


class ModelVersionDetector:
    def __init__(self):
        self._known_versions: dict[str, str] = {}

    def record_version(self, model_id: str, version: str):
        self._known_versions[model_id] = version

    def detect_change(self, model_id: str, current_version: str) -> bool:
        known = self._known_versions.get(model_id)
        return known is not None and known != current_version

    def should_degrade(self, model_id: str, current_version: str) -> bool:
        return self.detect_change(model_id, current_version)
