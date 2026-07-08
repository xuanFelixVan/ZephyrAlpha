# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.governance.kb.vms_memory_backend
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_vms_memory_backend | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
VMSMemoryBackend — UnifiedMemoryAPI 的 VMS 后端适配器
=====================================================
MOD-INF-011 (vector-memory) ↔ MOD-CONTEXT_ENGINE (kb) 统一桥接

功能
----
实现 MemoryBackend 协议，将 UnifiedMemoryAPI 的三件套 API
(write / recall / search) 委托给 InProcessVectorMemory 的 8 Collection。

路由策略
--------
- write(topic) -> BridgeLayer.TOPIC_TO_COLLECTION 映射到 VMS Collection
  未匹配的 topic 写入 "knowledge"（默认兜底）
- recall(topic) -> VMS.recall(collection_name)
- search(query) -> VMS.search(collection_name, query) 使用 HybridRetriever

降级链
------
VMSMemoryBackend -> InMemoryMemoryBackend
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from zephyr.governance.kb._backend_protocol import (
    InMemoryMemoryBackend,
    MemoryBackend,
    MemoryRecord,
)
from zephyr.integration.vector_memory.bridge_layer import TOPIC_TO_COLLECTION

__all__ = ["TOPIC_TO_COLLECTION", "VMSMemoryBackend"]

_logger = logging.getLogger(__name__)


class VMSMemoryBackend:
    """VMS 后端——将 UnifiedMemoryAPI 的操作路由到 InProcessVectorMemory。

    参数
    ----
    vms : InProcessVectorMemory
        已初始化的 VMS 实例（需先调用 vms.start()）。
    fallback : MemoryBackend | None
        VMS 不可用时的降级后端；None 时使用 InMemoryMemoryBackend。
    """

    def __init__(
        self,
        vms: Any | None = None,
        fallback: MemoryBackend | None = None,
    ) -> None:
        self._vms = vms
        self._fallback: MemoryBackend = fallback or InMemoryMemoryBackend()
        self._lock = threading.RLock()
        self._vms_available: bool = vms is not None

    @property
    def vms(self) -> Any:
        return self._vms

    @property
    def is_vms_available(self) -> bool:
        return self._vms_available and self._vms is not None

    def _resolve_collection(self, topic: str) -> str:
        for prefix, collection in TOPIC_TO_COLLECTION.items():
            if topic.lower().startswith(prefix.lower()):
                return collection
        return "knowledge"

    def _try_vms_write(self, record: MemoryRecord) -> str | None:
        if not self.is_vms_available:
            return None
        collection = self._resolve_collection(record.topic)
        metadata = dict(record.metadata)
        metadata["topic"] = record.topic
        metadata["written_at"] = record.written_at
        try:
            chunk_id = self._vms.write(
                collection_name=collection,
                content=record.content,
                metadata=metadata,
                doc_id=record.chunk_id,  # 治本：用确定性业务 id 替代 uuid（修复丢弃 record.chunk_id 的 bug）
            )
            return chunk_id
        except Exception as exc:
            _logger.warning("VMSMemoryBackend.write fallback: VMS write failed: %s", exc, exc_info=True)
            self._vms_available = False
            return None

    def write(self, record: MemoryRecord) -> str:
        with self._lock:
            chunk_id = self._try_vms_write(record)
            if chunk_id is not None:
                return chunk_id
            return self._fallback.write(record)

    def list_by_topic(self, topic: str, k: int) -> list[MemoryRecord]:
        with self._lock:
            if not self.is_vms_available:
                return self._fallback.list_by_topic(topic, k)
            collection = self._resolve_collection(topic)
            try:
                # 先按 topic where 过滤再取 k。
                # 旧实现调 vms.recall(k=k) 取 collection 最近 k 条再过滤，
                # topic 不在最近 k 条时返回空，导致 recall(topic, 小k) 误报数据丢失。
                col = self._vms.get_collection(collection)
                raw = col.get(where={"topic": topic}, include=["documents", "metadatas"])
                records: list[MemoryRecord] = []
                ids = raw.get("ids") or []
                docs = raw.get("documents") or []
                metas = raw.get("metadatas") or []
                for chunk_id, doc, meta in zip(ids, docs, metas, strict=False):
                    meta = meta or {}
                    records.append(
                        MemoryRecord(
                            chunk_id=chunk_id,
                            topic=str(meta.get("topic", topic)),
                            content=doc or "",
                            score=1.0,
                            written_at=str(meta.get("written_at", "")),
                            metadata={kk: vv for kk, vv in meta.items() if kk not in {"topic", "written_at"}},
                        )
                    )
                records.sort(key=lambda r: r.written_at, reverse=True)
                return records[: max(0, k)]
            except Exception as exc:
                _logger.warning("VMSMemoryBackend.list_by_topic fallback: %s", exc, exc_info=True)
                return self._fallback.list_by_topic(topic, k)

    def query(self, query_text: str, k: int, topic: str | None = None) -> list[MemoryRecord]:
        with self._lock:
            if not self.is_vms_available:
                return self._fallback.query(query_text, k, topic)
            collection = self._resolve_collection(topic) if topic else "knowledge"
            try:
                raw_results = self._vms.search(
                    collection_name=collection,
                    query=query_text,
                    k=k,
                )
                records: list[MemoryRecord] = []
                for item in raw_results:
                    meta = item.get("metadata", {}) or {}
                    rec_topic = meta.get("topic", topic or "")
                    if topic is not None and rec_topic != topic:
                        continue
                    records.append(
                        MemoryRecord(
                            chunk_id=item.get("id", ""),
                            topic=rec_topic,
                            content=item.get("content", item.get("document", "")),
                            score=float(item.get("score", 0.0)),
                            written_at=meta.get("written_at", ""),
                            metadata={kk: vv for kk, vv in meta.items() if kk not in {"topic", "written_at"}},
                        )
                    )
                return records[: max(0, k)]
            except Exception as exc:
                _logger.warning("VMSMemoryBackend.query fallback: %s", exc, exc_info=True)
                return self._fallback.query(query_text, k, topic)

    def count(self) -> int:
        if not self.is_vms_available:
            return self._fallback.count()
        try:
            health = self._vms.health_check()
            total = 0
            collections_info = health.get("collections", {})
            for col_info in collections_info.values():
                if isinstance(col_info, dict):
                    total += col_info.get("count", 0)
            return total
        except Exception:
            return self._fallback.count()


def create_vms_backend(
    *,
    vms_persist_dir: str | None = None,
    fallback: MemoryBackend | None = None,
) -> VMSMemoryBackend:
    """工厂函数——创建 VMSMemoryBackend（含 VMS 初始化 + 降级保护）。

    参数
    ----
    vms_persist_dir : str | None
        VMS 持久化目录；None 使用 VMS 默认路径。
    fallback : MemoryBackend | None
        降级后端；None 使用 InMemoryMemoryBackend。

    返回
    ----
    VMSMemoryBackend
        已初始化的 VMS 后端（VMS 不可用时自动降级）。
    """
    try:
        from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory

        vms = InProcessVectorMemory(persist_dir=vms_persist_dir)
        vms.start()
        _logger.info("VMSMemoryBackend: VMS initialized successfully")
        return VMSMemoryBackend(vms=vms, fallback=fallback)
    except Exception as exc:
        _logger.warning("VMSMemoryBackend: VMS init failed, using fallback: %s", exc, exc_info=True)
        return VMSMemoryBackend(vms=None, fallback=fallback)
