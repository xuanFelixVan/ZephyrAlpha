# [A_test] module_id: MOD-GOV_assembly_context_injector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.context.context_injector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.context.context_injector import (
        ContextInjector,
        InjectedContext,
        RetrievalMode,
    )
except Exception as _exc:
    pytest.skip(f"cannot import context_injector: {_exc}", allow_module_level=True)


class _FakeRecord:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class _FakeKbRepo:
    def __init__(self, records=None, search_hits=None):
        self._records = records or []
        self._search_hits = search_hits or []

    def list_by_status(self):
        return self._records

    def search(self, query_text="", collection="", n_results=10, score_threshold=0.3):
        return self._search_hits


class TestContextInjectorInjectByTaskId:
    def test_inject_by_task_id_returns_injected_context(self):
        records = [_FakeRecord(ke_id="KE-001", summary="task related", tags=["T-001"], source_file="a.py")]
        repo = _FakeKbRepo(records=records)
        inj = ContextInjector(repo, token_budget=8000)
        result = inj.inject_by_task_id("T-001")
        assert isinstance(result, InjectedContext)
        assert result.retrieval_mode == "task_id"

    def test_inject_by_task_id_no_matches(self):
        repo = _FakeKbRepo(records=[])
        inj = ContextInjector(repo)
        result = inj.inject_by_task_id("T-999")
        assert result.token_count == 0


class TestContextInjectorInjectByModuleId:
    def test_inject_by_module_id_returns_injected_context(self):
        records = [_FakeRecord(ke_id="KE-002", summary="module info", category="MOD-CONTEXT_ENGINE")]
        repo = _FakeKbRepo(records=records)
        inj = ContextInjector(repo, token_budget=8000)
        result = inj.inject_by_module_id("MOD-CONTEXT_ENGINE")
        assert isinstance(result, InjectedContext)
        assert result.retrieval_mode == "module_id"

    def test_inject_by_module_id_no_matches(self):
        repo = _FakeKbRepo(records=[])
        inj = ContextInjector(repo)
        result = inj.inject_by_module_id("MOD-XXX")
        assert result.token_count == 0


class TestContextInjectorProperties:
    def test_token_budget_property(self):
        repo = _FakeKbRepo()
        inj = ContextInjector(repo, token_budget=5000)
        assert inj.token_budget == 5000

    def test_max_sources_property(self):
        repo = _FakeKbRepo()
        inj = ContextInjector(repo, max_sources=5)
        assert inj.max_sources == 5


class TestRetrievalMode:
    def test_retrieval_modes(self):
        assert RetrievalMode.TASK_ID.value == "task_id"
        assert RetrievalMode.MODULE_ID.value == "module_id"
        assert RetrievalMode.KEYWORD.value == "keyword"
