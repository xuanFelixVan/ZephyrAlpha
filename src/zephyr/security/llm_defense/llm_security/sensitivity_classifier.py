# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md
# [MODULE] zephyr.security.llm_defense.llm_security.sensitivity_classifier
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-LLM_SECURITY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
sensitivity_classifier.py — 数据分级 (B9, DD83, TASK-015 beta w)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: sensitivity_classifier.py
# 层: 算法
# - id: A1
#   name_zh: ① SensitivityClassifier
#   name_en: SensitivityClassifier
#   intro: ML auto-classify KE (Public/Internal/Confidential/Restricte…
#   desc: ML auto-classify KE (Public/Internal/Confidential/Restricted) (DD83).；公共方法（定义序）: classify；源码 L67-L74
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: SensitivityClassifier
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
