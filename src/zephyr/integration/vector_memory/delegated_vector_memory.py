# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.delegated_vector_memory
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.integration.vector_memory.interface
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
# [A_module] module_id=MOD-INT_delegated_vector_memory | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
DelegatedVectorMemory — VectorMemoryBase 的 RI-02 落地适配器
============================================================
将 ``VectorMemoryBase`` 映射到 ``UnifiedMemoryAPI``（Chroma / InMemory 后端），
消除「仅有 ABC、无实体实现」的审计缺口。

映射约定
--------
- ``MemoryEntry.collection`` → ``UnifiedMemoryAPI.write(..., topic=collection)``
- ``search`` → ``UnifiedMemoryAPI.search(query, k=top_k, topic=collection)``
- ``delete``：当前后端无统一 delete API → 返回 False
- ``get_collection_stats``：以 ``recall(topic=collection)`` 条数近似条目数
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from zephyr.governance.kb.unified_memory_api import UnifiedMemoryAPI, WriteTrace, get_unified_memory_api
from zephyr.integration.vector_memory.interface import MemoryEntry, VectorMemoryBase

_logger = logging.getLogger(__name__)

__all__ = ["UnifiedVectorMemoryAdapter"]


class UnifiedVectorMemoryAdapter(VectorMemoryBase):
    """以 ``UnifiedMemoryAPI`` 为后端的 ``VectorMemoryBase`` 实现。"""

    def __init__(
        self,
        api: UnifiedMemoryAPI | None = None,
        *,
        enforce_capability: bool = False,
    ) -> None:
        self._api = api or get_unified_memory_api(enforce_capability=enforce_capability)

    def store(self, entry: MemoryEntry) -> str:
        origin = str(entry.metadata.get("origin") or f"vms:{entry.entry_id[:24]}")
        chain = entry.metadata.get("audit_chain")
        if not isinstance(chain, list) or not chain:
            chain = ["VMS-ADAPTER", entry.collection]
        prov = WriteTrace(
            origin=origin, audit_chain=[str(x) for x in chain], arbitration=entry.metadata.get("arbitration")
        )
        return self._api.write(entry.collection, entry.content, prov)

    def search(self, query: str, collection: str, top_k: int = 10) -> list[MemoryEntry]:
        records = self._api.search(query, k=max(1, top_k), topic=collection or None)
        out: list[MemoryEntry] = []
        for r in records:
            ts = r.written_at or datetime.now(UTC).isoformat()
            try:
                created = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                created = datetime.now(UTC)
            out.append(
                MemoryEntry(
                    entry_id=r.chunk_id,
                    collection=r.topic,
                    content=r.content,
                    embedding=None,
                    metadata=dict(r.metadata),
                    created_at=created,
                )
            )
        return out

    def delete(self, entry_id: str, collection: str) -> bool:
        _logger.warning(
            "UnifiedVectorMemoryAdapter.delete(%r, %r): RI-02 未暴露 delete，跳过",
            entry_id,
            collection,
        )
        return False

    def get_collection_stats(self, collection: str) -> dict[str, int]:
        try:
            rows = self._api.recall(collection, k=100_000)
        except Exception as exc:
            _logger.warning("get_collection_stats recall failed: %s", exc)
            return {"entries": -1}
        return {"entries": len(rows)}
