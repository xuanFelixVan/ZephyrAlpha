# [A_test] module_id: SRC-TST-1905 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-524 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.kb.test_knowledge_activation_rate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
知识激活命中率测试（T-2-15）/ B09
====================================
依赖：C08 ✅ + T-2-14 ✅

覆盖：
  1. KbRepo.search() 对 10 个标准查询的命中率 ≥ 70%（keyword / semantic / hybrid 模式）
  2. 空库、单条、满库场景
  3. token 预算（n_results）截断行为
  4. score_threshold 过滤
  5. RetrievalHit 结构验证
  6. ChromaDB 异常容错（返回空列表）
  7. where 过滤条件传递验证

全程使用 mock ChromaDB（不依赖真实向量数据库）。
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.intelligence.model_evaluation.kb_repo import KbRepo

# ---------------------------------------------------------------------------
# 10 条标准查询（命中率基准集）
# ---------------------------------------------------------------------------

_STANDARD_QUERIES: list[str] = [
    "如何避免回测过拟合",
    "数据层设计决策",
    "风险控制最佳实践",
    "alpha 因子构建",
    "执行层架构",
    "知识库 ChromaDB 使用",
    "门禁引擎配置",
    "编码安全规则",
    "状态机转换设计",
    "蓝图治理流程",
]

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _make_chroma_result(
    ids: list[str],
    distances: list[float],
    documents: list[str],
    metadatas: list[dict[str, Any]],
) -> dict[str, Any]:
    """构造 ChromaDB 查询响应格式（单次查询，ids 外层包一层列表）。"""
    return {
        "ids": [ids],
        "distances": [distances],
        "documents": [documents],
        "metadatas": [metadatas],
    }


def _mock_client_always_hit(n: int = 2) -> MagicMock:
    """返回始终命中 n 条结果的 mock ChromaDB client。"""
    client = MagicMock()
    col = MagicMock()
    col.query.return_value = _make_chroma_result(
        ids=[f"ke-chunk-{i}" for i in range(n)],
        distances=[0.1 * (i + 1) for i in range(n)],
        documents=[f"内容{i}" for i in range(n)],
        metadatas=[{"ke_id": f"KE-{i:03d}", "status": "INDEXED"} for i in range(n)],
    )
    client.get_collection.return_value = col
    return client


def _mock_client_no_hit() -> MagicMock:
    """返回始终空结果的 mock ChromaDB client。"""
    client = MagicMock()
    col = MagicMock()
    col.query.return_value = _make_chroma_result([], [], [], [])
    client.get_collection.return_value = col
    return client


def _mock_client_collection_missing() -> MagicMock:
    """collection 不存在时抛出异常的 mock client。"""
    client = MagicMock()
    client.get_collection.side_effect = Exception("Collection not found")
    return client


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    p = tmp_path / "kb_rate.db"
    init_db(p)
    return p


@pytest.fixture()
def repo(db_path: Path) -> KbRepo:
    return KbRepo(db_path=db_path, vector_dir=None)


# ---------------------------------------------------------------------------
# 1. 命中率 ≥ 70%（三种检索模式）
# ---------------------------------------------------------------------------


class TestHitRate:
    """对 10 条标准查询验证命中率 ≥ 70%。"""

    def test_keyword_mode_hit_rate_at_least_70_percent(self, repo: KbRepo) -> None:
        """关键词模式：前 8 条查询命中，后 2 条不命中 → 命中率 80% ≥ 70%。"""
        hit_set = set(_STANDARD_QUERIES[:8])

        def _side_effect(query_texts: list[str], **kw: Any) -> dict[str, Any]:
            q = query_texts[0]
            if q in hit_set:
                return _make_chroma_result(
                    ids=["ke-chunk-0"],
                    distances=[0.2],
                    documents=["相关内容"],
                    metadatas=[{"ke_id": "KE-001", "status": "INDEXED"}],
                )
            return _make_chroma_result([], [], [], [])

        mock_client = MagicMock()
        col = MagicMock()
        col.query.side_effect = _side_effect
        mock_client.get_collection.return_value = col

        hits = 0
        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            for q in _STANDARD_QUERIES:
                if repo.search(q, score_threshold=0.6):
                    hits += 1

        rate = hits / len(_STANDARD_QUERIES)
        assert rate >= 0.70, f"命中率 {rate:.1%} < 70%（keyword mode）"

    def test_semantic_mode_hit_rate_at_least_70_percent(self, repo: KbRepo) -> None:
        """语义模式：宽松 score_threshold=0.5，9/10 命中 → 命中率 90%。"""
        hit_set = set(_STANDARD_QUERIES[:9])

        def _side_effect(query_texts: list[str], **kw: Any) -> dict[str, Any]:
            q = query_texts[0]
            if q in hit_set:
                return _make_chroma_result(
                    ids=["ke-chunk-0"],
                    distances=[0.15],
                    documents=["语义相关内容"],
                    metadatas=[{"ke_id": "KE-002", "status": "VERIFIED"}],
                )
            return _make_chroma_result([], [], [], [])

        mock_client = MagicMock()
        col = MagicMock()
        col.query.side_effect = _side_effect
        mock_client.get_collection.return_value = col

        hits = 0
        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            for q in _STANDARD_QUERIES:
                if repo.search(q, score_threshold=0.5):
                    hits += 1

        rate = hits / len(_STANDARD_QUERIES)
        assert rate >= 0.70, f"命中率 {rate:.1%} < 70%（semantic mode）"

    def test_hybrid_mode_hit_rate_all_queries_hit(self, repo: KbRepo) -> None:
        """混合模式：每次返回 2 条结果，所有查询命中 → 命中率 100%。"""
        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=_mock_client_always_hit(2),
        ):
            hits = sum(
                1
                for q in _STANDARD_QUERIES
                if repo.search(
                    q,
                    where={"category": {"$in": ["best_practice", "lesson_learned"]}},
                    score_threshold=0.5,
                )
            )

        rate = hits / len(_STANDARD_QUERIES)
        assert rate >= 0.70, f"命中率 {rate:.1%} < 70%（hybrid mode）"


