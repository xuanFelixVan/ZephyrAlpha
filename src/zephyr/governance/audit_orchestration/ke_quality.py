# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.ke_quality
# [DOMAIN] D-GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_orchestration.__init__
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
# [A_module] module_id=MOD-GOV_ke_quality | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""知识质量评分契约（CT-KE-QUALITY）——KE完整性+准确性+时效性三维评分。"""

from __future__ import annotations


class KnowledgeEntryQuality:
    def score(self, completeness: float, accuracy: float, timeliness: float) -> float:
        return (completeness + accuracy + timeliness) / 3.0

    def is_acceptable(self, score: float) -> bool:
        return score >= 0.7

    def needs_review(self, score: float) -> bool:
        return score < 0.5
