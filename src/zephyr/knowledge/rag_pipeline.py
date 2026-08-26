# [BLUEPRINT] MOD-KNW-008 | docs/03_modules/_domain_knowledge/rag_pipeline/blueprint.md
# [MODULE] zephyr.knowledge.rag_pipeline
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（纯内存分块与融合；vector_searcher/keyword_searcher/reranker/generator/clock 全注入）
# [CONSUMERS] 运行时装配批（文档统一 ingest / 向量+关键词双路检索器绑定 / 本地 LLM 生成器绑定 / 问答路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 分块=重叠滑窗（overlap<window 强制，chunk_id 确定性 doc_id#Cnnnn）; 双路检索器与生成器未注入 Fail-Closed 不旁路; RRF 融合 k=60 恒定，并列按 chunk_id 字典序; 重排仅可重排候选不得引入新 chunk; 答案必携引用列表（chunk_id 回链源文档）; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/rag_pipeline/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RagPipelineError(占位 ZA-KNW-UNREGISTERED-RAG-PIPELINE)——空字段/重复文档/非法滑窗参数/检索器或生成器未注入/未知chunk引用/重排非排列/生成非文本/top_k越界时抛
# [TESTS] tests/knowledge/test_rag_pipeline.py
# [A_module] module_id=MOD-KNW-008 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""RagPipeline — RAG 问答管道（MOD-KNW-008）。

B13-04034（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-009，A3）：RAG 问答管道
——文档**分块**（重叠滑窗，确定性 chunk_id）→ **hybrid 双路检索**（向量+关键词
检索器全注入，**RRF 融合 k=60**）→ **重排**（注入 reranker，仅重排候选不得引入
新 chunk）→ 本地 **LLM 生成**（注入生成器，未注入 Fail-Closed）+ **引用溯源**
（chunk_id 回链源文档，引用列表随答案输出）+ 统一 **ingest** 入口。

查重分工（蓝图 §0）：integration/vector_memory/cross_collection_retriever=跨
集合检索实现（本件仅注入其检索语义为双路之一，不实现向量存储）；kb_engine=通
用 CRUD 门面（本件 ingest 产物为内存 chunk 表，可选外挂）；layered_memory_
orchestrator=五层记忆编排（本件=单管道路由，零交集）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "Answer",
    "Chunk",
    "Citation",
    "Document",
    "RagPipeline",
    "RagPipelineError",
]

#: RRF 融合常数（k=60 恒定）
_RRF_K: Final[int] = 60


class RagPipelineError(Exception):
    """RAG 管道输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-RAG-PIPELINE。
    """


@dataclass(frozen=True)
class Document:
    """源文档（frozen）。"""

    doc_id: str
    title: str
    text: str
    ingested_at: datetime.datetime


@dataclass(frozen=True)
class Chunk:
    """文档分块（frozen）：chunk_id 回链源文档。"""

    chunk_id: str
    doc_id: str
    chunk_index: int
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class Citation:
    """引用溯源（frozen）：chunk → 源文档回链。"""

    chunk_id: str
    doc_id: str
    doc_title: str
    chunk_index: int


@dataclass(frozen=True)
class Answer:
    """RAG 答案（frozen）：必携引用列表。"""

    question: str
    answer: str
    citations: tuple[Citation, ...]


