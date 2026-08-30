# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.anomaly.log_anomaly
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
Log Anomaly Detector — v0.6.0 R61

Blindspot: Structured log anomalies invisible to metric-only detection.
Risk: R61 — Error log spikes undetected while CPU/memory look normal.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: log_anomaly.py
# 层: 算法
# - id: A1
#   name_zh: ① LogAnomaly
#   name_en: LogAnomaly
#   intro: class LogAnomaly 源码 L55-L59
#   desc: 公共方法（定义序）: check；源码 L55-L59
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: LogAnomaly
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class LogAnomaly:
    error_rate_threshold: float = 0.05

    def check(self, error_rate: float) -> bool:
        return error_rate > self.error_rate_threshold
