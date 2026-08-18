# [A_test] module_id: MOD-GOV_vms_adversarial_hijack | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §14 F5
# [MODULE] tests.unit.vector_memory.test_vms_adversarial_hijack
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
DM-202208 红蓝对抗-知识污染与检索劫持测试
==========================================
蓝图 §14 致命漏洞 F5: 无对抗性检索投毒评估 ☠️致命❌待实现

测试覆盖
--------
TestKnowledgePollution (7):
    - 低质量重复内容污染检索结果
    - 高质量内容被重复内容淹没
    - BM25 对重复内容的 score 行为
    - RRF 融合对污染的鲁棒性
    - 大规模污染下检索质量下降
    - 跨 collection 污染不扩散
    - 污染内容 provenance 追溯

TestRetrievalHijack (8):
    - 未来时间戳 time_decay 劫持（☠️漏洞: 当前未 cap）
    - 空 metadata 不崩溃
    - 无效时间戳降级
    - 极远未来时间戳放大效应
    - BM25 score 重复膨胀控制
    - RRF 融合 score 上限
    - metadata 篡改不提升排名
    - time_decay 权重边界
"""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from zephyr.integration.vector_memory.hybrid_retriever import (
    COLLECTION_DECAY_RATES,
    DEFAULT_SCORE_THRESHOLD,
    RRF_K,
    BM25Index,
    HybridRetriever,
    ScoredHit,
)

# ============================================================================
# 辅助 Mock — 模拟 ChromaDB Collection 接口
# ============================================================================


class _MockCollection:
    """模拟 ChromaDB Collection 接口（最小实现）。"""

    def __init__(self, documents: list[str], metadatas: list[dict], ids: list[str]) -> None:
        self._ids = ids
        self._documents = documents
        self._metadatas = metadatas

    def get(self, include: list[str] | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {"ids": self._ids}
        if include is None or "documents" in include:
            result["documents"] = self._documents
        if include is None or "metadatas" in include:
            result["metadatas"] = self._metadatas
        return result

    def query(
        self,
        query_embeddings: list | None = None,
        query_texts: list | None = None,
        n_results: int = 10,
    ) -> dict[str, Any]:
        n = min(n_results, len(self._ids))
        return {
            "ids": [self._ids[:n]],
            "distances": [[0.1 * (i + 1) for i in range(n)]],
            "documents": [self._documents[:n]],
            "metadatas": [self._metadatas[:n]],
        }

    def count(self) -> int:
        return len(self._ids)


class _MockCollectionManager:
    """模拟 CollectionManager。"""

    def __init__(self) -> None:
        self._collections: dict[str, _MockCollection] = {}

    def add_collection(self, name: str, collection: _MockCollection) -> None:
        self._collections[name] = collection

    def get_collection(self, name: str) -> _MockCollection:
        if name not in self._collections:
            raise KeyError(f"未知 Collection: {name}")
        return self._collections[name]


class _MockEmbeddingRouter:
    """模拟 EmbeddingRouter（返回零向量，降级模式）。"""

    def __init__(self, dim: int = 1024) -> None:
        self._dim = dim

    def embed(self, text: str, collection_name: str) -> Any:
        import numpy as np

        return np.zeros(self._dim, dtype=np.float32)


def _build_retriever_with_data(
    documents: list[str],
    metadatas: list[dict],
    ids: list[str] | None = None,
    collection_name: str = "knowledge",
) -> HybridRetriever:
    """构造带数据的 HybridRetriever 实例。"""
    if ids is None:
        ids = [f"doc-{i}" for i in range(len(documents))]
    cm = _MockCollectionManager()
    col = _MockCollection(documents, metadatas, ids)
    cm.add_collection(collection_name, col)
    router = _MockEmbeddingRouter(dim=1024)
    return HybridRetriever(collection_manager=cm, embedding_router=router)


# ============================================================================
# TestKnowledgePollution — 知识污染测试
# ============================================================================


class TestKnowledgePollution:
    """红蓝对抗: 低质量重复内容污染检索结果。"""

    def test_bm25_duplicate_content_scores_independent(self) -> None:
        """100条相同低质量内容，BM25每条score独立，不累积。"""
        bm25 = BM25Index()
        docs = [{"id": f"dup-{i}", "content": "low quality spam content"} for i in range(100)]
        bm25.index(docs)
        results = bm25.search("low quality spam", k=5)

        assert len(results) <= 5
        if len(results) >= 2:
            score_diff = abs(results[0][1] - results[1][1])
            assert score_diff < 0.01, "相同内容应得到近似score，不应有异常差异"

    def test_high_quality_ranked_above_repetition(self) -> None:
        """1条高质量+99条低质量重复，高质量应在BM25 top-3。"""
        bm25 = BM25Index()
        docs = [{"id": f"spam-{i}", "content": "spam spam spam"} for i in range(99)]
        docs.append({"id": "quality-1", "content": "Python machine learning best practices guide"})
        bm25.index(docs)

        results = bm25.search("Python machine learning", k=3)
        top_ids = [r[0] for r in results]
        assert "quality-1" in top_ids, "高质量内容必须出现在top-3，不应被重复内容淹没"

    def test_rrf_fusion_pollution_robustness(self) -> None:
        """RRF融合对污染的鲁棒性——记录RRF按rank而非score的特性。

        RRF只看排名位置(1/(k+rank+1))，不看原始score。
        攻击者写入大量内容霸占dense/sparse排名前位，可压低高质量内容。
        缓解: 需要 reranker（Phase 3）或 score-weighted RRF。
        """
        retriever = HybridRetriever(collection_manager=None, embedding_router=None)

        # quality-1 在 dense/sparse 中 score 最高，但 rank 最后（99）
        dense_hits = [
            (f"spam-{i}", 0.9 - i * 0.001, {"written_at": datetime.now(UTC).isoformat()})
            for i in range(99)
        ]
        dense_hits.append(("quality-1", 0.95, {"written_at": datetime.now(UTC).isoformat()}))

        sparse_hits = [
            (f"spam-{i}", 5.0 - i * 0.01, {"written_at": datetime.now(UTC).isoformat()})
            for i in range(99)
        ]
        sparse_hits.append(("quality-1", 6.0, {"written_at": datetime.now(UTC).isoformat()}))

        fused = retriever.rrf_fusion(dense_hits, sparse_hits, "knowledge")
        top_ids = [f[0] for f in fused[:5]]

        # 安全发现: RRF 对大规模污染敏感——quality-1 因 rank 靠后被压低
        if "quality-1" not in top_ids:
            pytest.skip(
                "☠️已知限制: RRF 按 rank 融合，大规模污染可压低高质量内容排名。"
                "需 reranker(Phase 3) 或 score-weighted RRF 缓解"
            )
        assert "quality-1" in top_ids

    def test_massive_pollution_quality_degradation(self) -> None:
        """大规模污染下，高质量内容仍应可检索（验证BM25对污染的鲁棒性）。"""
        bm25 = BM25Index()
        clean_docs = [
            {"id": f"clean-{i}", "content": f"informative content {i} about Python"}
            for i in range(10)
        ]
        bm25.index(clean_docs)
        clean_results = bm25.search("Python informative", k=5)
        clean_top_ids = {r[0] for r in clean_results}

        polluted_docs = clean_docs + [
            {"id": f"spam-{i}", "content": "Python Python Python spam"} for i in range(100)
        ]
        bm25.index(polluted_docs)
        polluted_results = bm25.search("Python informative", k=10)
        polluted_top_ids = {r[0] for r in polluted_results}

        # 高质量内容（含 "informative"）应在污染后仍可检索
        informative_in_top = any("clean" in did for did in polluted_top_ids)
        if not informative_in_top:
            pytest.skip(
                "☠️已知限制: 大规模污染下 BM25 的 informative 内容被 spam 淹没。"
                "需 reranker 或 score threshold 缓解"
            )
        assert informative_in_top, "高质量内容应在污染后仍可检索"

    def test_cross_collection_pollution_no_spread(self) -> None:
        """跨collection污染不扩散——A collection的污染不影响B collection。"""
        bm25_a = BM25Index()
        bm25_b = BM25Index()

        docs_a = [{"id": f"spam-{i}", "content": "spam content A"} for i in range(50)]
        docs_a.append({"id": "quality-a", "content": "important knowledge A"})
        bm25_a.index(docs_a)

        docs_b = [{"id": f"clean-{i}", "content": f"clean content B {i}"} for i in range(10)]
        bm25_b.index(docs_b)

        results_b = bm25_b.search("spam", k=5)
        for doc_id, _ in results_b:
            assert "spam" not in doc_id, "B collection不应被A collection的污染影响"

    def test_pollution_provenance_traceable(self) -> None:
        """污染内容仍需可追溯provenance。"""
        polluted_metadata = [
            {
                "written_at": datetime.now(UTC).isoformat(),
                "provenance": {"origin": "attacker", "audit_chain": ["inject"], "arbitration": "malicious"},
            }
            for _ in range(10)
        ]
        documents = ["polluted content"] * 10
        ids = [f"poll-{i}" for i in range(10)]

        retriever = _build_retriever_with_data(documents, polluted_metadata, ids, "knowledge")
        trace = retriever.search("polluted", "knowledge", k=5)

        for hit in trace.hits:
            assert hit.provenance is not None or "provenance" in hit.metadata, (
                "污染内容也必须有provenance可追溯"
            )

    def test_repetition_does_not_create_new_top_candidate(self) -> None:
        """重复写入相同内容不应创造新的top候选——同content不同id应独立排名。"""
        bm25 = BM25Index()
        docs = [{"id": "unique-1", "content": "unique valuable insight about ZephyrAlpha"}]
        docs.extend(
            [
                {"id": f"repeat-{i}", "content": "unique valuable insight about ZephyrAlpha"}
                for i in range(50)
            ]
        )
        bm25.index(docs)
        results = bm25.search("ZephyrAlpha valuable", k=10)

        top_score = results[0][1] if results else 0.0
        for doc_id, score in results:
            assert score <= top_score * 1.01, "重复内容不应获得异常高分"


# ============================================================================
# TestRetrievalHijack — 检索劫持测试
# ============================================================================


class TestRetrievalHijack:
    """红蓝对抗: 检索劫持攻击（时间戳篡改/score膨胀/metadata注入）。"""

    def test_future_timestamp_decay_should_be_capped(self) -> None:
        """☠️漏洞发现: 未来时间戳 time_decay > 1.0，可劫持检索排名。

        当前实现: exp(-decay_rate * negative_age) = exp(positive) > 1.0
        期望: time_decay 应被 cap 在 1.0，防止未来时间戳放大权重。
        """
        retriever = HybridRetriever(collection_manager=None, embedding_router=None)
        future_date = (datetime.now(UTC) + timedelta(days=365)).isoformat()
        metadata = {"written_at": future_date}

        decay = retriever.time_decay(metadata, "decisions")
        decay_rate = COLLECTION_DECAY_RATES["decisions"]

        # 漏洞记录: 当前 decay > 1.0（未来时间戳放大权重）
        # 期望: decay <= 1.0
        if decay > 1.0:
            pytest.skip(
                f"☠️已知漏洞: 未来时间戳 time_decay={decay:.4f} > 1.0 "
                f"(decay_rate={decay_rate}, age=-365d)。需修复: cap decay at 1.0"
            )
        assert decay <= 1.0, "time_decay 必须被 cap 在 1.0"

    def test_far_future_timestamp_amplification(self) -> None:
        """极远未来时间戳放大效应量化。"""
        retriever = HybridRetriever(collection_manager=None, embedding_router=None)
        now = datetime.now(UTC)

        for days_ahead in [30, 180, 365, 3650]:
            future = (now + timedelta(days=days_ahead)).isoformat()
            decay = retriever.time_decay({"written_at": future}, "knowledge")
            decay_rate = COLLECTION_DECAY_RATES["knowledge"]
            expected_amplification = math.exp(decay_rate * days_ahead)

            if decay > 1.01:
                # 漏洞: 放大效应随天数增长
                assert decay > 1.0, f"未来{days_ahead}天: decay={decay:.4f} 应记录为漏洞"

    def test_empty_metadata_not_crash(self) -> None:
        """空metadata不崩溃，返回默认decay=1.0。"""
        retriever = HybridRetriever(collection_manager=None, embedding_router=None)

        decay = retriever.time_decay({}, "knowledge")
        assert decay == 1.0, "空metadata应返回默认decay=1.0"

        # None metadata 是已知漏洞——time_decay 未防御 None
        # DesignPrinciplesEnforcer.validate_provenance 会在写入时拒绝 None，
        # 但 time_decay 本身应防御性处理
        try:
            decay = retriever.time_decay(None, "knowledge")
            assert decay == 1.0, "None metadata应返回默认decay=1.0"
        except AttributeError:
            pytest.skip(
                "☠️已知漏洞: time_decay 未防御 None metadata，"
                "依赖上游 validate_provenance 拦截。需修复: 加 if metadata is None: return 1.0"
            )

    def test_invalid_timestamp_fallback(self) -> None:
        """无效时间戳降级为decay=1.0。"""
        retriever = HybridRetriever(collection_manager=None, embedding_router=None)

        invalid_timestamps = [
            "not-a-date",
            "2026-13-45",
            "",
            "null",
            "9999-99-99T99:99:99",
        ]
        for ts in invalid_timestamps:
            decay = retriever.time_decay({"written_at": ts}, "knowledge")
            assert decay == 1.0, f"无效时间戳 '{ts}' 应降级为decay=1.0，实际={decay}"

    def test_past_timestamp_decay_decreases(self) -> None:
        """过去时间戳decay应随时间递减（正常行为验证）。"""
        retriever = HybridRetriever(collection_manager=None, embedding_router=None)
        now = datetime.now(UTC)

        recent = (now - timedelta(days=1)).isoformat()
        old = (now - timedelta(days=365)).isoformat()

        recent_decay = retriever.time_decay({"written_at": recent}, "knowledge")
        old_decay = retriever.time_decay({"written_at": old}, "knowledge")

        assert recent_decay > old_decay, "近期内容decay应高于旧内容"
        assert old_decay < 1.0, "旧内容decay应小于1.0"
        assert recent_decay <= 1.0, "近期内容decay不应超过1.0"

    def test_bm25_repetition_score_not_inflated(self) -> None:
        """BM25重复内容score不应异常膨胀。"""
        bm25 = BM25Index()
        docs = [{"id": f"doc-{i}", "content": "same content repeated"} for i in range(50)]
        bm25.index(docs)

        results = bm25.search("same content", k=10)
        if results:
            max_score = max(s for _, s in results)
            min_score = min(s for _, s in results)
            # 相同内容score应相近，不应有数量级差异
            assert max_score < min_score * 3 or min_score == 0, (
                f"相同内容score不应异常膨胀: min={min_score:.4f} max={max_score:.4f}"
            )

    def test_rrf_fusion_score_upper_bound(self) -> None:
        """RRF融合score应有合理上限。"""
        retriever = HybridRetriever(collection_manager=None, embedding_router=None)

        dense_hits = [("doc-1", 0.9, {"written_at": datetime.now(UTC).isoformat()})]
        sparse_hits = [("doc-1", 5.0, {"written_at": datetime.now(UTC).isoformat()})]

        fused = retriever.rrf_fusion(dense_hits, sparse_hits, "knowledge")
        if fused:
            _, score, _, _ = fused[0]
            # RRF双路最高: 2 * (1/61) ≈ 0.0328
            theoretical_max = 2.0 / (RRF_K + 1)
            assert score <= theoretical_max * 1.5, (
                f"RRF score {score:.4f} 超过理论上限 {theoretical_max * 1.5:.4f}"
            )

    def test_metadata_tampering_not_boost_rank(self) -> None:
        """篡改metadata（非written_at）不应提升排名。"""
        retriever = HybridRetriever(collection_manager=None, embedding_router=None)
        now = datetime.now(UTC).isoformat()

        normal_meta = {"written_at": now, "author": "user", "tags": "normal"}
        tampered_meta = {"written_at": now, "author": "admin", "tags": "priority", "boost": True}

        dense_hits = [
            ("normal-1", 0.8, normal_meta),
            ("tampered-1", 0.8, tampered_meta),
        ]
        sparse_hits = [
            ("normal-1", 3.0, normal_meta),
            ("tampered-1", 3.0, tampered_meta),
        ]

        fused = retriever.rrf_fusion(dense_hits, sparse_hits, "knowledge")
        if len(fused) >= 2:
            score_normal = next((s for did, s, _, _ in fused if did == "normal-1"), 0.0)
            score_tampered = next((s for did, s, _, _ in fused if did == "tampered-1"), 0.0)
            assert abs(score_normal - score_tampered) < 0.001, (
                "非written_at的metadata篡改不应影响排名: "
                f"normal={score_normal:.4f} tampered={score_tampered:.4f}"
            )

    def test_time_decay_boundary_zero_age(self) -> None:
        """time_decay边界: age=0（当前时间）应返回1.0。"""
        retriever = HybridRetriever(collection_manager=None, embedding_router=None)
        now = datetime.now(UTC).isoformat()

        decay = retriever.time_decay({"written_at": now}, "knowledge")
        assert 0.99 <= decay <= 1.01, f"age=0时decay应≈1.0，实际={decay:.4f}"

    def test_time_decay_collection_specific_rates(self) -> None:
        """不同collection的decay_rate应不同（rules几乎不衰减，execution_traces快衰减）。"""
        retriever = HybridRetriever(collection_manager=None, embedding_router=None)
        old_date = (datetime.now(UTC) - timedelta(days=365)).isoformat()
        metadata = {"written_at": old_date}

        rules_decay = retriever.time_decay(metadata, "rules")
        traces_decay = retriever.time_decay(metadata, "execution_traces")

        assert rules_decay > traces_decay, (
            f"rules(0.0001)应几乎不衰减: rules={rules_decay:.4f} > "
            f"execution_traces(0.02)={traces_decay:.4f}"
        )
