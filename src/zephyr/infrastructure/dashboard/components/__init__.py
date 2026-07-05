# [A_module] module_id=MOD-INF_components | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain-frontend/hmi-core/blueprint.md
# [MODULE] zephyr.infrastructure.dashboard.components
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent

__all__ = ["fitness_functions", "gate_statistics", "knowledge_overview", "olap_trend", "task_progress"]
