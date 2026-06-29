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


def fetch_knowledge_overview(kb_repo: Any = None) -> KnowledgeOverviewData:
    data = KnowledgeOverviewData()
    if kb_repo is None:
        return data
    try:
        all_records = kb_repo.list_by_status()
        data.total_entries = len(all_records)
        activated_statuses = {"INDEXED", "VERIFIED", "ACCEPTED"}
        data.activated_entries = sum(1 for r in all_records if r.status.value in activated_statuses)
        data.activation_rate = data.activated_entries / data.total_entries if data.total_entries > 0 else 0.0
        status_counts: dict[str, int] = {}
        for r in all_records:
            s = r.status.value
            status_counts[s] = status_counts.get(s, 0) + 1
        data.status_distribution = [
            KnowledgeStatusDistribution(status=s, count=c) for s, c in sorted(status_counts.items())
        ]
        cat_counts: dict[str, int] = {}
        for r in all_records:
            cat_counts[r.category] = cat_counts.get(r.category, 0) + 1
        data.category_distribution = cat_counts
    except Exception:
        pass
    return data


def render_knowledge_overview(data: KnowledgeOverviewData) -> dict[str, Any]:
    return {
        "total_entries": data.total_entries,
        "activated_entries": data.activated_entries,
        "activation_rate": round(data.activation_rate, 4),
        "status_distribution": [{"status": d.status, "count": d.count} for d in data.status_distribution],
        "category_distribution": data.category_distribution,
    }
