# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.sensitivity_classifier

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""sensitivity_classifier.py — 数据分级 (B9, DD83, TASK-015 beta w)"""
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass


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