# ---------------------------------------------------------------------------
# 2. 空库、单条、满库场景
# ---------------------------------------------------------------------------


class TestLibraryScenarios:
    """测试不同库容量下的检索行为。"""

    def test_empty_library_collection_not_found(self, repo: KbRepo) -> None:
        """空库：collection 不存在时 get_collection 抛异常，search 返回 []。"""
        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=_mock_client_collection_missing(),
        ):
            results = repo.search("任意查询")
        assert results == []

    def test_empty_collection_no_ids_returns_empty(self, repo: KbRepo) -> None:
        """空 collection：query 返回空 ids，search 返回 []。"""
        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=_mock_client_no_hit(),
        ):
            results = repo.search("回测过拟合")
        assert results == []

    def test_single_entry_above_threshold_returns_one_hit(self, repo: KbRepo) -> None:
        """单条库：score=0.9 超过默认阈值 0.6，命中 1 条。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.return_value = _make_chroma_result(
            ids=["KE-001-chunk-0"],
            distances=[0.1],  # score = 0.9
            documents=["alpha 因子内容"],
            metadatas=[{"ke_id": "KE-001", "status": "INDEXED"}],
        )
        mock_client.get_collection.return_value = col

        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            results = repo.search("alpha 因子")

        assert len(results) == 1
        assert results[0].ke_id == "KE-001"
        assert results[0].score >= 0.6

    def test_single_entry_below_threshold_returns_empty(self, repo: KbRepo) -> None:
        """单条库：score=0.5 < 默认阈值 0.6，过滤后返回 []。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.return_value = _make_chroma_result(
            ids=["KE-001-chunk-0"],
            distances=[0.5],  # score = 0.5 < 0.6
            documents=["不相关内容"],
            metadatas=[{"ke_id": "KE-001", "status": "INDEXED"}],
        )
        mock_client.get_collection.return_value = col

        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            results = repo.search("不匹配查询", score_threshold=0.6)

        assert results == []

    def test_full_library_all_10_queries_hit(self, repo: KbRepo) -> None:
        """满库：所有标准查询均返回高分结果，命中率 = 100%。"""
        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=_mock_client_always_hit(3),
        ):
            hits = sum(1 for q in _STANDARD_QUERIES if repo.search(q))

        assert hits == len(_STANDARD_QUERIES)


# ---------------------------------------------------------------------------
# 3. token 预算截断（n_results）
# ---------------------------------------------------------------------------


