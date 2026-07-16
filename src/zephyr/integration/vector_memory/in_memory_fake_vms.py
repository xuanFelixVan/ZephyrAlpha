# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.in_memory_fake_vms
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.vector_memory.collection_manager
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
# [A_module] module_id=MOD-INF-011 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双胞胎
===================================================
蓝图 §7 · TASK-INF-0220 R3 · 单元测试隔离而不用真实 ChromaDB

所有方法签名与 InProcessVectorMemory 完全一致
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, ClassVar

from zephyr.integration.vector_memory.collection_manager import COLLECTION_NAMES


class InMemoryFakeVMS:
    COLLECTION_NAMES: ClassVar[tuple[str, ...]] = COLLECTION_NAMES

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        self._started: bool = True

    @property
    def started(self) -> bool:
        return self._started

    def start(self) -> None:
        self._started = True

    def shutdown(self) -> None:
        self._started = False
        self._store.clear()

    def write(self, collection_name: str, content: str, metadata: dict[str, Any] | None = None) -> str:
        if collection_name not in self.COLLECTION_NAMES:
            raise KeyError(f"未知 Collection: {collection_name}")
        doc_id = f"fake::{collection_name}::{datetime.now(UTC).strftime('%Y%m%dT%H%M%S')}::{uuid.uuid4().hex[:8]}"
        self._store[doc_id] = {
            "collection": collection_name,
            "content": content,
            "metadata": dict(metadata or {}),
        }
        return doc_id

    def search(self, collection_name: str, query: str, k: int = 5) -> list[dict[str, Any]]:
        hits: list[dict[str, Any]] = []
        for doc_id, data in self._store.items():
            if data["collection"] == collection_name:
                if query.lower() in data["content"].lower():
                    hits.append(
                        {
                            "id": doc_id,
                            "content": data["content"],
                            "distance": 0.1,
                            "metadata": data.get("metadata", {}),
                        }
                    )
        return hits[:k]

    def recall(self, collection_name: str, k: int = 5) -> list[dict[str, Any]]:
        hits: list[dict[str, Any]] = []
        for doc_id, data in self._store.items():
            if data["collection"] == collection_name:
                hits.append(
                    {
                        "id": doc_id,
                        "content": data["content"],
                        "metadata": data.get("metadata", {}),
                    }
                )
        return hits[-k:]

    def health_check(self) -> dict[str, Any]:
        return {"status": "healthy", "mode": "fake", "stored": len(self._store)}
