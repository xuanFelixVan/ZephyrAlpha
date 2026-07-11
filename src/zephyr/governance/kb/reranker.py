# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.governance.kb.reranker
# [DOMAIN] D_GOV_KB
# [DEPENDENCIES] zephyr.governance.kb.__init__
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
# [A_module] module_id=MOD-DAT_reranker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Cross-Encoder 重排序层 — BGE-reranker-v2-m3（T-MOD-KB-001-RERANKER）
====================================================================
蓝图：§5.9 路由级重排序 + §9.4 Reranker截流
模块版本：v0.1.0 (beta reranker core)

功能
----
1. BGE-reranker-v2-m3 Cross-Encoder 模型加载（惰性）
2. rerank(query, documents) -> [(text, score)] 精排结果
3. 排序后截流截断
4. 模型不可用时 fallback 降级为无重排直通
5. score_threshold 阈值过滤

True Source : IRN-022（Reranker字段与三件套对齐）
               blueprint.md §5.9（重排序机制）
               T-V2-011（search_with_rerank 规格）
"""

from __future__ import annotations

from typing import Final
import logging
import threading
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_RERANK_MODEL",
    "RerankedHit",
    "Reranker",
    "rerank_batch",
]


DEFAULT_RERANK_MODEL: Final[str] = "BAAI/bge-reranker-v2-m3"
DEFAULT_TOP_K: Final[int] = 5
DEFAULT_SCORE_THRESHOLD: Final[float] = 0.0


@dataclass
class RerankedHit:
    text: str
    score: float
    index: int = -1
    metadata: dict[str, Any] = field(default_factory=dict)


class Reranker:
    def __init__(
        self,
        model_name: str = DEFAULT_RERANK_MODEL,
        top_k: int = DEFAULT_TOP_K,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    ) -> None:
        self._model_name = model_name
        self._top_k = max(1, top_k)
        self._score_threshold = score_threshold
        self._model: Any = None
        self._load_attempted = False
        self._lock = threading.RLock()

    @property
    def available(self) -> bool:
        self._ensure_model()
        return self._model is not None

    def rerank(
        self,
        query: str,
        documents: Sequence[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> list[RerankedHit]:
        if not documents:
            return []
        if not query or not query.strip():
            return _fallback_rerank(documents, metadatas, self._top_k, self._score_threshold)

        self._ensure_model()
        if self._model is None:
            return _fallback_rerank(documents, metadatas, self._top_k, self._score_threshold)

        try:
            pairs = [[query, doc] for doc in documents]
            scores = self._model.compute_score(pairs)
            if isinstance(scores, (int, float)):
                scores = [float(scores)]
            scores = [float(s) for s in scores]
        except Exception as exc:
            _log.warning("Reranker compute_score failed: %s, falling back", exc, exc_info=True)
            return _fallback_rerank(documents, metadatas, self._top_k, self._score_threshold)

        hits: list[RerankedHit] = []
        metas = metadatas or [{}] * len(documents)
        for i, (doc, score, meta) in enumerate(zip(documents, scores, metas, strict=False)):
            if score < self._score_threshold:
                continue
            hits.append(RerankedHit(text=doc, score=round(score, 4), index=i, metadata=dict(meta)))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[: self._top_k]

    def _ensure_model(self) -> None:
        if self._load_attempted:
            return
        with self._lock:
            if self._load_attempted:
                return
            self._load_attempted = True
            try:
                from sentence_transformers import CrossEncoder  # type: ignore[import-not-found]

                self._model = CrossEncoder(self._model_name, trust_remote_code=True)
                _log.info("Reranker loaded: %s", self._model_name)
            except Exception as exc:
                _log.warning("Reranker model load failed (%s): %s, rerank disabled", self._model_name, exc, exc_info=True)
                self._model = None


def _fallback_rerank(
    documents: Sequence[str],
    metadatas: list[dict[str, Any]] | None,
    top_k: int,
    threshold: float,
) -> list[RerankedHit]:
    metas = metadatas or [{}] * len(documents)
    hits = []
    for i, (doc, meta) in enumerate(zip(documents, metas, strict=False)):
        if threshold > 1.0:
            continue
        hits.append(RerankedHit(text=doc, score=1.0, index=i, metadata=dict(meta)))
    return hits[:top_k]


def rerank_batch(
    query: str,
    documents: Sequence[str],
    *,
    model_name: str = DEFAULT_RERANK_MODEL,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    metadatas: list[dict[str, Any]] | None = None,
) -> list[RerankedHit]:
    rk = Reranker(model_name=model_name, top_k=top_k, score_threshold=score_threshold)
    return rk.rerank(query, documents, metadatas=metadatas)
