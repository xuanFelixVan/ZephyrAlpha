# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.quality.ke_quality
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
知识质量评分契约（CT-KE-QUALITY）——KE完整性+准确性+时效性三维评分。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ke_quality.py
# 层: 算法
# - id: A1
#   name_zh: ① KnowledgeEntryQuality
#   name_en: KnowledgeEntryQuality
#   intro: class KnowledgeEntryQuality 源码 L49-L57
#   desc: 公共方法（定义序）: score, is_acceptable, needs_review；源码 L49-L57
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: KnowledgeEntryQuality
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class KnowledgeEntryQuality:
    def score(self, completeness: float, accuracy: float, timeliness: float) -> float:
        return (completeness + accuracy + timeliness) / 3.0

    def is_acceptable(self, score: float) -> bool:
        return score >= 0.7

    def needs_review(self, score: float) -> bool:
        return score < 0.5