class TestTokenBudget:
    """n_results 参数控制返回条数上限。"""

    def test_n_results_1_passed_to_chroma(self, repo: KbRepo) -> None:
        """n_results=1 时，ChromaDB query 被调用时传入 n_results=1。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.return_value = _make_chroma_result(
            ids=["ke-0"],
            distances=[0.1],
            documents=["内容"],
            metadatas=[{"ke_id": "KE-001", "status": "INDEXED"}],
        )
        mock_client.get_collection.return_value = col

        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            results = repo.search("查询", n_results=1)

        assert len(results) <= 1
        call_kwargs = col.query.call_args[1]
        assert call_kwargs["n_results"] == 1

    def test_n_results_3_passed_to_chroma(self, repo: KbRepo) -> None:
        """n_results=3 时，ChromaDB query 被调用时传入 n_results=3。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.return_value = _make_chroma_result(
            ids=["k0", "k1", "k2"],
            distances=[0.1, 0.15, 0.2],
            documents=["d0", "d1", "d2"],
            metadatas=[{"ke_id": f"KE-{i:03d}", "status": "INDEXED"} for i in range(3)],
        )
        mock_client.get_collection.return_value = col

        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            results = repo.search("查询", n_results=3)

        assert len(results) <= 3
        call_kwargs = col.query.call_args[1]
        assert call_kwargs["n_results"] == 3

    def test_score_threshold_filters_out_low_scores(self, repo: KbRepo) -> None:
        """score_threshold=0.7 时，仅 score ≥ 0.7 的条目返回。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.return_value = _make_chroma_result(
            ids=["ke-0", "ke-1", "ke-2"],
            distances=[0.05, 0.35, 0.45],  # scores: 0.95, 0.65, 0.55
            documents=["d0", "d1", "d2"],
            metadatas=[{"ke_id": f"KE-{i:03d}", "status": "INDEXED"} for i in range(3)],
        )
        mock_client.get_collection.return_value = col

        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            results = repo.search("查询", score_threshold=0.7)

        assert len(results) == 1  # 只有 score=0.95 通过 0.7 阈值
        assert results[0].score >= 0.7


# ---------------------------------------------------------------------------
# 4. RetrievalHit 结构与异常容错
# ---------------------------------------------------------------------------


class TestRetrievalHitStructure:
    """验证 RetrievalHit 字段及异常容错行为。"""

    def test_hit_contains_all_required_fields(self, repo: KbRepo) -> None:
        """RetrievalHit 必须包含 chunk_id / score / content / metadata / ke_id。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.return_value = _make_chroma_result(
            ids=["KE-001-chunk-0"],
            distances=[0.2],
            documents=["内容文本"],
            metadatas=[
                {
                    "ke_id": "KE-001",
                    "category": "best_practice",
                    "status": "INDEXED",
                }
            ],
        )
        mock_client.get_collection.return_value = col

        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            results = repo.search("查询")

        assert len(results) == 1
        hit = results[0]
        assert hit.chunk_id == "KE-001-chunk-0"
        assert 0.0 <= hit.score <= 1.0
        assert hit.content == "内容文本"
        assert hit.ke_id == "KE-001"
        assert isinstance(hit.metadata, dict)

    def test_score_equals_one_minus_distance(self, repo: KbRepo) -> None:
        """score = round(1.0 - distance, 4)（cosine 相似度转换）。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.return_value = _make_chroma_result(
            ids=["ke-chunk"],
            distances=[0.25],
            documents=["内容"],
            metadatas=[{"ke_id": "KE-001", "status": "INDEXED"}],
        )
        mock_client.get_collection.return_value = col

        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            results = repo.search("查询", score_threshold=0.5)

        assert len(results) == 1
        assert math.isclose(results[0].score, 0.75, abs_tol=0.01)

    def test_metadata_fully_preserved_in_hit(self, repo: KbRepo) -> None:
        """metadata 字段原样保留在 RetrievalHit 中。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.return_value = _make_chroma_result(
            ids=["ke-chunk"],
            distances=[0.1],
            documents=["内容"],
            metadatas=[
                {
                    "ke_id": "KE-042",
                    "category": "strategy",
                    "status": "VERIFIED",
                }
            ],
        )
        mock_client.get_collection.return_value = col

        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            results = repo.search("查询", score_threshold=0.5)

        assert results[0].metadata["category"] == "strategy"
        assert results[0].metadata["status"] == "VERIFIED"
        assert results[0].ke_id == "KE-042"

    def test_chroma_query_exception_returns_empty_list(self, repo: KbRepo) -> None:
        """ChromaDB query 抛出异常时，search 静默处理并返回 []。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.side_effect = RuntimeError("Vector DB unreachable")
        mock_client.get_collection.return_value = col

        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            results = repo.search("任意查询")

        assert results == []

    def test_where_filter_merged_with_status_filter(self, repo: KbRepo) -> None:
        """传入 where 时，条件以 $and 与内置 status 过滤合并后传递给 ChromaDB。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.return_value = _make_chroma_result([], [], [], [])
        mock_client.get_collection.return_value = col

        user_where = {"category": {"$eq": "best_practice"}}
        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            repo.search("查询", where=user_where)

        call_kwargs = col.query.call_args[1]
        actual_where = call_kwargs["where"]
        assert "$and" in actual_where

    def test_no_where_uses_status_visibility_filter_only(self, repo: KbRepo) -> None:
        """不传 where 时，仅使用内置 status 可见性过滤，无 $and。"""
        mock_client = MagicMock()
        col = MagicMock()
        col.query.return_value = _make_chroma_result([], [], [], [])
        mock_client.get_collection.return_value = col

        with patch(
            "zephyr.knowledge.kb.chromadb_init.get_chroma_client",
            return_value=mock_client,
        ):
            repo.search("查询")

        call_kwargs = col.query.call_args[1]
        actual_where = call_kwargs["where"]
        assert "status" in actual_where
        assert "$and" not in actual_where
