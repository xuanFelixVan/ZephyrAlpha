# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.verifiers.auto_rollback
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Auto Rollback — v0.8.0 R93

Blindspot: Bad repair persists; manual rollback required.
Risk: R93 — Harmful repair keeps running because no auto-rollback.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: auto_rollback.py
# 层: 算法
# - id: A1
#   name_zh: ① AutoRollback
#   name_en: AutoRollback
#   intro: class AutoRollback 源码 L55-L57
#   desc: 公共方法（定义序）: should_rollback；源码 L55-L57
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: AutoRollback
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class AutoRollback:
    def should_rollback(self, pre_metric: float, post_metric: float) -> bool:
        return post_metric < pre_metric * 0.7
