# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.in_memory_memory_backend
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INT_in_memory_memory_backend | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
InMemoryMemoryBackend — MOD-INF-011 降级兜底
=============================================
蓝图 §6 · V-VMS-505/507 · ChromaDB + 双模型全不可用时的最后防线

特性
----
- 零向量 placeholder（dtype=float32）
- degraded=True 标记——告知消费方结果不可信
- 极简内存 dict 存储（write/recall/search 兼容接口）
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, ClassVar

import numpy as np

_logger = logging.getLogger(__name__)


class InMemoryMemoryBackend:
    DEFAULT_DIM: ClassVar[int] = 512

    def __init__(self, dim: int = DEFAULT_DIM) -> None:
        self._dim = dim
        self._store: dict[str, dict[str, Any]] = {}
        self._degraded = True
        _logger.warning("InMemoryMemoryBackend: 进入降级模式 (%dd degraded=True)", dim)

    @property
    def degraded(self) -> bool:
        return self._degraded

    @property
    def dim(self) -> int:
        return self._dim

    def write(self, content: str, metadata: dict[str, Any] | None = None) -> str:
        import uuid

        doc_id = f"im::{datetime.now(UTC).strftime('%Y%m%dT%H%M%S')}::{uuid.uuid4().hex[:12]}"
        self._store[doc_id] = {
            "content": content,
            "metadata": dict(metadata or {}),
            "vector": np.zeros(self._dim, dtype=np.float32),
            "degraded": True,
            "written_at": datetime.now(UTC).isoformat(),
        }
        return doc_id

    def search(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        ids = list(self._store.keys())[-k:]
        return [
            {
                "id": doc_id,
                "content": self._store[doc_id]["content"],
                "metadata": self._store[doc_id]["metadata"],
                "degraded": True,
            }
            for doc_id in ids
        ]

    def recall(self, k: int = 5) -> list[dict[str, Any]]:
        ids = sorted(
            self._store.keys(),
            key=lambda x: self._store[x].get("written_at", ""),
            reverse=True,
        )[:k]
        return [
            {
                "id": doc_id,
                "content": self._store[doc_id]["content"],
                "metadata": self._store[doc_id]["metadata"],
                "degraded": True,
            }
            for doc_id in ids
        ]

    def health_check(self) -> dict[str, Any]:
        return {
            "mode": "in_memory",
            "degraded": self._degraded,
            "dim": self._dim,
            "stored": len(self._store),
        }

    def clear(self) -> None:
        self._store.clear()
