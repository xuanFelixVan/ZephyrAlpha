# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.bm25_index
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.vector_memory.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_bm25_index | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""BM25Index — MOD-INF-011 稀疏检索组件
============================================
蓝图 §3.2 · BM25 稀疏检索索引

从 hybrid_retriever.py 拆分而来，职责单一化。
"""

from __future__ import annotations

import math
import re
from typing import Any


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
        tokens = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z0-9_]+", text.lower())
        return [t for t in tokens if len(t) > 0]


__all__: list[str] = ["BM25Index"]
