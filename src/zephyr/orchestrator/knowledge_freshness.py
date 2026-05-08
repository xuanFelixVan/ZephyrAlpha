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
