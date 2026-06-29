# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain-frontend/hmi-core/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.knowledge_overview
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] zephyr.infra_ops.dashboard.components.gate_statistics
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
# [A_module] module_id=MOD-INF_knowledge_overview | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# AI-generated: T-4-07 Knowledge Overview Component
"""
KnowledgeOverviewComponent · 知识库概览（条目数/状态分布/激活率）
================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeStatusDistribution:
    status: str
    count: int = 0


@dataclass
class KnowledgeOverviewData:
    total_entries: int = 0
    activated_entries: int = 0
    activation_rate: float = 0.0
    status_distribution: list[KnowledgeStatusDistribution] = field(default_factory=list)
    category_distribution: dict[str, int] = field(default_factory=dict)


def fetch_knowledge_overview() -> KnowledgeOverviewData:
    return KnowledgeOverviewData()


def render_knowledge_overview(data: KnowledgeOverviewData) -> dict[str, Any]:
    return {
        "total_entries": data.total_entries,
        "activated_entries": data.activated_entries,
        "activation_rate": round(data.activation_rate, 4),
        "status_distribution": [{"status": d.status, "count": d.count} for d in data.status_distribution],
        "category_distribution": data.category_distribution,
    }