class RagPipeline:
    """RAG 问答管道（分块→hybrid RRF 检索→重排→生成→引用溯源）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        vector_searcher: Callable[[str, int], Sequence[str]] | None = None,
        keyword_searcher: Callable[[str, int], Sequence[str]] | None = None,
        reranker: Callable[[str, tuple[Chunk, ...]], Sequence[str]] | None = None,
        generator: Callable[[str, tuple[Chunk, ...]], str] | None = None,
        chunk_size: int = 200,
        chunk_overlap: int = 50,
        candidate_pool: int = 10,
    ) -> None:
        if chunk_size <= 0:
            raise RagPipelineError(f"chunk_size 须为正: {chunk_size!r}")
        if not 0 <= chunk_overlap < chunk_size:
            raise RagPipelineError(f"chunk_overlap 须满足 0<=overlap<chunk_size: {chunk_overlap!r}")
        if candidate_pool <= 0:
            raise RagPipelineError(f"candidate_pool 须为正: {candidate_pool!r}")
        self._clock = clock or datetime.datetime.now
        self._vector_searcher = vector_searcher
        self._keyword_searcher = keyword_searcher
        self._reranker = reranker
        self._generator = generator
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._candidate_pool = candidate_pool
        self._documents: dict[str, Document] = {}
        self._chunks: dict[str, Chunk] = {}
        self._doc_chunks: dict[str, list[str]] = {}

    # ── 统一 ingest ───────────────────────────────────────────────────────

    def ingest(self, doc_id: str, title: str, text: str) -> tuple[Chunk, ...]:
        """统一 ingest：重叠滑窗分块入库；空字段/重复文档 → Fail-Closed。"""
        if not doc_id:
            raise RagPipelineError("doc_id 为空")
        if not title:
            raise RagPipelineError(f"title 为空: {doc_id!r}")
        if not text:
            raise RagPipelineError(f"text 为空: {doc_id!r}")
        if doc_id in self._documents:
            raise RagPipelineError(f"文档重复 ingest: {doc_id!r}")
        document = Document(doc_id=doc_id, title=title, text=text, ingested_at=self._clock())
        self._documents[doc_id] = document
        step = self._chunk_size - self._chunk_overlap
        chunk_ids: list[str] = []
        index = 0
        for start in range(0, len(text), step):
            end = min(start + self._chunk_size, len(text))
            chunk_id = f"{doc_id}#C{index:04d}"
            chunk = Chunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                chunk_index=index,
                text=text[start:end],
                start=start,
                end=end,
            )
            self._chunks[chunk_id] = chunk
            chunk_ids.append(chunk_id)
            index += 1
            if end >= len(text):
                break
        self._doc_chunks[doc_id] = chunk_ids
        return tuple(self._chunks[cid] for cid in chunk_ids)

    # ── 查询构件 ──────────────────────────────────────────────────────────

    def get_chunk(self, chunk_id: str) -> Chunk:
        """单 chunk 查询（未知 → Fail-Closed）。"""
        chunk = self._chunks.get(chunk_id)
        if chunk is None:
            raise RagPipelineError(f"未知 chunk: {chunk_id!r}")
        return chunk

    def chunks_of(self, doc_id: str) -> tuple[Chunk, ...]:
        """单文档 chunk 列表（chunk_index 升序，确定性）。"""
        if doc_id not in self._documents:
            raise RagPipelineError(f"未知文档: {doc_id!r}")
        return tuple(self._chunks[cid] for cid in self._doc_chunks[doc_id])

    # ── RRF 融合 ──────────────────────────────────────────────────────────

    def _rrf_fuse(self, rankings: list[Sequence[str]]) -> list[str]:
        """RRF 融合（k=60）：score=Σ1/(k+rank)，并列按 chunk_id 字典序。"""
        scores: dict[str, float] = {}
        for ranking in rankings:
            for rank, chunk_id in enumerate(ranking, start=1):
                scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (_RRF_K + rank)
        return sorted(scores, key=lambda cid: (-scores[cid], cid))

    def _require_known(self, chunk_ids: Sequence[str], *, source: str) -> None:
        for chunk_id in chunk_ids:
            if chunk_id not in self._chunks:
                raise RagPipelineError(f"{source} 返回未知 chunk 引用: {chunk_id!r}")

    # ── 问答 ─────────────────────────────────────────────────────────────

    def query(self, question: str, *, top_k: int = 3) -> Answer:
        """问答：双路检索→RRF→重排→生成→引用溯源。

        检索器/生成器未注入、回调返回未知 chunk、重排非候选排列、生成非文本
        → Fail-Closed。
        """
        if not question or not question.strip():
            raise RagPipelineError("question 为空")
        if top_k <= 0:
            raise RagPipelineError(f"top_k 须为正: {top_k!r}")
        if self._vector_searcher is None or self._keyword_searcher is None:
            raise RagPipelineError("双路检索器未注入（hybrid 检索强制注入，禁止旁路）")
        if self._generator is None:
            raise RagPipelineError("generator 未注入（本地 LLM 生成强制注入，禁止旁路）")

        try:
            vector_hits = list(self._vector_searcher(question, self._candidate_pool))
            keyword_hits = list(self._keyword_searcher(question, self._candidate_pool))
        except RagPipelineError:
            raise
        except Exception as exc:  # noqa: BLE001 — 检索回调异常统一 Fail-Closed
            raise RagPipelineError(f"检索器异常: {exc}") from exc
        self._require_known(vector_hits, source="vector_searcher")
        self._require_known(keyword_hits, source="keyword_searcher")

        fused = self._rrf_fuse([vector_hits, keyword_hits])
        candidates = fused[: self._candidate_pool]
        if self._reranker is not None:
            candidate_chunks = tuple(self._chunks[cid] for cid in candidates)
            try:
                reranked = list(self._reranker(question, candidate_chunks))
            except RagPipelineError:
                raise
            except Exception as exc:  # noqa: BLE001
                raise RagPipelineError(f"reranker 异常: {exc}") from exc
            if sorted(reranked) != sorted(candidates):
                raise RagPipelineError("reranker 输出非候选排列（不得增删 chunk）")
            ordered = reranked
        else:
            ordered = candidates
        selected = [self._chunks[cid] for cid in ordered[:top_k]]

        try:
            answer_text = self._generator(question, tuple(selected))
        except RagPipelineError:
            raise
        except Exception as exc:  # noqa: BLE001 — 生成回调异常统一 Fail-Closed
            raise RagPipelineError(f"generator 异常: {exc}") from exc
        if not isinstance(answer_text, str) or not answer_text:
            raise RagPipelineError("generator 输出非文本（Fail-Closed）")

        citations = tuple(
            Citation(
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                doc_title=self._documents[chunk.doc_id].title,
                chunk_index=chunk.chunk_index,
            )
            for chunk in selected
        )
        return Answer(question=question, answer=answer_text, citations=citations)
