# [BLUEPRINT] MOD-KNW-009 | docs/03_modules/_domain_knowledge/layered_memory_orchestrator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-009 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_layered_memory_orchestrator
# [TESTS] src/zephyr/knowledge/layered_memory_orchestrator.py
"""MOD-KNW-009 单元测试：layered_memory_orchestrator 五层记忆编排器。

蓝图验收（B13-04342/CAND-KNW-011，A3 D-AUTONOMY-05）：
FAISS/FTS5/GRAPH/GIT/RAG 五层适配器全注入（缺层标记 degraded 不重建）+
统一检索编排（分层扇出 + 按 doc_id 合并去重 + 层故障降级不阻断）+
层健康检查 + 结果确定性排序。层适配器全内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.knowledge.layered_memory_orchestrator",
    reason="layered_memory_orchestrator not importable",
)

from zephyr.knowledge.layered_memory_orchestrator import (  # noqa: E402
    LayeredMemoryError,
    LayeredMemoryOrchestrator,
    LayerHit,
    MemoryLayer,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _hit(doc_id: str, layer: MemoryLayer, score: float, snippet: str = "") -> LayerHit:
    return LayerHit(doc_id=doc_id, layer=layer, score=score, snippet=snippet or f"s-{doc_id}")


def _orch(adapters: dict | None = None) -> LayeredMemoryOrchestrator:
    return LayeredMemoryOrchestrator(adapters=adapters, clock=lambda: _T0)


# ──────────────────────────────────────────────────────────────────────────────
# 层注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterLayer:
    def test_register_via_constructor(self) -> None:
        orch = _orch({MemoryLayer.FAISS: lambda q, n: []})
        assert orch.registered_layers() == (MemoryLayer.FAISS,)

    def test_register_layer_ok(self) -> None:
        orch = _orch()
        orch.register_layer(MemoryLayer.GRAPH, lambda q, n: [])
        assert orch.registered_layers() == (MemoryLayer.GRAPH,)

    def test_registered_layers_definition_order(self) -> None:
        orch = _orch()
        orch.register_layer(MemoryLayer.RAG, lambda q, n: [])
        orch.register_layer(MemoryLayer.FAISS, lambda q, n: [])
        orch.register_layer(MemoryLayer.GIT, lambda q, n: [])
        assert orch.registered_layers() == (MemoryLayer.FAISS, MemoryLayer.GIT, MemoryLayer.RAG)

    def test_duplicate_register_raises(self) -> None:
        orch = _orch({MemoryLayer.FAISS: lambda q, n: []})
        with pytest.raises(LayeredMemoryError):
            orch.register_layer(MemoryLayer.FAISS, lambda q, n: [])

    def test_invalid_layer_raises(self) -> None:
        orch = _orch()
        with pytest.raises(LayeredMemoryError):
            orch.register_layer("redis", lambda q, n: [])  # type: ignore[arg-type]

    def test_non_callable_adapter_raises(self) -> None:
        orch = _orch()
        with pytest.raises(LayeredMemoryError):
            orch.register_layer(MemoryLayer.GIT, "not-callable")  # type: ignore[arg-type]

    def test_unregister_ok(self) -> None:
        orch = _orch({MemoryLayer.FTS5: lambda q, n: []})
        orch.unregister_layer(MemoryLayer.FTS5)
        assert orch.registered_layers() == ()

    def test_unregister_unregistered_raises(self) -> None:
        orch = _orch()
        with pytest.raises(LayeredMemoryError):
            orch.unregister_layer(MemoryLayer.GRAPH)


# ──────────────────────────────────────────────────────────────────────────────
# 统一检索编排（扇出 + 合并去重 + 降级）
# ──────────────────────────────────────────────────────────────────────────────


class TestSearch:
    def test_search_merges_by_doc_id_max_score(self) -> None:
        orch = _orch({
            MemoryLayer.FAISS: lambda q, n: [_hit("d1", MemoryLayer.FAISS, 0.8, "faiss-d1")],
            MemoryLayer.FTS5: lambda q, n: [_hit("d1", MemoryLayer.FTS5, 0.9, "fts5-d1")],
        })
        result = orch.search("动量因子")
        assert len(result.hits) == 1
        merged = result.hits[0]
        assert merged.doc_id == "d1"
        assert merged.score == 0.9  # 取最高分
        assert merged.snippet == "fts5-d1"
        assert merged.layers == (MemoryLayer.FAISS, MemoryLayer.FTS5)  # 层定义序

    def test_search_missing_layers_marked_degraded(self) -> None:
        orch = _orch({MemoryLayer.FAISS: lambda q, n: [_hit("d1", MemoryLayer.FAISS, 1.0)]})
        result = orch.search("x")
        assert result.degraded_layers == (
            MemoryLayer.FTS5, MemoryLayer.GRAPH, MemoryLayer.GIT, MemoryLayer.RAG,
        )

    def test_search_layer_failure_degrades_not_blocks(self) -> None:
        def _boom(q: str, n: int) -> list[LayerHit]:
            raise RuntimeError("faiss 索引损坏")

        orch = _orch({
            MemoryLayer.FAISS: _boom,
            MemoryLayer.GRAPH: lambda q, n: [_hit("g1", MemoryLayer.GRAPH, 0.7)],
        })
        result = orch.search("供应链")
        assert [h.doc_id for h in result.hits] == ["g1"]  # 不阻断
        assert result.degraded_layers == (MemoryLayer.FAISS,) + tuple(
            la for la in (MemoryLayer.FTS5, MemoryLayer.GIT, MemoryLayer.RAG)
        )

    def test_search_deterministic_sort(self) -> None:
        orch = _orch({
            MemoryLayer.FAISS: lambda q, n: [
                _hit("d2", MemoryLayer.FAISS, 0.5),
                _hit("d1", MemoryLayer.FAISS, 0.5),  # 同分按 doc_id
                _hit("d3", MemoryLayer.FAISS, 0.9),
            ],
        })
        result = orch.search("x")
        assert [h.doc_id for h in result.hits] == ["d3", "d1", "d2"]

    def test_search_limit_truncates(self) -> None:
        orch = _orch({
            MemoryLayer.FTS5: lambda q, n: [_hit(f"d{i}", MemoryLayer.FTS5, float(i)) for i in range(5)],
        })
        result = orch.search("x", limit=2)
        assert [h.doc_id for h in result.hits] == ["d4", "d3"]

    def test_search_layers_subset(self) -> None:
        seen: list[str] = []

        def _mk(name: str):
            return lambda q, n: seen.append(name) or []

        orch = _orch({MemoryLayer.FAISS: _mk("faiss"), MemoryLayer.GIT: _mk("git")})
        result = orch.search("x", layers=[MemoryLayer.GIT])
        assert seen == ["git"]
        assert result.degraded_layers == ()

    def test_search_empty_query_raises(self) -> None:
        orch = _orch()
        with pytest.raises(LayeredMemoryError):
            orch.search("   ")

    def test_search_invalid_limit_raises(self) -> None:
        orch = _orch()
        with pytest.raises(LayeredMemoryError):
            orch.search("x", limit=0)

    def test_search_empty_layers_raises(self) -> None:
        orch = _orch()
        with pytest.raises(LayeredMemoryError):
            orch.search("x", layers=[])

    def test_search_invalid_layer_in_layers_raises(self) -> None:
        orch = _orch()
        with pytest.raises(LayeredMemoryError):
            orch.search("x", layers=["s3"])  # type: ignore[list-item]

    def test_search_invalid_hit_type_raises(self) -> None:
        orch = _orch({MemoryLayer.RAG: lambda q, n: [("d1", 0.9)]})  # 非 LayerHit
        with pytest.raises(LayeredMemoryError):
            orch.search("x")

    def test_search_empty_doc_id_raises(self) -> None:
        orch = _orch({MemoryLayer.RAG: lambda q, n: [_hit("", MemoryLayer.RAG, 0.9)]})
        with pytest.raises(LayeredMemoryError):
            orch.search("x")

    def test_search_determinism_same_input_same_output(self) -> None:
        adapters = {
            MemoryLayer.FAISS: lambda q, n: [_hit("a", MemoryLayer.FAISS, 0.3), _hit("b", MemoryLayer.FAISS, 0.6)],
            MemoryLayer.RAG: lambda q, n: [_hit("b", MemoryLayer.RAG, 0.7)],
        }
        r1 = _orch(adapters).search("x")
        r2 = _orch(adapters).search("x")
        assert r1 == r2


# ──────────────────────────────────────────────────────────────────────────────
# 健康检查
# ──────────────────────────────────────────────────────────────────────────────


class TestHealthCheck:
    def test_all_missing_degraded(self) -> None:
        health = _orch().health_check()
        assert len(health) == 5
        assert all((not h.registered) and h.degraded for h in health)
        assert [h.layer for h in health] == list(MemoryLayer)  # 定义序

    def test_registered_layer_healthy(self) -> None:
        orch = _orch({MemoryLayer.GRAPH: lambda q, n: []})
        health = {h.layer: h for h in orch.health_check()}
        assert health[MemoryLayer.GRAPH].registered
        assert not health[MemoryLayer.GRAPH].degraded
        assert health[MemoryLayer.GRAPH].failure_count == 0
        assert health[MemoryLayer.GRAPH].last_error is None

    def test_failed_layer_marked_degraded_with_error(self) -> None:
        def _boom(q: str, n: int) -> list[LayerHit]:
            raise ValueError("超时")

        orch = _orch({MemoryLayer.FAISS: _boom})
        orch.search("x", layers=[MemoryLayer.FAISS])
        orch.search("y", layers=[MemoryLayer.FAISS])
        health = {h.layer: h for h in orch.health_check()}
        faiss = health[MemoryLayer.FAISS]
        assert faiss.registered
        assert faiss.degraded
        assert faiss.failure_count == 2
        assert faiss.last_error is not None and "超时" in faiss.last_error
