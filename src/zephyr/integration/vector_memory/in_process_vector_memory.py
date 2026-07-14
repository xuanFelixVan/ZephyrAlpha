# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.in_process_vector_memory
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.vector_memory.collection_manager; zephyr.integration.local_model.embedding_router; zephyr.integration.vector_memory.chunk_strategy_router; zephyr.integration.vector_memory.provenance_enforcer; zephyr.integration.vector_memory.retrieval_feedback; zephyr.integration.local_model.cache_layer; zephyr.integration.vector_memory.hybrid_retriever; zephyr.integration.vector_memory.index_health_monitor; zephyr.integration.vector_memory.bridge_layer; zephyr.integration.vector_memory.vector_bridge; zephyr.integration.vector_memory.in_memory_memory_backend
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
# [A_module] module_id=MOD-INT_in_process_vector_memory | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
InProcessVectorMemory — MOD-INF-011 VMS 统一入口
===================================================
蓝图 §6 架构分层 · Phase 1-4 施工 · 11 子模块组装

架构
----
    InProcessVectorMemory (统一入口)
    ├── CollectionManager        ← 8 Collection 生命周期
    │   ├── decisions / code_context / lessons / knowledge
    │   ├── rules / blueprints / session_snapshots / execution_traces
    ├── EmbeddingRouter          ← 双模型路由 (Phase 1)
    ├── ChunkStrategyRouter      ← 分块策略调度 (Phase 1)
    ├── HybridRetriever          ← Vector+BM25+RRF (Phase 3)
    ├── ProvenanceEnforcer       ← WriteTrace强制 (Phase 1)
    ├── IndexHealthMonitor       ← 自检+自动修复 (Phase 1)
    ├── RetrievalFeedback        ← FLE检索质量消费 (Phase 3)
    ├── CacheLayer               ← Embedding memoization (Phase 1)
    ├── BridgeLayer              ← kb/ ↔ VMS 桥接 (Phase 1)
    ├── VectorBridge             ← CE/KB 外部集成 (Phase 1)
    └── InMemoryMemoryBackend    ← 降级兜底 (Phase 1)
