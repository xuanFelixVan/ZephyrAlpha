# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.collectors.config_timeline
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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

"""Config Timeline — v0.8.0 R99

Blindspot: Config change history invisible; cannot correlate config changes with anomalies.
Risk: R99 — Post-config-change anomaly misdiagnosed as system failure.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 配置变更记录
#   fields: change dict（一次配置变更的描述）
#   code: ConfigTimeline.record
# 层: 算法
# - id: A1
#   name_zh: 变更追加留痕
#   name_en: change_append_recording
#   intro: 将变更 dict 追加到 changes 时间线列表，形成可关联异常的变更历史
#   code: ConfigTimeline.record
# 层: 输出
# - id: O1
#   name_zh: 配置变更时间线
#   name_en: config_change_timeline
#   intro: changes 列表——按到达顺序排列的变更历史
#   downstream: FLE 诊断方（变更-异常关联分析）
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class ConfigTimeline:
    changes: list[dict] = field(default_factory=list)

    def record(self, change: dict) -> None:
        self.changes.append(change)
