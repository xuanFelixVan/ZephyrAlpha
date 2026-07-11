# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.quality.knowledge_freshness
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_knowledge_freshness | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""知识新鲜度废止管理器（CT-KNOWLEDGE-FRESHNESS）——KE过期标记+自动失效。"""

from datetime import UTC, datetime


class KnowledgeFreshnessManager:
    MAX_AGE_DAYS: int = 90

    def is_stale(self, created_at: datetime) -> bool:
        age = (datetime.now(UTC) - created_at).days
        return age > self.MAX_AGE_DAYS

    def should_deprecate(self, created_at: datetime) -> bool:
        return self.is_stale(created_at)