"""

from __future__ import annotations

import logging
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from zephyr.integration.local_model.embedding_router import EmbeddingRouter

if TYPE_CHECKING:
    from zephyr.integration.local_model.cache_layer import CacheLayer
    from zephyr.integration.local_model.embedding_router import EmbeddingRouterProtocol
    from zephyr.integration.vector_memory.bridge_layer import BridgeLayer
    from zephyr.integration.vector_memory.chunk_strategy_router import ChunkStrategyRouter
    from zephyr.integration.vector_memory.in_memory_memory_backend import InMemoryMemoryBackend
    from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer
    from zephyr.integration.vector_memory.retrieval_feedback import RetrievalFeedback
    from zephyr.integration.vector_memory.vector_bridge import VectorBridge

from zephyr.integration.vector_memory.collection_manager import (
    COLLECTION_NAMES,
    VMS_PERSIST_DIR,
    CollectionInfo,
    CollectionManager,
)

_logger = logging.getLogger(__name__)


class InProcessVectorMemory:
    COLLECTION_NAMES: ClassVar[tuple[str, ...]] = COLLECTION_NAMES
    VMS_PERSIST_DIR: ClassVar[Path] = VMS_PERSIST_DIR

    def __init__(
        self,
        persist_dir: Path | str | None = None,
        embedding_router: EmbeddingRouterProtocol | None = None,
    ) -> None:
        self._started: bool = False
        self._embedding_router = embedding_router if embedding_router is not None else EmbeddingRouter()
        self._collection_manager = CollectionManager(persist_dir=persist_dir, embedding_router=self._embedding_router)
        self._chunk_strategy_router: Any = self._init_chunk_router()
        self._hybrid_retriever: Any = None
        self._provenance_enforcer = self._init_provenance_enforcer()
        self._index_health_monitor: Any = None
        self._retrieval_feedback = self._init_retrieval_feedback()
        self._cache_layer = self._init_cache_layer()
        self._bridge_layer: Any | None = None
        self._vector_bridge: Any | None = None
        self._in_memory_backend: Any | None = None
        self._stop_event = threading.Event()
        self._maintenance_thread: threading.Thread | None = None

    @staticmethod
    def _init_chunk_router() -> ChunkStrategyRouter:
        from zephyr.integration.vector_memory.chunk_strategy_router import ChunkStrategyRouter

        return ChunkStrategyRouter()

    @staticmethod
    def _init_provenance_enforcer() -> ProvenanceEnforcer:
        from zephyr.integration.vector_memory.provenance_enforcer import ProvenanceEnforcer

        return ProvenanceEnforcer()

    @staticmethod
    def _init_retrieval_feedback() -> RetrievalFeedback:
        from zephyr.integration.vector_memory.retrieval_feedback import RetrievalFeedback

        return RetrievalFeedback()

    @staticmethod
    def _init_cache_layer() -> CacheLayer:
        from zephyr.integration.local_model.cache_layer import CacheLayer

        return CacheLayer()

    @property
    def started(self) -> bool:
        return self._started

    @property
    def collection_manager(self) -> CollectionManager:
        return self._collection_manager

    @property
    def embedding_router(self) -> EmbeddingRouter:
        return self._embedding_router

    @property
    def bridge_layer(self) -> BridgeLayer | None:
        return self._bridge_layer

    @property
    def vector_bridge(self) -> VectorBridge | None:
        return self._vector_bridge

    @property
    def persist_dir(self) -> Path:
        return self._collection_manager.persist_dir

    def start(self) -> None:
        if self._started:
            return
        import os

        os.environ.setdefault("CHROMA_TELEMETRY_IMPL", "none")
        os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

        self._collection_manager.persist_dir.mkdir(parents=True, exist_ok=True)

        _logger.info("VMS: ChromaDB PersistentClient -> %s (telemetry disabled)", self._collection_manager.persist_dir)

        self._embedding_router.warmup()

        from zephyr.integration.vector_memory.hybrid_retriever import HybridRetriever
        from zephyr.integration.vector_memory.index_health_monitor import IndexHealthMonitor

        self._hybrid_retriever = HybridRetriever(self._collection_manager, self._embedding_router)
        self._index_health_monitor = IndexHealthMonitor(self._collection_manager)

        from zephyr.integration.vector_memory.bridge_layer import BridgeLayer
        from zephyr.integration.vector_memory.vector_bridge import VectorBridge

        self._bridge_layer = BridgeLayer(self._collection_manager)
        self._vector_bridge = VectorBridge(self)
        # InMemoryMemoryBackend 惰性创建——仅在所有检索路径失败时才实例化（对标 Netflix Hystrix fallback 按需触发）
        self._in_memory_backend: Any | None = None

        self._started = True
        _logger.info(
            "VMS: 启动完成 (11子模块全部初始化, BGE-M3=%s, bge-small=%s)",
            self._embedding_router.bge_m3_available,
            self._embedding_router.bge_small_available,
        )

        try:
            baseline = self._index_health_monitor.inspect_all()
            _logger.info(
                "VMS: 启动后健康基线: %s/%s healthy, drift=%s",
                baseline.collections_healthy,
                baseline.collections_healthy + baseline.collections_unhealthy,
                baseline.drift_detected,
            )
        except Exception as exc:
            _logger.warning("VMS: 健康基线检查失败: %s", exc, exc_info=True)

        self._stop_event.clear()
        self._maintenance_thread = threading.Thread(target=self._maintenance_loop, daemon=True, name="vms-maintenance")
        self._maintenance_thread.start()
        _logger.info("VMS: 维护线程已启动")

    def shutdown(self) -> None:
        if not self._started:
            return
        self._stop_event.set()
        if self._maintenance_thread is not None and self._maintenance_thread.is_alive():
            self._maintenance_thread.join(timeout=5.0)
        self._embedding_router.shutdown()
        if self._collection_manager.client is not None:
            pass
        self._started = False
        _logger.info("VMS: 已停止")

    def init_all_collections(self) -> list[CollectionInfo]:
        return self._collection_manager.init_all_collections()

    def list_collections(self) -> list[CollectionInfo]:
        return self._collection_manager.list_collections()

    def get_collection(self, name: str) -> object:
        return self._collection_manager.get_collection(name=name)

    def create_collection(
        self,
        name: str,
        dim: int = 1024,
        chunk_strategy: str = "semantic",
        ttl_days: int = 0,
        ai_autonomy: str = "supervised",
    ) -> CollectionInfo:
        return self._collection_manager.create_collection(
            name=name,
            dim=dim,
            chunk_strategy=chunk_strategy,
            ttl_days=ttl_days,
            ai_autonomy=ai_autonomy,
        )

    def write(
        self,
        collection_name: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> str:
        from zephyr.integration.vector_memory.bridge_layer import COLLECTION_ALIASES
        from zephyr.integration.vector_memory.collection_manager import DesignPrinciplesEnforcer

        collection_name = COLLECTION_ALIASES.get(collection_name, collection_name)
        meta = dict(metadata or {})
        DesignPrinciplesEnforcer.validate_provenance(meta)
        return self._collection_manager.write_with_provenance(
            collection_name=collection_name,
            content=content,
            metadata=meta,
            doc_id=doc_id,
        )

    def _get_in_memory_backend(self) -> InMemoryMemoryBackend:
        """惰性创建 InMemoryMemoryBackend——仅在所有检索路径失败时才实例化。

        对标 Netflix Hystrix：fallback 按需触发，不预先创建。
        蓝图 §6.2 退化矩阵 L3 级别：双嵌入模型全不可用 -> InMemory 零向量检索。
        """
        if self._in_memory_backend is None:
            from zephyr.integration.vector_memory.in_memory_memory_backend import InMemoryMemoryBackend

            self._in_memory_backend = InMemoryMemoryBackend()
            _logger.warning("VMS: 所有检索路径失败，降级到 InMemoryMemoryBackend (L3)")
        return self._in_memory_backend

    def search(
        self,
        collection_name: str,
        query: str,
        k: int = 5,
    ) -> list[dict[str, Any]]:
        from zephyr.integration.vector_memory.bridge_layer import COLLECTION_ALIASES

        collection_name = COLLECTION_ALIASES.get(collection_name, collection_name)
        col = self._collection_manager.get_collection(collection_name)
        if col.count() == 0:
            return []

        if self._hybrid_retriever is not None and self._started:
            try:
                trace = self._hybrid_retriever.search(query, collection_name, k=k)
                hits: list[dict[str, Any]] = []
                for h in trace.hits:
                    hits.append(
                        {
                            "id": h.id,
                            "content": h.content,
                            "score": h.score,
                            "score_breakdown": h.score_breakdown,
                            "metadata": h.metadata,
                            "provenance": h.provenance,
                        }
                    )
                return hits
            except Exception:
                _logger.debug("HybridRetriever 检索失败，降级为原始 EmbeddingRouter 检索", exc_info=True)

        try:
            try:
                if (
                    self._started and self._embedding_router.bge_m3_available
                ) or self._embedding_router.bge_small_available:
                    query_embedding = self._embedding_router.embed(query, collection_name)
                    results = col.query(
                        query_embeddings=[query_embedding.tolist()],
                        n_results=min(k, col.count()),
                    )
                else:
                    results = col.query(query_texts=[query], n_results=min(k, col.count()))
            except Exception:
                results = col.query(query_texts=[query], n_results=min(k, col.count()))

            hits: list[dict[str, Any]] = []
            if results.get("ids") and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    hit: dict[str, Any] = {"id": doc_id}
                    if results.get("documents") and results["documents"][0]:
                        hit["content"] = results["documents"][0][i]
                    if results.get("distances") and results["distances"][0]:
                        hit["distance"] = results["distances"][0][i]
                    if results.get("metadatas") and results["metadatas"][0]:
                        hit["metadata"] = results["metadatas"][0][i]
                    hits.append(hit)
            return hits
        except Exception:
            _logger.warning("VMS: ChromaDB 检索全部失败，降级到 InMemoryMemoryBackend (L3)", exc_info=True)
            return self._get_in_memory_backend().search(query, k=k)

    def recall(
        self,
        collection_name: str,
        k: int = 5,
    ) -> list[dict[str, Any]]:
        from zephyr.integration.vector_memory.bridge_layer import COLLECTION_ALIASES

        collection_name = COLLECTION_ALIASES.get(collection_name, collection_name)
        col = self._collection_manager.get_collection(collection_name)
        all_data = col.get(include=["documents", "metadatas"])
        records: list[dict[str, Any]] = []
        if all_data.get("ids"):
            for i, doc_id in enumerate(all_data["ids"]):
                record: dict[str, Any] = {"id": doc_id}
                if all_data.get("documents"):
                    record["content"] = all_data["documents"][i]
                if all_data.get("metadatas"):
                    record["metadata"] = all_data["metadatas"][i]
                records.append(record)
        records.sort(key=lambda r: r.get("metadata", {}).get("written_at", ""), reverse=True)
        return records[:k]

    def health_check(self) -> dict[str, Any]:
        collections = self._collection_manager.list_collections()
        result = {
            "status": "healthy",
            "started": self._started,
            "persist_dir": str(self._collection_manager.persist_dir),
            "embedding": self._embedding_router.health_check(),
            "collections": {
                c.name: {
                    "exists": c.exists,
                    "dimension": c.dimension,
                    "chunk_strategy": c.chunk_strategy,
                    "ai_autonomy_level": c.ai_autonomy_level,
                }
                for c in collections
            },
        }
        if self._index_health_monitor is not None:
            try:
                report = self._index_health_monitor.inspect_all()
                result["index_health"] = {
                    "status": report.status,
                    "collections_healthy": report.collections_healthy,
                    "collections_unhealthy": report.collections_unhealthy,
                    "drift_detected": report.drift_detected,
                    "issues": report.issues,
                }
            except Exception as exc:
                result["index_health"] = {"error": str(exc)}
        return result

    def clear_all(self) -> None:
        from zephyr.integration.vector_memory.collection_manager import COLLECTION_SCHEMAS

        for name in COLLECTION_SCHEMAS:
            try:
                col = self._collection_manager.get_collection(name)
                if col.count() > 0:
                    all_ids = col.get()["ids"]
                    if all_ids:
                        col.delete(ids=all_ids)
            except Exception:
                _logger.debug("clear_all: 无法清空 %s", name, exc_info=True)

    def _maintenance_loop(self) -> None:
        CHECK_INTERVAL = 60
        DAILY_INTERVAL = 86400
        last_daily_ts: float = datetime.now(UTC).timestamp()

        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=CHECK_INTERVAL)
            if self._stop_event.is_set():
                break

            try:
                report = self._index_health_monitor.inspect_all()
                if report.collections_unhealthy > 0:
                    for cn in self._collection_manager.list_collections():
                        ci = cn.name if hasattr(cn, "name") else str(cn)
                        try:
                            self._index_health_monitor.auto_repair(ci)
                            _logger.info("VMS maintenance: auto_repair(%s)", ci)
                        except Exception:
                            _logger.debug("VMS maintenance: auto_repair(%s) failed", ci, exc_info=True)
            except Exception:
                _logger.debug("VMS maintenance: check_all failed", exc_info=True)

            now = datetime.now(UTC).timestamp()
            if now - last_daily_ts >= DAILY_INTERVAL:
                last_daily_ts = now
                try:
                    self._collection_manager.purge_expired()
                    _logger.info("VMS maintenance: purge_expired done")
                except Exception:
                    _logger.debug("VMS maintenance: purge_expired failed", exc_info=True)
