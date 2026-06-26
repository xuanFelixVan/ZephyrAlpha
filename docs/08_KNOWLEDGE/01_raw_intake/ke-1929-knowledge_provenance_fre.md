---
module_id: KE-1838
status: active
title: 2.251 Knowledge Provenance Freshness Scorer - knowledge_provenance_freshness.py
category: module_blueprint
ttl: permanent
---

# 2.251 Knowledge Provenance Freshness Scorer - knowledge_provenance_freshness.py

2.251 Knowledge Provenance Freshness Scorer - knowledge_provenance_freshness.py (🆕 v0.23.0 - 盲点300 — KB条目的原始上下文可能已完全过时→但KB仍当作有效知识使用)

**致命问题**：FLE的KB累积了大量的知识条目。但知识随时间贬值。"2025-03-05: connection_pool_size调整策略"——这个knowledge是在2025年的架构下学到的。到了2026年，系统架构完全变了（order_router用gRPC替代了HTTP）→这个knowledge不仅无用、甚至有害。KB有"何时学到了什么"的provenance metadata，但从未有"这个provenance现在还有多相关"的新鲜度评分。这是比data_freshness_weighting（管道数据鲜度）更深一层的问题——知识本身的语义新鲜度。
**对标**：Google Knowledge Graph Temporal Freshness + Wikidata Temporal Qualifiers + Wikipedia Citation Rot Detection + Palantir Foundry Ontology Freshness + Semantic Web Temporal RDF

```python
@dataclass
class ProvenanceFreshnessScore:
    kb_entry_id: str
    knowledge_created_at: datetime
    source_system_version: str      # 知识产生时系统的版本
    source_architecture_hash: str   # 架构签名
    current_architecture_hash: str  # 当前架构签名
    architecture_divergence: float  # 架构偏离度 (0=identical, 1=completely different)
    source_regime: str              # 知识产生时的市场状态
    source_data_model_version: str
    semantic_freshness: float       # 综合新鲜度 0(完全过时)-1(完全新鲜)
    recommendation: str             # "ACTIVE"|"DEPRECATE"|"RETIRE_IMMEDIATELY"

class KnowledgeProvenanceFreshnessScorer:
    RETIREMENT_THRESHOLD: float = 0.15     # <0.15 → RETIRE_IMMEDIATELY
    DEPRECATION_THRESHOLD: float = 0.40    # <0.40 → DEPRECATE
    FRESHNESS_CHECK_INTERVAL_DAYS: int = 30

    async def score_all_kb_provenance_freshness(self) -> ProvenanceHealthReport:
        entries = await self.kb.get_all_entries()
        scores = []
        for entry in entries:
            arch_div = await self._compute_architecture_divergence(
                entry.provenance.system_version, entry.provenance.architecture_hash)
            temporal_decay = await self._compute_temporal_decay_factor(entry.provenance.created_at)
            regime_validity = await self._check_regime_relevance(entry.provenance.source_regime)
            freshness = 1.0 / (1.0 + arch_div * 0.5 + (1.0 - temporal_decay) * 0.3 + (1.0 - regime_validity) * 0.2)
            rec = ("RETIRE_IMMEDIATELY" if freshness < self.RETIREMENT_THRESHOLD
                   else "DEPRECATE" if freshness < self.DEPRECATION_THRESHOLD else "ACTIVE")
            scores.append(ProvenanceFreshnessScore(
                kb_entry_id=entry.id,
                knowledge_created_at=entry.provenance.created_at,
                source_system_version=entry.provenance.system_version,
                source_architecture_hash=entry.provenance.architecture_hash,
                current_architecture_hash=self._current_architecture_hash(),
                architecture_divergence=arch_div,
                source_regime=entry.provenance.regime,
                source_data_model_version=entry.provenance.data_model_version,
                semantic_freshness=freshness,
                recommendation=rec))

        to_retire = [s for s in scores if s.recommendation == "RETIRE_IMMEDIATELY"]
        if to_retire:
            self.FLE.notify_owner("KB_P
