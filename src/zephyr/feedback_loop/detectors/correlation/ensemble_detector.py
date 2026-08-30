# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation.ensemble_detector
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
Ensemble Detector — v0.4.0 R21

Blindspot: Single anomaly detection method misses multi-modal anomalies.
Risk: R21 — False negatives on anomalies detectable only by ensemble voting.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ensemble_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① EnsembleDetector
#   name_en: EnsembleDetector
#   intro: class EnsembleDetector 源码 L55-L59
#   desc: 公共方法（定义序）: vote；源码 L55-L59
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: EnsembleDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class EnsembleDetector:
    detectors: list[str] = field(default_factory=list)

    def vote(self, scores: dict[str, float]) -> bool:
        return sum(1 for v in scores.values() if v > 2.5) > len(scores) // 2
