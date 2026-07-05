# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.cross_collection_retriever
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.vector_memory.__init__
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
# [A_module] module_id=MOD-INT_cross_collection_retriever | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CrossCollectionRetriever — MOD-INF-011 跨 Collection 联合检索
===============================================================
蓝图 §3 · §6 · 多 Collection 并行检索 → 聚合 → 重排序

策略
----
- knead(): 跨 Collection 查询，各取 k*2 候选 → RRF 再融合
- context_assembly(): 多 Collection 结果拼接 + dedup
"""

from __future__ import annotations

import logging
from typing import Any

_logger = logging.getLogger(__name__)


class CrossCollectionRetriever:
    def __init__(self, hybrid_retriever: Any) -> None:
        self._hybrid_retriever = hybrid_retriever

    def knead(
        self,
        query: str,
        collections: list[str],
        k: int = 5,
    ) -> list[dict[str, Any]]:
        all_hits: list[dict[str, Any]] = []
        for col_name in collections:
            try:
                trace = self._hybrid_retriever.search(query, col_name, k=max(k, 3))
                for hit in trace.hits:
                    all_hits.append(
                        {
                            "id": hit.id,
                            "content": hit.content,
                            "score": hit.score,
                            "collection": col_name,
                            "metadata": hit.metadata,
                        }
                    )
            except Exception as e:
                _logger.debug("CrossCollectionRetriever: %s 检索失败: %s", col_name, e, exc_info=True)

        all_hits.sort(key=lambda x: x["score"], reverse=True)
        return all_hits[:k]

    def context_assembly(self, query: str, collections: list[str]) -> str:
        results = self.knead(query, collections, k=3)
        parts: list[str] = []
        for r in results:
            parts.append(f"[{r['collection']}] {r['content']}")
        return "\n\n".join(parts)
