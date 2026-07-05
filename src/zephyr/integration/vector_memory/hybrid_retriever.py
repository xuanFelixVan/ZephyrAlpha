# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.hybrid_retriever
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.schema.schemas
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
# [A_module] module_id=MOD-INT_hybrid_retriever | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
HybridRetriever — MOD-INF-011 混合检索架构
============================================
蓝图 §3.2 · Vector(HNSW) + BM25 + RRF 融合 + score threshold

Pipeline
--------
    query → dense_search(k*3) ─┐
                                ├→ RRF fusion (k=60) → score filter(≥0.6) → top-k
    query → sparse_search(k*3) ─┘

特性
----
- RetrievalTrace 带 score_breakdown + why_top
- 查询超时机制 timeout_ms=2000
- 时间衰减权重 time_decay = e^(-decay_rate·age_days)
- 可插拔 reranker 预留接口 (Phase 3)
"""

from __future__ import annotations

import logging
import math
import threading
import time
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG

_logger = logging.getLogger(__name__)

RRF_K: int = 60
DEFAULT_SCORE_THRESHOLD: float = 0.6
DEFAULT_TIMEOUT_MS: int = 2000
RECALL_MULTIPLIER: int = 3

COLLECTION_DECAY_RATES: dict[str, float] = {
    "decisions": 0.003,
    "lessons": 0.005,
    "knowledge": 0.02,
    "rules": 0.0001,
    "code_context": 0.01,
    "blueprints": 0.001,
    "session_snapshots": 0.005,
    "execution_traces": 0.02,
}


class ScoredHit(BaseModel):
    model_config = BASE_CONFIG

    id: str = ""
    content: str = ""
    score: float = 0.0
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] | None = None
    partial: bool = False
    degraded: bool = False


class RetrievalTrace(BaseModel):
    model_config = BASE_CONFIG

    hits: list[ScoredHit] = Field(default_factory=list)
    collection: str = ""
    query: str = ""
    elapsed_ms: float = 0.0
    partial: bool = False
    why_top: str = ""


class BM25Index:
    def __init__(self) -> None:
        self._documents: list[dict[str, Any]] = []
        self._term_freqs: dict[str, dict[str, int]] = {}
        self._doc_freqs: dict[str, int] = {}
        self._doc_count: int = 0
        self._avg_doc_len: float = 0.0
        self._k1: float = 1.5
        self._b: float = 0.75

    def index(self, documents: list[dict[str, Any]]) -> None:
        self._documents = documents
        self._term_freqs.clear()
        self._doc_freqs.clear()
        self._doc_count = len(documents)
        total_len = 0

        for doc in documents:
            content = doc.get("content", "")
            tokens = self._tokenize(content)
            total_len += len(tokens)
            seen: set[str] = set()
            for token in tokens:
                if token not in self._term_freqs:
                    self._term_freqs[token] = {}
                self._term_freqs[token][doc["id"]] = self._term_freqs[token].get(doc["id"], 0) + 1
                if token not in seen:
                    self._doc_freqs[token] = self._doc_freqs.get(token, 0) + 1
                    seen.add(token)

        self._avg_doc_len = total_len / max(self._doc_count, 1)

    def search(self, query: str, k: int = 15) -> list[tuple[str, float]]:
        query_tokens = self._tokenize(query)
        scores: dict[str, float] = {}

        for token in query_tokens:
            df = self._doc_freqs.get(token, 0)
            if df == 0:
                continue
            idf = math.log((self._doc_count - df + 0.5) / (df + 0.5) + 1.0)
            for doc_id, tf in self._term_freqs.get(token, {}).items():
                doc = next((d for d in self._documents if d["id"] == doc_id), None)
                doc_len = len(self._tokenize(doc["content"])) if doc else 0
                numerator = tf * (self._k1 + 1)
                denominator = tf + self._k1 * (1 - self._b + self._b * doc_len / max(self._avg_doc_len, 1))
                scores[doc_id] = scores.get(doc_id, 0.0) + idf * numerator / denominator

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:k]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        import re

        tokens = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z0-9_]+", text.lower())
        return [t for t in tokens if len(t) > 0]


class HybridRetriever:
    def __init__(
        self,
        collection_manager: Any,
        embedding_router: Any,
    ) -> None:
        self._collection_manager = collection_manager
        self._embedding_router = embedding_router
        self._bm25_indexes: dict[str, BM25Index] = {}
        self._lock = threading.Lock()

    def _get_or_build_bm25(self, collection_name: str) -> BM25Index:
        if collection_name not in self._bm25_indexes:
            bm25 = BM25Index()
            all_data = self._collection_manager.get_collection(collection_name).get(include=["documents", "metadatas"])
            documents: list[dict[str, Any]] = []
            if all_data.get("ids"):
                for i, doc_id in enumerate(all_data["ids"]):
                    documents.append(
                        {
                            "id": doc_id,
                            "content": all_data.get("documents", [""] * len(all_data["ids"]))[i]
                            if all_data.get("documents")
                            else "",
                            "metadata": all_data.get("metadatas", [{}] * len(all_data["ids"]))[i]
                            if all_data.get("metadatas")
                            else {},
                        }
                    )
            bm25.index(documents)
            with self._lock:
                self._bm25_indexes[collection_name] = bm25
        return self._bm25_indexes[collection_name]

    def _time_decay(self, metadata: dict[str, Any], collection_name: str) -> float:
        decay_rate = COLLECTION_DECAY_RATES.get(collection_name, 0.005)
        written_at = metadata.get("written_at", "")
        if not written_at:
            return 1.0
        try:
            written_dt = datetime.fromisoformat(written_at.replace("Z", "+00:00"))
            now = datetime.now(UTC)
            age_days = (now - written_dt).total_seconds() / 86400
            return math.exp(-decay_rate * age_days)
        except Exception:
            return 1.0

    def _dense_search(self, query: str, collection_name: str, k: int) -> list[tuple[str, float, dict[str, Any]]]:
        col = self._collection_manager.get_collection(collection_name)
        try:
            query_embedding = self._embedding_router.embed(query, collection_name)
            results = col.query(query_embeddings=[query_embedding.tolist()], n_results=min(k, col.count()))
        except Exception:
            results = col.query(query_texts=[query], n_results=min(k, col.count()))

        hits: list[tuple[str, float, dict[str, Any]]] = []
        if results.get("ids") and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                dist = results.get("distances", [[0.0]])[0][i] if results.get("distances") else 0.0
                score = 1.0 / (1.0 + dist)
                meta = results.get("metadatas", [[{}]])[0][i] if results.get("metadatas") else {}
                hits.append((doc_id, score, meta))
        return hits

    def _sparse_search(self, query: str, collection_name: str, k: int) -> list[tuple[str, float, dict[str, Any]]]:
        bm25 = self._get_or_build_bm25(collection_name)
        scores = bm25.search(query, k)
        col = self._collection_manager.get_collection(collection_name)
        meta_map: dict[str, dict[str, Any]] = {}
        try:
            all_data = col.get(include=["metadatas"])
            if all_data.get("ids"):
                for i, doc_id in enumerate(all_data["ids"]):
                    meta_map[doc_id] = all_data.get("metadatas", [{}])[i] if all_data.get("metadatas") else {}
        except Exception as e:
            _logger.warning("suppressed error in hybrid_retriever", exc_info=True)
        return [(doc_id, score, meta_map.get(doc_id, {})) for doc_id, score in scores]

    def _rrf_fusion(
        self,
        dense_hits: list[tuple[str, float, dict[str, Any]]],
        sparse_hits: list[tuple[str, float, dict[str, Any]]],
        collection_name: str,
        k: int = RRF_K,
    ) -> list[tuple[str, float, dict[str, float], dict[str, Any]]]:
        rrf_scores: dict[str, float] = {}
        breakdowns: dict[str, dict[str, float]] = {}

        for rank, (doc_id, dense_score, meta) in enumerate(dense_hits):
            rrf = 1.0 / (k + rank + 1)
            decay = self._time_decay(meta, collection_name)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + rrf * decay
            breakdowns[doc_id] = {"dense": dense_score, "sparse": 0.0, "rrf": 0.0}

        for rank, (doc_id, sparse_score, meta) in enumerate(sparse_hits):
            rrf = 1.0 / (k + rank + 1)
            decay = self._time_decay(meta, collection_name)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + rrf * decay
            if doc_id in breakdowns:
                breakdowns[doc_id]["sparse"] = sparse_score
            else:
                breakdowns[doc_id] = {"dense": 0.0, "sparse": sparse_score, "rrf": 0.0}

        for doc_id in breakdowns:
            breakdowns[doc_id]["rrf"] = rrf_scores.get(doc_id, 0.0)

        merged = sorted(
            [(doc_id, rrf_scores[doc_id], breakdowns.get(doc_id, {}), {}) for doc_id in rrf_scores],
            key=lambda x: x[1],
            reverse=True,
        )
        return merged

    def search(
        self,
        query: str,
        collection_name: str,
        k: int = 5,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
    ) -> RetrievalTrace:
        start_time = time.perf_counter()
        candidate_k = k * RECALL_MULTIPLIER
        partial = False

        col = self._collection_manager.get_collection(collection_name)
        col_data = col.get(include=["documents", "metadatas"])

        doc_map: dict[str, dict[str, Any]] = {}
        if col_data.get("ids"):
            for i, doc_id in enumerate(col_data["ids"]):
                doc_map[doc_id] = {
                    "content": col_data.get("documents", [""] * len(col_data["ids"]))[i]
                    if col_data.get("documents")
                    else "",
                    "metadata": col_data.get("metadatas", [{}] * len(col_data["ids"]))[i]
                    if col_data.get("metadatas")
                    else {},
                }

        try:
            dense_hits = self._dense_search(query, collection_name, candidate_k)
        except Exception:
            dense_hits = []

        try:
            sparse_hits = self._sparse_search(query, collection_name, candidate_k)
        except Exception:
            sparse_hits = []

        fused = self._rrf_fusion(dense_hits, sparse_hits, collection_name)

        filtered: list[ScoredHit] = []
        for doc_id, score, breakdown, _ in fused:
            if score < DEFAULT_SCORE_THRESHOLD:
                continue
            doc_info = doc_map.get(doc_id, {})
            provenance = doc_info.get("metadata", {}).get("provenance")
            filtered.append(
                ScoredHit(
                    id=doc_id,
                    content=doc_info.get("content", ""),
                    score=round(score, 4),
                    score_breakdown={k: round(v, 4) for k, v in breakdown.items()},
                    metadata=doc_info.get("metadata", {}),
                    provenance=provenance,
                )
            )
            if len(filtered) >= k:
                break

        elapsed = (time.perf_counter() - start_time) * 1000
        if elapsed > timeout_ms:
            partial = True

        why_keywords = set()
        for token in BM25Index._tokenize(query):
            why_keywords.add(token)
        why_top = f"matched: {', '.join(sorted(why_keywords)[:5])}"

        return RetrievalTrace(
            hits=filtered,
            collection=collection_name,
            query=query,
            elapsed_ms=round(elapsed, 2),
            partial=partial,
            why_top=why_top,
        )

    def search_with_rerank(
        self,
        query: str,
        collection_name: str,
        k: int = 5,
        reranker: Any = None,
    ) -> RetrievalTrace:
        trace = self.search(query, collection_name, k=max(k * 2, 10))
        if reranker is not None and len(trace.hits) > 0:
            pairs = [(query, h.content) for h in trace.hits]
            try:
                rerank_scores = reranker.predict(pairs)
                for i, h in enumerate(trace.hits):
                    h.score = float(rerank_scores[i]) if i < len(rerank_scores) else h.score
                trace.hits.sort(key=lambda x: x.score, reverse=True)
                trace.hits = trace.hits[:k]
            except Exception as e:
                _logger.warning("HybridRetriever: rerank 失败: %s", e)
        return trace

    def invalidate_bm25(self, collection_name: str) -> None:
        with self._lock:
            self._bm25_indexes.pop(collection_name, None)
