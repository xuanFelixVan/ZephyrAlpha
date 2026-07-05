# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md
# [MODULE] zephyr.security.llm_defense.llm_security.sensitivity_classifier
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_sensitivity_classifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""sensitivity_classifier.py — 数据分级 (B9, DD83, TASK-015 beta w)"""

from dataclasses import dataclass
from enum import Enum


class SensitivityLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class ClassificationResult:
    ke_id: str
    level: SensitivityLevel
    confidence: float


class SensitivityClassifier:
    """ML auto-classify KE (Public/Internal/Confidential/Restricted) (DD83)."""

    def classify(self, ke_id: str, content: str) -> ClassificationResult:
        level = SensitivityLevel.INTERNAL
        if "key" in content.lower() or "secret" in content.lower():
            level = SensitivityLevel.CONFIDENTIAL
        return ClassificationResult(ke_id=ke_id, level=level, confidence=0.7)
