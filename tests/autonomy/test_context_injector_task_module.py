# [A_test] module_id: MOD-CONTEXT_ENGINE_injector_task_module | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | 07号文 §4-P1
# [MODULE] tests.autonomy.test_context_injector_task_module
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""ContextInjector inject_by_task_id / inject_by_module_id 检索接线测试（07 号文 §4 GP1 P1 补缺）。

验证两种模式经 VMSSearchProtocol 检索返回非空 InjectedContext（含 sources +
provenances），以及客户端缺省/异常/空 query 时的降级空纪律（不炸）。
检索客户端一律 fake——不触网、不依赖 VMS/UnifiedMemory 实体。
"""

from __future__ import annotations

from typing import Any

from zephyr.autonomy_core.context.context_injector import ContextInjector, RetrievalMode


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


class TestInjectByTaskId:
    def test_returns_non_empty_with_sources_and_provenances(self) -> None:
        client = _FakeSearchClient(
            [
                _hit("任务关联经验一", chunk_id="c-1", source="ke/task-a.md"),
                _hit("任务关联经验二", chunk_id="c-2", source="ke/task-b.md"),
            ]
        )
        injector = ContextInjector(search_client=client)
        result = injector.inject_by_task_id("T-2-12")

        assert result.context != ""
        assert "任务关联经验一" in result.context
        assert result.retrieval_mode == RetrievalMode.TASK_ID.value
        assert result.query == "T-2-12"
        assert "ke/task-a.md" in result.sources
        assert any(p.startswith("unified_memory:ke_entries:") for p in result.provenances)
        assert result.token_count > 0

    def test_query_is_task_id_verbatim(self) -> None:
        client = _FakeSearchClient([_hit("x")])
        injector = ContextInjector(search_client=client, max_sources=4)
        injector.inject_by_task_id("MOD-X-TASK-010")
        assert client.calls == [("ke_entries", "MOD-X-TASK-010", 4)]

    def test_client_exception_degrades_to_empty(self) -> None:
        injector = ContextInjector(search_client=_FakeSearchClient(raises=True))
        result = injector.inject_by_task_id("T-1-1")
        assert result.context == ""
        assert result.retrieval_mode == "task_id"
        assert result.sources == []

    def test_blank_task_id_returns_empty_without_search(self) -> None:
        client = _FakeSearchClient([_hit("x")])
        injector = ContextInjector(search_client=client)
        result = injector.inject_by_task_id("   ")
        assert result.context == ""
        assert client.calls == []

    def test_empty_hits_degrade_to_empty(self) -> None:
        injector = ContextInjector(search_client=_FakeSearchClient([]))
        result = injector.inject_by_task_id("T-1-1")
        assert result.context == ""
        assert result.provenances == []


class TestInjectByModuleId:
    def test_returns_non_empty_with_sources_and_provenances(self) -> None:
        client = _FakeSearchClient([_hit("模块归属知识", chunk_id="c-9", source="ke/mod.md")])
        injector = ContextInjector(search_client=client)
        result = injector.inject_by_module_id("MOD-CONTEXT_ENGINE")

        assert result.context != ""
        assert "模块归属知识" in result.context
        assert result.retrieval_mode == RetrievalMode.MODULE_ID.value
        assert result.query == "MOD-CONTEXT_ENGINE"
        assert "ke/mod.md" in result.sources
        assert result.provenances

    def test_query_is_module_id_verbatim(self) -> None:
        client = _FakeSearchClient([_hit("x")])
        injector = ContextInjector(search_client=client, search_collection="blueprints")
        injector.inject_by_module_id("MOD-INF-051")
        assert client.calls == [("blueprints", "MOD-INF-051", 10)]

    def test_client_exception_degrades_to_empty(self) -> None:
        injector = ContextInjector(search_client=_FakeSearchClient(raises=True))
        result = injector.inject_by_module_id("MOD-X")
        assert result.context == ""
        assert result.retrieval_mode == "module_id"

    def test_blank_module_id_returns_empty_without_search(self) -> None:
        client = _FakeSearchClient([_hit("x")])
        injector = ContextInjector(search_client=client)
        result = injector.inject_by_module_id("")
        assert result.context == ""
        assert client.calls == []


class TestNoClientDegradation:
    def test_missing_default_client_degrades_both_modes(self, monkeypatch: Any) -> None:
        import zephyr.autonomy_core.context.context_injector as ci

        monkeypatch.setattr(ci, "_build_default_search_client", lambda: None)
        injector = ContextInjector()
        assert injector.inject_by_task_id("T-1-1").context == ""
        assert injector.inject_by_module_id("MOD-X").context == ""


class TestInjectDispatch:
    def test_dispatch_task_and_module_modes(self) -> None:
        client = _FakeSearchClient([_hit("命中", chunk_id="c-1")])
        injector = ContextInjector(search_client=client)
        task_result = injector.inject("T-9-9", mode=RetrievalMode.TASK_ID)
        module_result = injector.inject("MOD-Y", mode=RetrievalMode.MODULE_ID)
        assert task_result.retrieval_mode == "task_id"
        assert task_result.context != ""
        assert module_result.retrieval_mode == "module_id"
        assert module_result.context != ""
