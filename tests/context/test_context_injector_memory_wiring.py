# [A_test] module_id: MOD-CONTEXT_ENGINE_injector_wiring | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §4 Phase 1 P1-1
# [MODULE] tests.context.test_context_injector_memory_wiring
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""ContextInjector 数据源接线测试（07 号文 §4 Phase 1 P1-1）。

验证 inject_by_keyword() 经 VMSSearchProtocol 协议注入接 UnifiedMemoryAPI
后返回非空 InjectedContext（含 sources + provenances），及降级/预算纪律。
检索客户端一律 fake/内存后端——不触网、不依赖 VMS 实体。
"""

from __future__ import annotations

from typing import Any

from zephyr.autonomy_core.context.context_injector import (
    ContextInjector,
    RetrievalMode,
    _UnifiedMemorySearchAdapter,
)


class _FakeSearchClient:
    """VMSSearchProtocol 假实现——返回预设 dict 命中。"""

    def __init__(self, hits: list[dict[str, Any]] | None = None, *, raises: bool = False) -> None:
        self._hits = hits or []
        self._raises = raises
        self.calls: list[tuple[str, str, int]] = []

    def search(self, collection: str, query: str, top_k: int) -> list[dict[str, Any]]:
        self.calls.append((collection, query, top_k))
        if self._raises:
            raise RuntimeError("backend down")
        return list(self._hits)


def _hit(content: str, *, topic: str = "ke_entries", chunk_id: str = "c-1", source: str = "") -> dict[str, Any]:
    metadata: dict[str, Any] = {"topic": topic, "chunk_id": chunk_id}
    if source:
        metadata["source"] = source
    return {"content": content, "score": 0.9, "metadata": metadata}


class TestInjectByKeywordWired:
    def test_returns_non_empty_context_with_sources_and_provenances(self) -> None:
        client = _FakeSearchClient(
            [
                _hit("规则一：禁止删除文件", chunk_id="c-1", source="rules/no-delete.md"),
                _hit("规则二：提交必须原子", chunk_id="c-2", source="rules/atomic.md"),
            ]
        )
        injector = ContextInjector(search_client=client)
        result = injector.inject_by_keyword("提交纪律")

        assert result.context != ""
        assert "规则一" in result.context
        assert result.retrieval_mode == RetrievalMode.KEYWORD.value
        assert result.query == "提交纪律"
        assert result.sources, "sources 不得为空"
        assert "rules/no-delete.md" in result.sources
        assert result.provenances, "provenances 不得为空"
        assert any(p.startswith("unified_memory:ke_entries:") for p in result.provenances)
        assert result.token_count > 0
        assert result.budget_remaining <= 8000

    def test_search_called_with_collection_and_top_k(self) -> None:
        client = _FakeSearchClient([_hit("x")])
        injector = ContextInjector(search_client=client, max_sources=3, search_collection="vibe_rules")
        injector.inject_by_keyword("q")
        assert client.calls == [("vibe_rules", "q", 3)]

    def test_token_budget_trims_entries(self) -> None:
        big = "很长的内容 " * 400  # 远超 100 token
        client = _FakeSearchClient([_hit(big, chunk_id="c-1"), _hit("短内容", chunk_id="c-2")])
        injector = ContextInjector(search_client=client, token_budget=50)
        result = injector.inject_by_keyword("q")
        # 第一条已超预算 → 被跳过，结果为空或仅含能进预算的条目
        assert result.token_count <= 50
        assert result.budget_remaining >= 0

    def test_max_sources_limits_entries(self) -> None:
        client = _FakeSearchClient([_hit(f"条目{i}", chunk_id=f"c-{i}") for i in range(10)])
        injector = ContextInjector(search_client=client, max_sources=2)
        result = injector.inject_by_keyword("q")
        assert result.context.count("条目") <= 2

    def test_blank_keyword_returns_empty_without_search(self) -> None:
        client = _FakeSearchClient([_hit("x")])
        injector = ContextInjector(search_client=client)
        result = injector.inject_by_keyword("   ")
        assert result.context == ""
        assert client.calls == []

    def test_client_exception_degrades_to_empty(self) -> None:
        injector = ContextInjector(search_client=_FakeSearchClient(raises=True))
        result = injector.inject_by_keyword("q")
        assert result.context == ""
        assert result.retrieval_mode == "keyword"

    def test_empty_hits_degrade_to_empty(self) -> None:
        injector = ContextInjector(search_client=_FakeSearchClient([]))
        result = injector.inject_by_keyword("q")
        assert result.context == ""
        assert result.sources == []
        assert result.provenances == []

    def test_inject_dispatch_uses_wired_keyword_path(self) -> None:
        client = _FakeSearchClient([_hit("命中内容", chunk_id="c-9")])
        injector = ContextInjector(search_client=client)
        result = injector.inject("纪律", mode=RetrievalMode.KEYWORD)
        assert result.context != ""
        assert result.retrieval_mode == "keyword"

    def test_task_and_module_modes_stay_empty(self) -> None:
        client = _FakeSearchClient([_hit("不应被检索", chunk_id="c-1")])
        injector = ContextInjector(search_client=client)
        assert injector.inject_by_task_id("T-1-1").context == ""
        assert injector.inject_by_module_id("MOD-X").context == ""
        assert client.calls == []


class TestUnifiedMemoryAdapterIntegration:
    """经 _UnifiedMemorySearchAdapter 接真实 UnifiedMemoryAPI（内存后端，CBAC 关）。"""

    def _make_api(self) -> Any:
        from zephyr.intelligence.model_evaluation._memory_backend import InMemoryMemoryBackend
        from zephyr.intelligence.model_evaluation.unified_memory_api import (
            UnifiedMemoryAPI,
            build_provenance,
        )

        api = UnifiedMemoryAPI(backend=InMemoryMemoryBackend(), enforce_capability=False)
        prov = build_provenance(origin="test:ce_wiring", audit_chain=["T-P1-1"])
        api.write(topic="ke_entries", content="CE 注入纪律：注入前必须过 LSG 扫描", provenance=prov)
        api.write(topic="ke_entries", content="CE 预算纪律：注入不得超 token 预算", provenance=prov)
        return api

    def test_adapter_search_returns_dict_hits(self) -> None:
        adapter = _UnifiedMemorySearchAdapter(self._make_api())
        hits = adapter.search("ke_entries", "LSG 扫描", top_k=5)
        assert isinstance(hits, list)
        assert all(isinstance(h, dict) for h in hits)
        assert all("content" in h and "metadata" in h for h in hits)

    def test_inject_by_keyword_non_empty_via_unified_memory(self) -> None:
        adapter = _UnifiedMemorySearchAdapter(self._make_api())
        injector = ContextInjector(search_client=adapter)
        result = injector.inject_by_keyword("LSG")
        assert result.context != ""
        assert result.sources
        assert result.provenances
        assert all(p.startswith("unified_memory:ke_entries:") for p in result.provenances)

    def test_no_match_returns_empty(self) -> None:
        adapter = _UnifiedMemorySearchAdapter(self._make_api())
        injector = ContextInjector(search_client=adapter)
        result = injector.inject_by_keyword("zzzz_no_such_token_zzzz")
        assert result.context == ""


class TestDefaultClientDegradation:
    def test_default_client_build_failure_degrades_to_empty(self, monkeypatch: Any) -> None:
        import zephyr.autonomy_core.context.context_injector as ci

        monkeypatch.setattr(ci, "_build_default_search_client", lambda: None)
        injector = ContextInjector()
        result = injector.inject_by_keyword("anything")
        assert result.context == ""
        assert result.retrieval_mode == "keyword"
