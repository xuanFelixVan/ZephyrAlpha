# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.quality.knowledge_freshness
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
知识新鲜度废止管理器（CT-KNOWLEDGE-FRESHNESS）——KE过期标记+自动失效。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: knowledge_freshness.py
# 层: 算法
# - id: A1
#   name_zh: ① KnowledgeFreshnessManager
#   name_en: KnowledgeFreshnessManager
#   intro: class KnowledgeFreshnessManager 源码 L51-L59
#   desc: 公共方法（定义序）: is_stale, should_deprecate；源码 L51-L59
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: KnowledgeFreshnessManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from datetime import UTC, datetime


class KnowledgeFreshnessManager:
    MAX_AGE_DAYS: int = 90

    def is_stale(self, created_at: datetime) -> bool:
        age = (datetime.now(UTC) - created_at).days
        return age > self.MAX_AGE_DAYS

    def should_deprecate(self, created_at: datetime) -> bool:
        return self.is_stale(created_at)
