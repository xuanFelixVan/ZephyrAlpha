# [BLUEPRINT] MOD-KNW-008 | docs/03_modules/_domain_knowledge/rag_pipeline/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-008 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_rag_pipeline
# [TESTS] src/zephyr/knowledge/rag_pipeline.py
"""MOD-KNW-008 单元测试：rag_pipeline RAG 问答管道。

蓝图验收（B13-04034/CAND-KNW-009，A3）：
重叠滑窗分块（确定性 chunk_id）+ hybrid 双路检索注入（RRF 融合 k=60）+
重排注入（非候选排列 Fail-Closed）+ 本地 LLM 生成注入（未注入 Fail-Closed）+
引用溯源（chunk_id 回链源文档，答案携引用列表）+ 统一 ingest。
检索器/重排器/生成器/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.knowledge.rag_pipeline",
    reason="rag_pipeline not importable",
)

from zephyr.knowledge.rag_pipeline import (  # noqa: E402
    RagPipeline,
    RagPipelineError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_TEXT_A = "动量因子在A股市场的实证研究表明，中期动量显著而短期反转明显。" * 4
_TEXT_B = "均值回复策略在震荡市中表现稳健，但需警惕趋势行情中的连续亏损。" * 4


def _pipeline(
    vector=None,
    keyword=None,
    reranker=None,
    generator=None,
    chunk_size: int = 40,
    chunk_overlap: int = 10,
) -> RagPipeline:
    return RagPipeline(
        clock=lambda: _T0,
        vector_searcher=vector,
        keyword_searcher=keyword,
        reranker=reranker,
        generator=generator if generator is not None else (lambda q, chunks: "答案文本"),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def _ingest_two(pipe: RagPipeline) -> None:
    pipe.ingest("doc-a", "动量研究", _TEXT_A)
    pipe.ingest("doc-b", "均值回复", _TEXT_B)


# ──────────────────────────────────────────────────────────────────────────────
# ingest（重叠滑窗分块）
# ──────────────────────────────────────────────────────────────────────────────


class TestIngest:
    def test_ingest_overlap_window(self) -> None:
        pipe = _pipeline()
        chunks = pipe.ingest("doc-a", "动量研究", "x" * 100)
        # window=40 overlap=10 → step=30：起点 0/30/60（60 起窗已覆盖全文，不产冗余尾块）
        assert [c.start for c in chunks] == [0, 30, 60]
        assert chunks[0].end == 40
        assert chunks[-1].end == 100
        assert [c.chunk_id for c in chunks] == [
            "doc-a#C0000",
            "doc-a#C0001",
            "doc-a#C0002",
        ]
        assert all(c.doc_id == "doc-a" for c in chunks)

    def test_ingest_overlap_content_shared(self) -> None:
        pipe = _pipeline()
        chunks = pipe.ingest("doc-a", "动量研究", "0123456789" * 10)
        # 相邻块重叠区内容一致（overlap=10）
        assert chunks[0].text[-10:] == chunks[1].text[:10]

    def test_ingest_short_text_single_chunk(self) -> None:
        pipe = _pipeline()
        chunks = pipe.ingest("doc-a", "动量研究", "短文")
        assert len(chunks) == 1
        assert chunks[0].text == "短文"
        assert (chunks[0].start, chunks[0].end) == (0, 2)

    def test_ingest_empty_fields_raises(self) -> None:
        pipe = _pipeline()
        with pytest.raises(RagPipelineError):
            pipe.ingest("", "t", "x")
        with pytest.raises(RagPipelineError):
            pipe.ingest("d", "", "x")
        with pytest.raises(RagPipelineError):
            pipe.ingest("d", "t", "")

    def test_ingest_duplicate_raises(self) -> None:
        pipe = _pipeline()
        pipe.ingest("doc-a", "动量研究", "x" * 10)
        with pytest.raises(RagPipelineError):
            pipe.ingest("doc-a", "动量研究", "y" * 10)

    def test_invalid_window_params_raises(self) -> None:
        with pytest.raises(RagPipelineError):
            _pipeline(chunk_size=0)
        with pytest.raises(RagPipelineError):
            _pipeline(chunk_size=40, chunk_overlap=40)  # overlap 须 < window
        with pytest.raises(RagPipelineError):
            _pipeline(chunk_size=40, chunk_overlap=-1)

    def test_chunks_of_and_get_chunk(self) -> None:
        pipe = _pipeline()
        _ingest_two(pipe)
        doc_a_chunks = pipe.chunks_of("doc-a")
        assert [c.chunk_index for c in doc_a_chunks] == list(range(len(doc_a_chunks)))
        assert pipe.get_chunk("doc-a#C0000") is doc_a_chunks[0]
        with pytest.raises(RagPipelineError):
            pipe.chunks_of("ghost")
        with pytest.raises(RagPipelineError):
            pipe.get_chunk("ghost#C0000")


# ──────────────────────────────────────────────────────────────────────────────
# 问答（hybrid RRF + 重排 + 生成 + 引用溯源）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def _ready(self, **kwargs) -> RagPipeline:
        pipe = _pipeline(
            vector=kwargs.get("vector", (lambda q, n: ["doc-a#C0000", "doc-b#C0000"])),
            keyword=kwargs.get("keyword", (lambda q, n: ["doc-b#C0000", "doc-a#C0000"])),
            reranker=kwargs.get("reranker"),
            generator=kwargs.get("generator"),
        )
        _ingest_two(pipe)
        return pipe

    def test_query_ok_with_citations(self) -> None:
        pipe = self._ready()
        answer = pipe.query("动量因子表现如何？", top_k=2)
        assert answer.answer == "答案文本"
        assert len(answer.citations) == 2
        for citation in answer.citations:
            assert citation.doc_id in ("doc-a", "doc-b")
            assert citation.doc_title in ("动量研究", "均值回复")
            assert citation.chunk_id.startswith(citation.doc_id)  # chunk 回链源文档

    def test_query_rrf_fusion_order(self) -> None:
        # vector: a0>b0；keyword: b0>a0 → RRF 同分，并列按 chunk_id 字典序
        pipe = self._ready()
        answer = pipe.query("q", top_k=2)
        assert [c.chunk_id for c in answer.citations] == ["doc-a#C0000", "doc-b#C0000"]

    def test_query_rrf_double_hit_wins(self) -> None:
        pipe = self._ready(
            vector=lambda q, n: ["doc-b#C0001", "doc-a#C0000"],
            keyword=lambda q, n: ["doc-b#C0001", "doc-b#C0000"],
        )
        answer = pipe.query("q", top_k=1)
        assert answer.citations[0].chunk_id == "doc-b#C0001"  # 双路命中者居首

    def test_query_searchers_missing_fail_closed(self) -> None:
        pipe = _pipeline()  # 双路均未注入
        _ingest_two(pipe)
        with pytest.raises(RagPipelineError):
            pipe.query("q")
        pipe2 = _pipeline(vector=lambda q, n: [])  # 仅单路
        _ingest_two(pipe2)
        with pytest.raises(RagPipelineError):
            pipe2.query("q")

    def test_query_generator_missing_fail_closed(self) -> None:
        pipe = RagPipeline(
            clock=lambda: _T0,
            vector_searcher=lambda q, n: [],
            keyword_searcher=lambda q, n: [],
            generator=None,
        )
        _ingest_two(pipe)
        with pytest.raises(RagPipelineError):
            pipe.query("q")

    def test_query_empty_question_or_bad_topk_raises(self) -> None:
        pipe = self._ready()
        with pytest.raises(RagPipelineError):
            pipe.query("")
        with pytest.raises(RagPipelineError):
            pipe.query("   ")
        with pytest.raises(RagPipelineError):
            pipe.query("q", top_k=0)

    def test_query_unknown_chunk_reference_raises(self) -> None:
        pipe = self._ready(vector=lambda q, n: ["ghost#C0000"])
        with pytest.raises(RagPipelineError):
            pipe.query("q")

    def test_query_reranker_applied(self) -> None:
        seen: list[str] = []

        def _rerank(question, chunks):
            seen.extend(c.chunk_id for c in chunks)
            return [c.chunk_id for c in reversed(chunks)]  # 逆序重排

        pipe = self._ready(reranker=_rerank)
        answer = pipe.query("q", top_k=2)
        assert [c.chunk_id for c in answer.citations] == list(reversed(seen))

    def test_query_reranker_non_permutation_raises(self) -> None:
        pipe = self._ready(reranker=lambda q, chunks: [chunks[0].chunk_id])  # 丢 chunk
        with pytest.raises(RagPipelineError):
            pipe.query("q")

    def test_query_generator_bad_output_raises(self) -> None:
        pipe = self._ready(generator=lambda q, chunks: "")
        with pytest.raises(RagPipelineError):
            pipe.query("q")
        pipe2 = self._ready(generator=lambda q, chunks: None)
        with pytest.raises(RagPipelineError):
            pipe2.query("q")

    def test_query_generator_receives_selected_chunks(self) -> None:
        received: list[str] = []

        def _gen(question, chunks):
            received.extend(c.chunk_id for c in chunks)
            return "ok"

        pipe = self._ready(generator=_gen)
        answer = pipe.query("q", top_k=1)
        assert [c.chunk_id for c in answer.citations] == received

    def test_query_searcher_exception_raises(self) -> None:
        def _boom(q, n):
            raise RuntimeError("索引损坏")

        pipe = self._ready(vector=_boom)
        with pytest.raises(RagPipelineError):
            pipe.query("q")

    def test_determinism_same_input_same_output(self) -> None:
        def _build() -> tuple:
            pipe = self._ready()
            a1 = pipe.query("q", top_k=2)
            a2 = pipe.query("q", top_k=2)
            return (a1, a2)

        first, second = _build()
        assert first == second
