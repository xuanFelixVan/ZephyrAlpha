# [BLUEPRINT] MOD-KNOWLEDGE | (pending)
# [MODULE] zephyr.knowledge
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-KNOWLEDGE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""zephyr.knowledge — D_KNOWLEDGE 域包门面（MOD-KNOWLEDGE）。

P2W03 DIGEST 波3 四件套（MOD-KNW-001/002/003/004）守卫式导入（目标类落地即
自愈，缺载不致包门面断链），与 data_eng 包门面同模式在案；本批只导出这
4 个类，后续波次他人追加。
"""

try:
    from zephyr.knowledge.kb_engine import KbEngine
except ImportError:
    KbEngine = None  # type: ignore[assignment]
try:
    from zephyr.knowledge.knowledge_quality_assessor import KnowledgeQualityAssessor
except ImportError:
    KnowledgeQualityAssessor = None  # type: ignore[assignment]
try:
    from zephyr.knowledge.financial_knowledge_graph import FinancialKnowledgeGraph
except ImportError:
    FinancialKnowledgeGraph = None  # type: ignore[assignment]
try:
    from zephyr.knowledge.knowledge_artifact_store import KnowledgeArtifactStore
except ImportError:
    KnowledgeArtifactStore = None  # type: ignore[assignment]

__all__ = []

__all__.append("KbEngine")

__all__.append("KnowledgeQualityAssessor")

__all__.append("FinancialKnowledgeGraph")

__all__.append("KnowledgeArtifactStore")
