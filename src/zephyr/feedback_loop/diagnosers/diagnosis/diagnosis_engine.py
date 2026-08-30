# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.diagnosis.diagnosis_engine
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: diagnosis_engine.py
# 层: 算法
# - id: A1
#   name_zh: ① DiagnosisEngine
#   name_en: DiagnosisEngine
#   intro: class DiagnosisEngine 源码 L62-L79
#   desc: 公共方法（定义序）: diagnose；源码 L62-L79
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DiagnosisEngine
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Diagnosis:
    diagnosis_id: str
    root_cause: str
    confidence: float
    evidence_chain: list[str] = field(default_factory=list)


@dataclass
class DiagnosisEngine:
    def diagnose(self, anomaly_id: str, anomaly_evidence: dict[str, Any]) -> Diagnosis:
        diagnosis_id = str(uuid.uuid4())[:8]
        metric_name = anomaly_evidence.get("metric_name", "unknown")
        z_score = abs(anomaly_evidence.get("z_score", 2.5))
        root_cause = f"Elevated {metric_name} (z={z_score:.2f})"
        confidence = min(0.5 + z_score / 10.0, 0.95)
        evidence_chain = [
            f"metric={metric_name}",
            f"z_score={z_score:.2f}",
            f"confidence={confidence:.2f}",
        ]
        return Diagnosis(
            diagnosis_id=diagnosis_id,
            root_cause=root_cause,
            confidence=confidence,
            evidence_chain=evidence_chain,
        )
