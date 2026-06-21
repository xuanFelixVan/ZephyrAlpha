# [A_module] module_id=MOD-GOV_knowledge_freshness | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.governance.audit_orchestration.knowledge_freshness

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""知识新鲜度废止管理器（CT-KNOWLEDGE-FRESHNESS）——KE过期标记+自动失效。"""

from __future__ import annotations
from datetime import datetime, timezone

class KnowledgeFreshnessManager:
    MAX_AGE_DAYS: int = 90

    def is_stale(self, created_at: datetime) -> bool:
        age = (datetime.now(timezone.utc) - created_at).days
        return age > self.MAX_AGE_DAYS

    def should_deprecate(self, created_at: datetime) -> bool:
        return self.is_stale(created_at)
