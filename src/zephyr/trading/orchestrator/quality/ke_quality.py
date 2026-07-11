# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.quality.ke_quality
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
# [A_module] module_id=MOD-ORC_ke_quality | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""知识质量评分契约（CT-KE-QUALITY）——KE完整性+准确性+时效性三维评分。"""


class KnowledgeEntryQuality:
    def score(self, completeness: float, accuracy: float, timeliness: float) -> float:
        return (completeness + accuracy + timeliness) / 3.0

    def is_acceptable(self, score: float) -> bool:
        return score >= 0.7

    def needs_review(self, score: float) -> bool:
        return score < 0.5
